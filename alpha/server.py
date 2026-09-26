"""Local-only BloodTap server. Run: python -m alpha.server"""
import argparse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit
from alpha.game import Game
from alpha import saves
from alpha.locking import exclusive_directory

STATIC=Path(__file__).with_name('web')


def make_server(game,port=8765):
    lock=threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass

        def send(self,status,payload,content_type='application/json; charset=utf-8',download=False):
            data=payload if isinstance(payload,bytes) else json.dumps(payload,allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            if download:self.send_header('Content-Disposition','attachment; filename="bloodtap-save.json"')
            self.end_headers()
            try:self.wfile.write(data)
            except (BrokenPipeError,ConnectionResetError):pass

        def valid_host(self):
            allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            return self.headers.get('Host') in allowed

        def do_GET(self):
            if not self.valid_host():return self.send(403,{'error':'Use the local BloodTap address'})
            path=urlsplit(self.path).path
            try:
                if path in ('/api/state','/api/export'):
                    with lock:
                        game.advance()
                        if path=='/api/export':
                            return self.send(200,saves.encode(game.state,game.wall()).encode('utf-8'),download=True)
                        return self.send(200,game.snapshot())
                files={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),
                       '/style.css':('style.css','text/css; charset=utf-8')}
                if path not in files:return self.send(404,{'error':'Not found'})
                name,mime=files[path]
                self.send(200,(STATIC/name).read_bytes(),mime)
            except (ValueError,OSError,OverflowError) as exc:self.send(500,{'error':str(exc)})

        def do_POST(self):
            origin=self.headers.get('Origin')
            expected={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
            if not self.valid_host() or origin not in expected:return self.send(403,{'error':'Local same-origin requests only'})
            if urlsplit(self.path).path!='/api/action':return self.send(404,{'error':'Not found'})
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send(415,{'error':'JSON required'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=saves.MAX_BYTES*2:return self.send(413,{'error':'Request too large or empty'})
                body=json.loads(self.rfile.read(size))
                with lock:
                    game.advance();result=game.action(body)
                self.send(200,result)
            except (ValueError,UnicodeError,RecursionError,OverflowError) as exc:self.send(400,{'error':str(exc)})
            except OSError as exc:self.send(500,{'error':'Save failed: '+str(exc)})

    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.daemon_threads=True
    return server


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parent.parent/'alpha-data')
    args=parser.parse_args()
    with exclusive_directory(args.data_dir):
        game=Game(args.data_dir/'save.json')
        server=make_server(game,args.port)
        print(f'BloodTap: http://127.0.0.1:{server.server_port}',flush=True)
        print(f'Save: {game.path.resolve()}\nPress Ctrl+C to stop.',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:
            server.server_close();game.advance();game.save()


if __name__=='__main__':main()
