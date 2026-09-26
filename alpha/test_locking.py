import tempfile
import unittest
from alpha.locking import exclusive_directory


class LockTests(unittest.TestCase):
    def test_second_writer_is_rejected_and_release_allows_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            with exclusive_directory(folder):
                with self.assertRaises(RuntimeError):
                    with exclusive_directory(folder):pass
            with exclusive_directory(folder):pass


if __name__=='__main__':unittest.main()
