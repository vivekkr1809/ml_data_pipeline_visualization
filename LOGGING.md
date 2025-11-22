# Logging and Debugging Guide

## Overview

The ML Data Pipeline Visualizer includes comprehensive logging to help diagnose issues and understand application behavior. All operations are logged with detailed context to make debugging easier.

## Log Files

### Location
- Logs are automatically created in the `logs/` directory
- Each run creates a new timestamped log file: `ml_visualizer_YYYYMMDD_HHMMSS.log`
- Example: `logs/ml_visualizer_20250122_143052.log`

### Log Levels

**Console Output (INFO and above):**
- Shows important operations and errors
- Minimal, user-friendly messages
- Appears in terminal/command prompt

**File Output (DEBUG and above):**
- Detailed operation logs
- Full stack traces for errors
- Platform and system information
- Data shapes, file sizes, timing
- Complete operation context

## What Gets Logged

### Application Lifecycle
```
[INFO] ML Data Pipeline Visualizer Starting
[INFO] Python version: 3.11.0
[INFO] Platform: win32
[INFO] Application version: 0.2.0
```

### Data Loading
```
[INFO] Loading CSV file: sample_contour_data.csv
[INFO] Successfully loaded CSV: shape=(50, 5), columns=['x_position', 'y_position', ...]
[DEBUG] Column types: {'x_position': dtype('float64'), ...}
[DEBUG] Memory usage: 2.34 KB
```

### Plot Generation
```
[INFO] Columns selected - X: x_position, Y: y_position, Z: temperature
[INFO] Generating contour plot in interactive mode
[INFO] Generating Plotly figure HTML
[DEBUG] Platform: win32, Default encoding: utf-8
[DEBUG] Generated HTML size: 3024.56 KB
[INFO] Successfully loaded Plotly figure
```

### Errors with Context
```
[ERROR] Unicode encoding error: 'charmap' codec can't encode character
[ERROR] Platform: win32, File encoding used: utf-8
[ERROR] Failed to generate plot: ...
[ERROR] Plot context - Type: contour, Mode: interactive
[ERROR] Data shape: (50, 5)
```

## Using Logs for Debugging

### When Something Goes Wrong

1. **Check the latest log file** in the `logs/` directory
2. **Look for ERROR or WARNING** messages
3. **Check the context** around the error (previous 10-20 lines)
4. **Note the stack trace** for detailed error information

### Example: Debugging a Plot Failure

```log
[2025-01-22 14:30:52] INFO     [ml_visualizer.gui.main_window._on_columns_selected:191] Columns selected - X: x_position, Y: y_position, Z: temperature
[2025-01-22 14:30:52] DEBUG    [ml_visualizer.gui.main_window._on_columns_selected:192] Plot type: contour, Mode: interactive
[2025-01-22 14:30:52] INFO     [ml_visualizer.gui.main_window._on_columns_selected:202] Generating contour plot in interactive mode
[2025-01-22 14:30:53] INFO     [ml_visualizer.gui.widgets.plotly_widget.set_figure:86] Generating Plotly figure HTML
[2025-01-22 14:30:53] DEBUG    [ml_visualizer.gui.widgets.plotly_widget.set_figure:87] Platform: win32, Default encoding: utf-8
[2025-01-22 14:30:55] DEBUG    [ml_visualizer.gui.widgets.plotly_widget.set_figure:108] Generated HTML size: 3024.56 KB
[2025-01-22 14:30:55] ERROR    [ml_visualizer.gui.widgets.plotly_widget.set_figure:135] Unicode encoding error: 'charmap' codec can't encode character '\u95f0'
```

This tells you:
- What was being attempted (contour plot in interactive mode)
- What column data was used
- Where the failure occurred (plotly_widget.py, line 135)
- The exact error (Unicode encoding issue)
- Platform details (Windows with utf-8 encoding)

### Sharing Logs for Support

When reporting issues:

1. **Locate the log file**: `logs/ml_visualizer_YYYYMMDD_HHMMSS.log`
2. **Include the entire log** if file is small (< 1MB)
3. **For large logs**, include:
   - First 50 lines (startup info)
   - Last 100 lines (recent operations)
   - All ERROR/WARNING lines

## Log Retention

- Log files are **not** automatically deleted
- You can safely delete old log files manually
- The `logs/` directory is ignored by git (won't be committed)

## Privacy and Sensitive Data

**What's logged:**
- File paths
- Column names
- Data shapes (rows × columns)
- Operation timings
- Error messages

**What's NOT logged:**
- Actual data values
- File contents
- Personal information

## Disabling File Logging

If you want console-only logging, modify `src/main.py`:

```python
# Change this line:
setup_logging(log_level=logging.INFO, log_to_file=True)

# To this:
setup_logging(log_level=logging.INFO, log_to_file=False)
```

## Advanced: Increasing Log Verbosity

For even more detailed logs, change the log level in `src/main.py`:

```python
# More verbose (shows DEBUG messages in console too):
setup_logging(log_level=logging.DEBUG, log_to_file=True)

# Less verbose (WARNING and above only):
setup_logging(log_level=logging.WARNING, log_to_file=True)
```

## Troubleshooting Common Issues

### "logs/ directory not found"
- Created automatically on first run
- Check file permissions in the project directory

### "Cannot write to log file"
- Check disk space
- Verify write permissions on project directory
- Log file location shown in console at startup

### "Log files very large"
- Normal for long sessions with many operations
- Safe to delete old log files
- Consider reducing log level to WARNING

## Examples

### Successful Operation Log
```
[INFO] Loading CSV file: sample_data.csv
[INFO] Successfully loaded CSV: shape=(30, 4), columns=['temperature', 'pressure', 'humidity', 'power_output']
[INFO] Columns selected - X: temperature, Y: power_output, Z:
[INFO] Generating correlation plot in static mode
[INFO] Plot generated - temperature vs power_output (R² = 0.9876)
```

### Failed Operation Log
```
[INFO] Loading CSV file: invalid_file.csv
[ERROR] File not found: invalid_file.csv
Traceback (most recent call last):
  File "src/data/sources/csv_source.py", line 40, in load
    raise FileNotFoundError(f"File not found: {file_path}")
FileNotFoundError: File not found: invalid_file.csv
```

## Log Format

File logs use this format:
```
[YYYY-MM-DD HH:MM:SS] LEVEL     [module.function:line] message
```

Example:
```
[2025-01-22 14:30:52] INFO     [ml_visualizer.data.sources.csv_source.load:35] Loading CSV file: sample.csv
```

This includes:
- **Timestamp**: When it happened
- **Level**: Severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Location**: Module, function, and line number
- **Message**: What happened

## Getting Help

If you encounter issues:

1. Check the latest log file
2. Look for ERROR messages with stack traces
3. Note the operation that failed
4. Share the relevant log excerpts when reporting issues
5. Include Python version and platform (shown at startup in logs)

The logging system is designed to capture everything needed to diagnose problems without exposing sensitive data.
