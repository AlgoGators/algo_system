import sys

# Add parent directory to path
sys.path.append('../algo_system')

import unittest
import pandas as pd
from get_instruments import get_instruments
from get_optimized_positions import get_optimized_positions

class TestGetInstruments(unittest.TestCase):
    def setUp(self):
        self.fictional_returns = pd.read_csv('unittesting/data/fictional_returns_TEST1.csv', index_col=0)

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

class TestGetOptimizedPositions(unittest.TestCase):
    def setUp(self):
        self.returns_df = pd.read_csv('unittesting/data/fictional_returns_TEST2.csv', index_col=0)
    
    def test_get_optimized_positions(self):
        held_positions = {'ES' : 1, 'ZF' : 3, 'ZN' : 2}
        ideal_positions = {'ES' : 0.94, 'ZF' : -0.1, 'ZN' : 0.2}
        notional_exposures_per_contract = {'ES' : 50000, 'ZF' : 100000, 'ZN' : 100000}
        capital = 500000
        costs_per_contract = {'ES' : 0.02, 'ZF' : 1.5, 'ZN' : 1.0}
        risk_target = 0.20

        optimized_positions = get_optimized_positions(held_positions, ideal_positions, notional_exposures_per_contract, capital, costs_per_contract, self.returns_df, risk_target)

        expected_result = {'ES' : 1, 'ZF' : 0, 'ZN' : 0}
        self.assertEqual(optimized_positions, expected_result)

if __name__ == '__main__':
    unittest.main(failfast=True)
