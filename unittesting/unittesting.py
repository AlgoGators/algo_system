import sys

# Add parent directory to path
sys.path.append('../algo_system')

import unittest
import pandas as pd
from get_instruments import get_instruments

class TestGetInstruments(unittest.TestCase):
    def setUp(self):
        self.fictional_returns = pd.read_csv('unittesting/data/fictional_returns.csv')

    def test_get_instruments(self):
        instruments = ['ES', 'ZF', 'ZN']
        instrument_weight = 1 / len(instruments)
        IDM = 1.48 # determined from number of instruments
        risk_target = 0.20
        instrument_returns_df = self.fictional_returns
        maximum_leverage = 2.0

        acceptable_instruments = get_instruments(instruments, instrument_weight, IDM, risk_target, instrument_returns_df, maximum_leverage)

        expected_result = ['ES', 'ZF']
        self.assertEqual(acceptable_instruments, expected_result)

if __name__ == '__main__':
    unittest.main(failfast=True)
