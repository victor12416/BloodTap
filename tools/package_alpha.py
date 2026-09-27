"""Build a deterministic, source-only BloodTap alpha ZIP."""
import argparse
import hashlib
from pathlib import Path
import zipfile


ROOT=Path(__file__).resolve().parent.parent
RUNTIME_FILES=(
    'VERSION','README.md','Start-BloodTap.cmd','android.py',
    'alpha/__init__.py','alpha/game.py','alpha/locking.py','alpha/saves.py','alpha/server.py',
    'alpha/web/app.js','alpha/web/index.html','alpha/web/style.css',
    'simulator/__init__.py','simulator/economy_data.json','simulator/garden_data.json',
)


def package_files(root):
    files=[root/path for path in RUNTIME_FILES]
    files.extend(path for path in (root/'docs').rglob('*') if path.is_file())
    missing=[str(path.relative_to(root)) for path in files if not path.is_file()]
    if missing:raise FileNotFoundError('Missing package files: '+', '.join(missing))
    return sorted(set(files),key=lambda path:path.relative_to(root).as_posix())


def add_bytes(archive,name,data):
    info=zipfile.ZipInfo(name,date_time=(2020,1,1,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o100644<<16
    archive.writestr(info,data)


def build(output=None,root=ROOT):
    root=Path(root).resolve()
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    if not version or any(c not in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-' for c in version):
        raise ValueError('VERSION must be a non-empty filename-safe identifier')
    output=Path(output) if output else root/'dist'/f'BloodTap-{version}.zip'
    output.parent.mkdir(parents=True,exist_ok=True)
    prefix=f'BloodTap-{version}'
    manifest=[]
    with zipfile.ZipFile(output,'w') as archive:
        for source in package_files(root):
            relative=source.relative_to(root).as_posix()
            data=source.read_bytes()
            manifest.append(f'{hashlib.sha256(data).hexdigest()}  {relative}')
            add_bytes(archive,f'{prefix}/{relative}',data)
        add_bytes(archive,f'{prefix}/PACKAGE-MANIFEST.txt',('\n'.join(manifest)+'\n').encode('utf-8'))
    return output.resolve()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    print(build(args.output))


if __name__=='__main__':main()
