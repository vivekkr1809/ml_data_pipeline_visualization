"""Unit tests for correlation analyzer"""
import unittest
import pandas as pd
import numpy as np
from src.analysis.correlation_analyzer import CorrelationAnalyzer


class TestCorrelationAnalyzer(unittest.TestCase):
    """Test cases for CorrelationAnalyzer"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CorrelationAnalyzer()

    def test_basic_correlation(self):
        """Test basic correlation analysis"""
        # Create simple linear data
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        })

        result = self.analyzer.analyze(data, column_x='x', column_y='y')

        # Should have perfect correlation
        self.assertAlmostEqual(result.get_metric('r2'), 1.0, places=10)
        self.assertAlmostEqual(result.get_metric('slope'), 2.0, places=10)
        self.assertAlmostEqual(result.get_metric('rmse'), 0.0, places=10)

    def test_same_column_selection(self):
        """Test when x and y are the same column (regression test for bug)"""
        # Create test data with single column
        data = pd.DataFrame({
            'temperature': [25.3, 26.1, 24.8, 27.5, 23.9],
        })

        # This should work - analyzing a column against itself
        result = self.analyzer.analyze(data, column_x='temperature', column_y='temperature')

        # Should have perfect correlation
        self.assertAlmostEqual(result.get_metric('r2'), 1.0, places=10)
        self.assertAlmostEqual(result.get_metric('slope'), 1.0, places=10)
        self.assertAlmostEqual(result.get_metric('rmse'), 0.0, places=10)
        self.assertAlmostEqual(result.get_metric('pearson_r'), 1.0, places=10)

    def test_same_column_with_multiple_columns(self):
        """Test same column selection when DataFrame has multiple columns"""
        # Create test data with multiple columns
        data = pd.DataFrame({
            'temperature': [25.3, 26.1, 24.8, 27.5, 23.9],
            'pressure': [101.2, 101.5, 100.9, 102.1, 100.5],
            'humidity': [45.2, 47.8, 44.1, 51.3, 42.5]
        })

        # Select same column for both x and y
        result = self.analyzer.analyze(data, column_x='pressure', column_y='pressure')

        # Should have perfect correlation
        self.assertAlmostEqual(result.get_metric('r2'), 1.0, places=10)
        self.assertAlmostEqual(result.get_metric('slope'), 1.0, places=10)
        self.assertAlmostEqual(result.get_metric('rmse'), 0.0, places=10)

    def test_validation_same_column(self):
        """Test validation works with same column selection"""
        # Single column DataFrame
        single_col = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        self.assertTrue(self.analyzer.validate_data(single_col, column_x='A', column_y='A'))

        # Multiple column DataFrame, same column selected
        multi_col = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        self.assertTrue(self.analyzer.validate_data(multi_col, column_x='B', column_y='B'))

    def test_negative_correlation(self):
        """Test negative correlation"""
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [10, 8, 6, 4, 2]
        })

        result = self.analyzer.analyze(data, column_x='x', column_y='y')

        self.assertAlmostEqual(result.get_metric('r2'), 1.0, places=10)
        self.assertAlmostEqual(result.get_metric('slope'), -2.0, places=10)

    def test_validation(self):
        """Test data validation"""
        # Empty dataframe
        empty_data = pd.DataFrame()
        self.assertFalse(self.analyzer.validate_data(empty_data))

        # Non-numeric data
        non_numeric = pd.DataFrame({'x': ['a', 'b', 'c'], 'y': [1, 2, 3]})
        self.assertFalse(self.analyzer.validate_data(non_numeric, column_x='x', column_y='y'))

        # Valid data
        valid_data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        self.assertTrue(self.analyzer.validate_data(valid_data, column_x='x', column_y='y'))


if __name__ == '__main__':
    unittest.main()
