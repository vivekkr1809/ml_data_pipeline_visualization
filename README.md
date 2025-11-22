# ML Data Pipeline Visualizer

A lightweight, extensible GUI application for visualizing ML data pipelines with support for **interactive plots** and **contour visualization**. Built with a focus on interactivity, low latency, and clean architecture.

## 🎉 New Features (v0.2.0)

### Interactive Plotly Mode
- **Fully Interactive Plots**: Pan, zoom, hover tooltips with Plotly
- **High-Resolution Export**: Export plots as PNG with configurable DPI
- **Real-time Interaction**: Smooth, responsive visualizations
- **Toggle Mode**: Switch between Static (Matplotlib) and Interactive (Plotly)

### Contour Plot Support
- **3D Data Visualization**: Visualize X, Y, Z relationships
- **2D Filled Contours**: Heatmap-style contour plots
- **3D Surface Plots**: Full 3D interactive surface visualization
- **Grid Interpolation**: Linear and cubic interpolation methods
- **Surface Statistics**: Min, max, mean, gradient calculations

## Features

### Data Loading & Management
- **CSV Data Loading**: Load CSV/TSV files with automatic validation
- **Column Selection**: Interactive selection of columns (2 for correlation, 3 for contour)
- **Sample Datasets**: Included sample data for testing

### Correlation Analysis
- **Scatter Plots with Regression**: High-quality visualization with trend lines
- **Linearity Metrics**: Real-time calculation and display of:
  - Slope and Intercept
  - R² (Coefficient of Determination)
  - RMSE (Root Mean Square Error)
  - Pearson correlation coefficient
  - P-value and Standard Error
- **Static & Interactive Modes**: Matplotlib or Plotly rendering

### Contour Visualization
- **2D Contour Maps**: Filled contours with customizable levels
- **3D Surface Plots**: Fully rotatable 3D surfaces
- **Interpolation**: Smooth surfaces from scattered data points
- **Original Data Overlay**: Show raw data points on contours

### Architecture & Extensibility
- **Clean Architecture**: Built with SOLID principles
- **Plugin-Ready**: Easy to add new plot types, data sources, analyzers
- **Multiple Renderers**: Matplotlib and Plotly support
- **Dependency Injection**: All components are swappable

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
2. **Choose Plot Type**: Select "Correlation" or "Contour" from Plot Options
3. **Select Mode**: Choose "Static (Matplotlib)" or "Interactive (Plotly)"
4. **Select Columns**:
   - **Correlation**: Choose X and Y columns
   - **Contour**: Choose X, Y, and Z columns
5. **Generate Plot**: Click "Generate Plot" to create the visualization
6. **Interact**:
   - **Static Mode**: Use toolbar to pan, zoom, save
   - **Interactive Mode**: Hover for tooltips, pan, zoom, rotate (3D)
7. **Analyze**: Review metrics in the left panel (correlation plots)

### Sample Datasets

Try the included sample datasets:
- `sample_data.csv`: Temperature, pressure, humidity, power output (correlation)
- `sample_contour_data.csv`: X, Y positions with temperature, pressure, efficiency (contour)
- `sample_terrain_data.csv`: Longitude, latitude, elevation, rainfall, vegetation (contour)

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
