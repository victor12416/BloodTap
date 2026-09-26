import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
import zipfile

from tools.package_alpha import build


class AlphaPackageTests(unittest.TestCase):
    def test_package_is_reproducible_safe_and_runnable(self):
        with tempfile.TemporaryDirectory() as folder:
            temp=Path(folder)
            first=build(temp/'first.zip')
            second=build(temp/'second.zip')
            self.assertEqual(first.read_bytes(),second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                names=archive.namelist()
                self.assertTrue(any(name.endswith('/PACKAGE-MANIFEST.txt') for name in names))
                self.assertTrue(all(not name.startswith(('/', '\\')) and '..' not in Path(name).parts for name in names))
                archive.extractall(temp/'unpacked')
            root=next((temp/'unpacked').iterdir())
            result=subprocess.run([sys.executable,'-B','-m','alpha.server','--help'],cwd=root,
                                  capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('--data-dir',result.stdout)


if __name__=='__main__':unittest.main()
