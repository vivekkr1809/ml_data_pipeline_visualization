# Bug Fix: Same Column Selection Error

## Bug Description

When users selected the same column for both X and Y axes in the correlation plot, the application crashed with the error:
```
Analysis Error: Failed to generate plot:
too many values to unpack (expected 4)
```

## Root Cause

The bug was caused by how pandas handles duplicate column selection. When you select the same column twice:

```python
data[['temperature', 'temperature']]
```

Pandas creates a DataFrame with **two columns both named 'temperature'**. Subsequently, when accessing:

```python
clean_data['temperature'].values
```

Pandas returns a **DataFrame** (containing both columns) instead of a **Series**, resulting in a 2D array instead of a 1D array. This caused downstream errors in scipy.stats.linregress and matplotlib, which expect 1D arrays.

## Affected Files

1. `src/analysis/correlation_analyzer.py`
   - Line 47: Creating clean_data with duplicate columns
   - Line 52-53: Accessing columns returned 2D arrays
   - Line 132: Same issue in validate_data method
   - Line 115: Validation incorrectly required 2 columns minimum

2. `src/visualization/renderers/correlation_renderer.py`
   - Line 54: Creating clean_data with duplicate columns
   - Line 55-56: Accessing columns returned 2D arrays
   - Line 186: Same issue in validate_data method
   - Line 169: Validation incorrectly required 2 columns minimum

## The Fix

Added special handling for when `column_x == column_y`:

### In `correlation_analyzer.py`:

```python
# Before (buggy):
clean_data = data[[column_x, column_y]].dropna()
x = clean_data[column_x].values
y = clean_data[column_y].values

# After (fixed):
if column_x == column_y:
    clean_data = data[[column_x]].dropna()
    x = clean_data[column_x].values
    y = clean_data[column_x].values
else:
    clean_data = data[[column_x, column_y]].dropna()
    x = clean_data[column_x].values
    y = clean_data[column_y].values
```

### In `validate_data` methods:

Updated column defaulting logic to handle single-column DataFrames:

```python
# Before:
if len(data.columns) < 2:
    return False
column_x = kwargs.get('column_x', data.columns[0])
column_y = kwargs.get('column_y', data.columns[1])

# After:
column_x = kwargs.get('column_x', data.columns[0] if len(data.columns) > 0 else None)
column_y = kwargs.get('column_y', data.columns[1] if len(data.columns) > 1 else data.columns[0] if len(data.columns) > 0 else None)
```

## Expected Behavior

When analyzing a column against itself:
- **Slope**: 1.0 (perfect 1:1 relationship)
- **R²**: 1.0 (perfect correlation)
- **RMSE**: 0.0 (no error)
- **Pearson r**: 1.0 (perfect positive correlation)

This is mathematically correct - any variable has perfect correlation with itself.

## Unit Tests Added

1. `tests/test_correlation_analyzer.py`:
   - `test_same_column_selection`: Tests single-column DataFrame
   - `test_same_column_with_multiple_columns`: Tests multi-column DataFrame with same column selected
   - `test_validation_same_column`: Tests validation logic

2. `tests/test_correlation_renderer.py`:
   - `test_render_same_column`: Tests rendering with single-column DataFrame
   - `test_render_same_column_multiple_columns`: Tests rendering with multi-column DataFrame
   - `test_validation_same_column`: Tests renderer validation

## Testing

To run the tests:
```bash
python -m unittest tests.test_correlation_analyzer.TestCorrelationAnalyzer.test_same_column_selection -v
python -m unittest tests.test_correlation_renderer.TestCorrelationRenderer.test_render_same_column -v
```

Or run all tests:
```bash
python -m unittest discover tests -v
```

## Related Code Review

This fix maintains backward compatibility and doesn't affect normal (different column) operations. The special case handling only activates when `column_x == column_y`, making it a safe, minimal fix.
