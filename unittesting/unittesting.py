import sys

# Add parent directory to path
sys.path.append('../algo_system')

import unittest
import pandas as pd
from get_instruments import get_instruments
from get_optimized_positions import get_optimized_positions
from get_risk_adjusted_positions import get_risk_adjusted_positions
from get_buffered_positions import get_buffered_positions
from get_notional_exposures import get_notional_exposures

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

class TestGetRiskAdjustedPositions(unittest.TestCase):
    def setUp(self):
        self.returns_df = pd.read_csv('unittesting/data/fictional_returns_TEST2.csv', index_col=0)

    def test_get_risk_adjusted_positions(self):
        positions = {'ES' : 1, 'ZF' : 1, 'ZN' : 2}
        notional_exposure_per_contract = {'ES' : 50000, 'ZF' : 100000, 'ZN' : 100000}
        capital = 500000
        risk_target = 0.20
        IDM = 2.50
        average_forecast = 10
        open_interest_dct = {'ES' : 100000, 'ZF' : 50000, 'ZN' : 50000}
        standard_deviation_dct = {'ES' : 0.01, 'ZF' : 0.005, 'ZN' : 0.005}
        instrument_weights_dct = {'ES' : 0.33, 'ZF' : 0.33, 'ZN' : 0.33}
        max_forecast = 20
        max_position_leverage_ratio = 2.0
        max_forecast_margin = 0.5
        max_pct_of_open_interest = 0.01
        instrument_returns_df = self.returns_df

        risk_adjusted_positions = get_risk_adjusted_positions(
            positions=positions,
            notional_exposure_per_contract=notional_exposure_per_contract,
            capital=capital,
            risk_target=risk_target,
            IDM=IDM,
            average_forecast=average_forecast,
            open_interest_dct=open_interest_dct,
            standard_deviation_dct=standard_deviation_dct,
            instrument_weights_dct=instrument_weights_dct,
            max_forecast=max_forecast,
            max_position_leverage_ratio=max_position_leverage_ratio,
            max_forecast_margin=max_forecast_margin,
            max_pct_of_open_interest=max_pct_of_open_interest,
            instrument_returns_df=instrument_returns_df,
            max_portfolio_leverage=20.0
        )

        expected_result = {'ES' : 1, 'ZF' : 1, 'ZN' : 2}
        self.assertEqual(risk_adjusted_positions, expected_result)

class TestGetBufferedPositions(unittest.TestCase):
    def test_get_buffered_positions(self):
        positions = {'ES' : 0.9, 'ZF' : 1, 'ZN' : 2}
        held_positions = {'ES' : 1, 'ZF' : 1, 'ZN' : 5}
        buffer_fraction = 0.01

        buffered_positions = get_buffered_positions(positions, held_positions, buffer_fraction)

        expected_result = {'ES' : 1, 'ZF' : 1, 'ZN' : 2}
        self.assertEqual(buffered_positions, expected_result)

class TestGetNotionalExposures(unittest.TestCase):
    def test_get_notional_exposures(self):
        prices = dict(ES=100, ZF=150, ZN=50)
        multipliers = dict(ES=50, ZF=1000, ZN=1000)

        notional_exposures = get_notional_exposures(prices, multipliers)

        expected_result = dict(ES=5000, ZF=150000, ZN=50000)

        self.assertEqual(notional_exposures, expected_result)

if __name__ == '__main__':
    unittest.main(failfast=True)
