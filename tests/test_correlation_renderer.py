"""Unit tests for correlation renderer"""
import unittest
import pandas as pd
from src.visualization.renderers.correlation_renderer import CorrelationRenderer
from src.core.interfaces.renderer import RenderConfig
from src.analysis.correlation_analyzer import CorrelationAnalyzer


class TestCorrelationRenderer(unittest.TestCase):
    """Test cases for CorrelationRenderer"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = CorrelationRenderer()
        self.analyzer = CorrelationAnalyzer()

    def test_render_same_column(self):
        """Test rendering when x and y are the same column (regression test)"""
        # Create test data with single column
        data = pd.DataFrame({
            'temperature': [25.3, 26.1, 24.8, 27.5, 23.9],
        })

        # Create config
        config = RenderConfig(
            title="Test Plot",
            xlabel="Temperature",
            ylabel="Temperature"
        )

        # Analyze data
        analysis_result = self.analyzer.analyze(data, column_x='temperature', column_y='temperature')

        # This should not raise an error
        try:
            fig = self.renderer.render_with_metrics(
                data,
                config,
                analysis_result,
                column_x='temperature',
                column_y='temperature'
            )
            self.assertIsNotNone(fig)
        except Exception as e:
            self.fail(f"Render failed with same column: {e}")

    def test_render_same_column_multiple_columns(self):
        """Test rendering same column when DataFrame has multiple columns"""
        # Create test data with multiple columns
        data = pd.DataFrame({
            'temperature': [25.3, 26.1, 24.8, 27.5, 23.9],
            'pressure': [101.2, 101.5, 100.9, 102.1, 100.5],
            'humidity': [45.2, 47.8, 44.1, 51.3, 42.5]
        })

        config = RenderConfig(title="Test Plot")
        analysis_result = self.analyzer.analyze(data, column_x='pressure', column_y='pressure')

        # Should render successfully
        try:
            fig = self.renderer.render_with_metrics(
                data,
                config,
                analysis_result,
                column_x='pressure',
                column_y='pressure'
            )
            self.assertIsNotNone(fig)
        except Exception as e:
            self.fail(f"Render failed: {e}")

    def test_validation_same_column(self):
        """Test validation works with same column selection"""
        # Single column DataFrame
        single_col = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        self.assertTrue(self.renderer.validate_data(single_col, column_x='A', column_y='A'))

        # Multiple column DataFrame, same column selected
        multi_col = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        self.assertTrue(self.renderer.validate_data(multi_col, column_x='B', column_y='B'))

    def test_render_different_columns(self):
        """Test rendering with different columns (normal case)"""
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        })

        config = RenderConfig(title="Test Plot")
        analysis_result = self.analyzer.analyze(data, column_x='x', column_y='y')

        fig = self.renderer.render_with_metrics(
            data,
            config,
            analysis_result,
            column_x='x',
            column_y='y'
        )
        self.assertIsNotNone(fig)


if __name__ == '__main__':
    unittest.main()
