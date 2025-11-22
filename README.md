# ML Data Pipeline Visualizer - MVP

A lightweight, extensible GUI application for visualizing ML data pipelines with a focus on interactivity and low latency.

## Features (MVP v0.1.0)

- **CSV Data Loading**: Load CSV/TSV files with automatic validation
- **Column Selection**: Interactive selection of X and Y columns from numeric data
- **Correlation Plots**: High-quality scatter plots with regression lines
- **Linearity Metrics**: Real-time calculation and display of:
  - Slope and Intercept
  - R² (Coefficient of Determination)
  - RMSE (Root Mean Square Error)
  - Pearson correlation coefficient
  - P-value and Standard Error
- **Interactive Visualization**: Pan, zoom, and explore your data
- **Clean Architecture**: Built with SOLID principles for extensibility

## Architecture

The application follows a layered architecture with clear separation of concerns:

```
src/
├── core/
│   ├── interfaces/       # Abstract interfaces (Strategy pattern)
│   │   ├── data_source.py    # IDataSource interface
│   │   ├── analyzer.py       # IAnalyzer interface
│   │   └── renderer.py       # IRenderer interface
│   └── models/           # Data models
├── data/
│   └── sources/          # Data source implementations
│       └── csv_source.py     # CSV data loader
├── analysis/
│   └── correlation_analyzer.py  # Correlation analysis
├── visualization/
│   └── renderers/
│       └── correlation_renderer.py  # Plot rendering
└── gui/
    ├── main_window.py    # Main application window
    └── widgets/          # UI components
        ├── data_loader.py
        ├── column_selector.py
        ├── plot_widget.py
        └── metrics_widget.py
```

### Design Principles

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible through interfaces without modification
- **Liskov Substitution**: Implementations are interchangeable
- **Interface Segregation**: Focused, minimal interfaces
- **Dependency Inversion**: Depends on abstractions, not concretions

## Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/vivekkr1809/ml_data_pipeline_visualization.git
cd ml_data_pipeline_visualization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install in development mode:
```bash
pip install -e .
```

## Usage

### Running the Application

From the project root directory:

```bash
python -m src.main
```

Or if installed:
```bash
ml-visualizer
```

### Workflow

1. **Load Data**: Click "Load CSV File" and select your CSV file
2. **Select Columns**: Choose X and Y columns from the numeric columns
3. **Generate Plot**: Click "Generate Plot" to create the visualization
4. **Explore**: Use the interactive toolbar to zoom, pan, and save the plot
5. **Analyze**: Review the linearity metrics in the left panel

## Extending the Application

The architecture is designed for easy extension:

### Adding New Data Sources

Implement the `IDataSource` interface:

```python
from src.core.interfaces.data_source import IDataSource

class ExcelDataSource(IDataSource):
    def load(self, file_path: str, **kwargs) -> pd.DataFrame:
        # Implementation
        pass

    def validate(self, file_path: str) -> bool:
        # Implementation
        pass

    def get_supported_extensions(self) -> list[str]:
        return ['.xlsx', '.xls']
```

### Adding New Analyzers

Implement the `IAnalyzer` interface:

```python
from src.core.interfaces.analyzer import IAnalyzer, AnalysisResult

class CustomAnalyzer(IAnalyzer):
    def analyze(self, data: pd.DataFrame, **kwargs) -> AnalysisResult:
        # Implementation
        pass
```

### Adding New Renderers

Implement the `IRenderer` interface:

```python
from src.core.interfaces.renderer import IRenderer, RenderConfig

class CustomRenderer(IRenderer):
    def render(self, data: pd.DataFrame, config: RenderConfig, **kwargs) -> Figure:
        # Implementation
        pass
```

## Future Roadmap

- **Data Types**: Support for Excel, JSON, Parquet, SQL databases
- **Custom Data Types**: Plugin system for user-defined data types
- **Advanced Plots**:
  - Contour plots
  - 3D scatter plots
  - Heatmaps
  - Distribution plots
- **Static Export**: High-resolution image export (PNG, SVG, PDF)
- **Interactive Mode**: Plotly-based interactive dashboards
- **Data Preprocessing**: Filtering, transformations, outlier removal
- **Batch Processing**: Analyze multiple column pairs simultaneously
- **Themes**: Customizable color schemes and styles
- **Cross-Platform**: macOS support

## Technology Stack

- **GUI Framework**: PyQt6 (cross-platform, performant)
- **Data Processing**: pandas, numpy
- **Statistics**: scipy
- **Visualization**: matplotlib (static), plotly (future - interactive)
- **Architecture**: Clean Architecture, SOLID principles

## Performance

The MVP is optimized for:
- **Low Latency**: Fast CSV loading and plot generation
- **Interactivity**: Responsive UI with background processing
- **Memory Efficiency**: Efficient data handling with pandas
- **Scalability**: Tested with datasets up to 100K rows

## Platform Support

- **Windows**: Fully supported (primary target)
- **Linux**: Supported
- **macOS**: Planned for future releases

## Contributing

Contributions are welcome! The codebase is designed to be:
- **Extensible**: Easy to add new features
- **Composable**: Components work together seamlessly
- **Debuggable**: Clear interfaces and error handling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with inspiration from professional data analysis tools like JMP, with a focus on simplicity and extensibility.
