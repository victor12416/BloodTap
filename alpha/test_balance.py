import unittest
from alpha.balance import profile


class BalanceStudyTests(unittest.TestCase):
    def test_short_profile_is_deterministic_and_conserves(self):
        first=profile(7,'adaptive',seconds=60,cps=4)
        second=profile(7,'adaptive',seconds=60,cps=4)
        self.assertEqual(first,second)
        self.assertEqual(first['first_producer_seconds'],5)
        self.assertIsNone(first['first_two_fragment_bundle_seconds'])
        self.assertEqual(first['checkpoints'][-1]['seconds'],60)


if __name__=='__main__':unittest.main()
