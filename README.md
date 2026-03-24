# BubbleTrack

Desktop application for extracting bubble radius vs. time data from high-speed camera image sequences. Detects bubble boundaries via adaptive thresholding and morphological filtering, then fits circles using the Taubin algebraic method.

## Installation

```bash
# Clone and set up
git clone https://github.com/zachtong/Bubble-Radius-Fitting.git
cd Bubble-Radius-Fitting

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (macOS / Linux)
source .venv/bin/activate

# Install
pip install -e .
```

## Usage

```bash
# Launch the GUI
bubbletrack

# Or run as a module
python -m bubbletrack
```

### Quick Start

1. **Open images** -- Click *Browse* to select a folder of images (TIFF, PNG, JPG, BMP)
2. **Navigate** -- Use the frame scrubber slider or press Play
3. **Pre-tune** -- Drag an ROI on the image, adjust Threshold and Removing Factor until the bubble boundary is clean, click *Fit Current Frame*
4. **Manual mode** -- Click 3+ points on the bubble edge, then click *Done*
5. **Automatic mode** -- Set the frame range and click *Run All* for batch processing
6. **Batch multi-folder** -- Process multiple experiment folders at once with identical parameters
7. **Export** -- Save results as `.mat`, CSV, or Excel from the Post Processing panel

### Standalone Executable

A pre-built Windows executable is available on the [Releases](https://github.com/zachtong/Bubble-Radius-Fitting/releases) page. No Python installation required -- just download and run.

## Features

| Category | Feature |
|----------|---------|
| **Analysis** | Three modes: Pre-tune, Manual (3+ point click), Automatic (batch) |
| **Auto-Tune** | One-click sensitivity optimisation with quality scoring |
| **Batch Processing** | Process multiple experiment folders with shared parameters |
| **Image Viewer** | Side-by-side original/binary display, zoom/pan, overlay/wipe comparison |
| **R(t) Chart** | Interactive scatter plot with hover tooltips, click-to-jump, right-click edit |
| **Filters** | Gaussian Blur, CLAHE, Morphological Open/Close, Max Radius cap |
| **Export** | `.mat` (R_data + RofT_data), CSV, Excel with physical-unit conversion |
| **Playback** | Play/pause with adjustable FPS, keyboard shortcuts |
| **Reports** | PDF report with parameters, statistics, and R(t) chart |
| **Session** | Save/load sessions, parameter presets |

## Project Structure

```
Bubble-Radius-Fitting/
├── src/bubbletrack/           # Application source code
│   ├── app.py                 #   GUI entry point
│   ├── cli.py                 #   CLI entry point
│   ├── model/                 #   Core algorithms (no GUI dependency)
│   │   ├── detection.py       #     Bubble boundary detection pipeline
│   │   ├── circle_fit.py      #     Taubin circle fitting
│   │   ├── export.py          #     .mat / CSV / Excel export
│   │   ├── image_io.py        #     Image loading and binarisation
│   │   ├── quality.py         #     Fit quality scoring
│   │   └── autotune.py        #     Auto-parameter optimisation
│   ├── controller/            #   MVC controllers
│   │   ├── controller.py      #     Main controller (signal wiring)
│   │   ├── worker.py          #     Background frame processing
│   │   └── batch_folder_worker.py  # Multi-folder batch worker
│   ├── ui/                    #   PyQt6 widgets
│   │   ├── main_window.py     #     3-panel layout
│   │   ├── image_panel.py     #     QGraphicsView with overlays
│   │   ├── radius_chart.py    #     pyqtgraph R(t) scatter chart
│   │   └── ...                #     Tabs, dialogs, controls
│   └── resources/
│       ├── style.qss          #   Dark-theme stylesheet
│       └── icon.ico           #   Application icon
├── tests/                     # pytest test suite
├── docs/                      # User guides, release notes
├── scripts/                   # Build and audit utilities
├── pyproject.toml             # Project metadata and dependencies
├── build.spec                 # PyInstaller spec (multi-file)
└── build_onefile.spec         # PyInstaller spec (single-file)
```

## Parameter Guide

| Parameter | Effect |
|-----------|--------|
| **Threshold** | Adaptive binarisation sensitivity. Higher = more white pixels. |
| **Removing Factor** | Remove small white speckles. Higher = removes larger noise regions. |
| **Gaussian Blur** | Smooth greyscale image before binarisation to suppress noise. |
| **CLAHE** | Adaptive histogram equalisation for uneven lighting. |
| **Morph Close** | Fill small holes and gaps inside the bubble boundary. |
| **Morph Open** | Remove thin protrusions on the bubble edge. |
| **Max Radius** | Cap fitted radius to reject false detections. |
| **Edge flags** | Handle bubbles extending beyond the ROI boundary. |

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

## Building the Executable

```bash
pip install -e ".[dev]"

# Multi-file distribution (faster startup)
pyinstaller build.spec

# Single-file distribution (easier to share)
pyinstaller build_onefile.spec
```

## Algorithm

1. **Adaptive binarisation** -- local mean thresholding converts greyscale to binary
2. **Pre-filters** -- optional Gaussian blur and CLAHE for noise/contrast
3. **Small object removal** -- filters components below a size threshold (log-mapped from slider)
4. **Boundary expansion** -- doubles the image along non-crossing edges for partial bubbles
5. **Morphological ops** -- opening removes spurs; closing fills gaps
6. **Blob selection** -- largest blob after rejecting elongated regions (axis ratio > 2.2)
7. **Edge detection** -- morphological gradient extracts boundary pixels
8. **Circle fitting** -- Taubin algebraic method yields centre and radius
9. **Rmax interpolation** -- quadratic fit around peak radius for sub-frame precision

## Reference

> G. Taubin, "Estimation of Planar Curves, Surfaces and Nonplanar Space Curves Defined by Implicit Equations, with Applications to Edge and Range Image Segmentation", IEEE Trans. PAMI, Vol. 13, pp. 1115--1138, 1991.

## Author

Zixiang (Zach) Tong, The University of Texas at Austin

## License

For academic and research use.
