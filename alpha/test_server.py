import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from alpha.game import Game
from alpha.server import make_server


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.game=Game(Path(self.temp.name)/'save.json')
        self.server=make_server(self.game,0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.close)

    def close(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)

    def request(self,method,path,body=None,origin=True,host=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=f'http://127.0.0.1:{self.server.server_port}'
        if host:headers['Host']=host
        conn.request(method,path,json.dumps(body) if body is not None else None,headers)
        response=conn.getresponse();data=response.read();status=response.status;conn.close()
        return status,data

    def test_round_trip_and_unknown_routes(self):
        code,data=self.request('GET','/');self.assertEqual(code,200);self.assertIn(b'Gather echoes',data)
        code,data=self.request('POST','/api/action',{'action':'click'});self.assertEqual(code,200)
        self.assertEqual(json.loads(data)['bank'],1)
        code,data=self.request('GET','/api/export');self.assertEqual(code,200)
        self.assertEqual(json.loads(data)['state']['bank'],1)
        self.assertEqual(self.request('GET','/../simulator/economy_data.json')[0],404)

    def test_cross_origin_and_bad_actions_cannot_mutate_state(self):
        self.assertEqual(self.request('POST','/api/action',{'action':'click'},origin=False)[0],403)
        self.assertEqual(self.request('GET','/api/state',host='evil.example')[0],403)
        self.assertEqual(self.request('POST','/api/action',{'action':'buy','producer':-1})[0],400)
        self.assertEqual(self.request('POST','/api/action',{'action':'reset'})[0],400)
        self.assertEqual(self.request('POST','/api/action',{'action':'ascension','id':[]})[0],400)
        self.assertEqual(self.game.state.bank,0)


if __name__=='__main__':unittest.main()
