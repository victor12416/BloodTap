import unittest
from contextlib import redirect_stdout
import io
from alpha.balance import profile


class BalanceStudyTests(unittest.TestCase):
    def test_short_profile_is_deterministic_and_conserves(self):
        first=profile(7,'adaptive',seconds=60,cps=4)
        second=profile(7,'adaptive',seconds=60,cps=4)
        self.assertEqual(first,second)
        self.assertEqual(first['first_producer_seconds'],5)
        self.assertIsNone(first['first_two_fragment_bundle_seconds'])
        self.assertEqual(first['checkpoints'][-1]['seconds'],60)

    def test_slow_sampled_seed_reaches_bundle_in_target_window(self):
        with redirect_stdout(io.StringIO()):
            result=profile(3,'adaptive',seconds=5400,cps=4,until_bundle=True)
        reached=result['first_two_fragment_bundle_seconds']
        self.assertIsNotNone(reached)
        self.assertGreaterEqual(reached,3600)
        self.assertLessEqual(reached,5400)


if __name__=='__main__':unittest.main()
