# BubbleTrack v2.0

Bubble radius fitting tool for high-speed camera image sequences. Detects bubble boundaries via adaptive thresholding and edge detection, then fits circles using the Taubin algebraic method to extract radius-vs-time data.

Originally developed in MATLAB; now available as a cross-platform Python/PyQt6 desktop application.

## Features

- **Three analysis modes**
  - **Pre-tune** — adjust threshold, removing factor, and edge-crossing flags on a single frame, then fit to preview results
  - **Manual** — select 3 boundary points by clicking on the image; circle is fitted to the selected points
  - **Automatic** — batch-process a frame range with one click; runs detection + fitting in a background thread with a progress bar

- **Side-by-side image viewer** — original image and binary mask displayed together with zoom/pan controls and overlay visualizations (ROI rectangle, detected edge points, fitted circle)

- **Interactive ROI selection** — drag a rectangle directly on the image to define the region of interest

- **R(t) scatter chart** — live-updating radius-vs-frame plot as you process frames

- **Data export** — save results to `.mat` files compatible with MATLAB:
  - `R_data.mat` — raw radii, circle centres, edge coordinates
  - `RofTdata.mat` — physical-unit R(t) with quadratic Rmax fitting

## Project Structure

```
Bubble_Radius_Fitting/
├── bubbletrack/                 # Python implementation
│   ├── src/bubbletrack/
│   │   ├── model/               # Core algorithms (no GUI dependency)
│   │   │   ├── circle_fit.py    #   Taubin circle fitting
│   │   │   ├── detection.py     #   Bubble boundary detection pipeline
│   │   │   ├── export.py        #   .mat file export
│   │   │   ├── image_io.py      #   Image loading, normalisation, binarisation
│   │   │   ├── removing_factor.py # Logarithmic slider mapping
│   │   │   └── state.py         #   Application state dataclass
│   │   ├── controller/
│   │   │   ├── controller.py    #   Main application controller (MVC)
│   │   │   └── worker.py        #   QThread worker for batch processing
│   │   ├── ui/                  #   PyQt6 widgets
│   │   │   ├── main_window.py   #   Top-level 3-panel layout
│   │   │   ├── image_panel.py   #   QGraphicsView image viewer with overlays
│   │   │   ├── pretune_tab.py   #   Pre-tune parameter controls
│   │   │   ├── manual_tab.py    #   Manual point-selection controls
│   │   │   ├── automatic_tab.py #   Batch processing controls
│   │   │   ├── radius_chart.py  #   Matplotlib R(t) scatter chart
│   │   │   ├── post_processing.py # Export panel (FPS, scale, save path)
│   │   │   └── ...              #   Header, status bar, sidebar, etc.
│   │   ├── resources/
│   │   │   └── style.qss        #   Application stylesheet
│   │   └── app.py               #   Entry point
│   ├── tests/                   #   pytest test suite
│   └── pyproject.toml
├── matlab_implementation/       # Original MATLAB implementation
│   ├── GUI_source_code_1_19.m   #   Monolithic GUI class
│   ├── +bubblefit/              #   Modularised MATLAB package
│   └── example/                 #   Sample TIFF image sequence
└── Modern GUI Design for Tabs/  # Figma design reference (React/Tailwind)
```

## Requirements

- Python 3.10+
- Dependencies: PyQt6, NumPy, OpenCV, scikit-image, SciPy, Matplotlib

## Installation

```bash
cd bubbletrack
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e .
```

## Usage

```bash
# Run the application
bubbletrack

# Or run as a module
python -m bubbletrack
```

### Quick Start

1. Click **Browse** in the left panel to select a folder of image files (TIFF, PNG, JPG, BMP)
2. The first image loads automatically; use the **frame scrubber** slider to navigate
3. Switch to the **Pre-tune** tab:
   - Drag on the image to select an ROI (region of interest)
   - Adjust **Threshold** and **Removing Factor** sliders until the bubble boundary is clean in the binary preview
   - Check edge-crossing flags if the bubble extends beyond the ROI boundary
   - Click **Fit Current Frame** to run detection + circle fitting
4. For single-frame analysis, use **Manual** mode: click 3 points on the bubble boundary, then click **Done**
5. For batch processing, use **Automatic** mode: set the frame range and click **Run All**
6. Open **Post Processing** to set FPS, scale (um/px), and export results as `.mat` files

## Running Tests

```bash
cd bubbletrack
pip install -e ".[dev]"
pytest tests/ -v
```

## Algorithm Overview

1. **Adaptive binarisation** — converts greyscale images to binary using local mean thresholding (OpenCV `adaptiveThreshold`, matching MATLAB's `imbinarize('adaptive')`)
2. **Small object removal** — filters noise by removing connected components below a size threshold (logarithmically mapped from slider value)
3. **Boundary expansion** — doubles the image along a non-crossing edge to handle bubbles that extend beyond the ROI
4. **Blob filtering** — selects the largest blob after rejecting regions that are too elongated (axis ratio > 2.2 or eccentricity > 1.6)
5. **Edge detection** — extracts the boundary via morphological gradient (dilation XOR original)
6. **Circle fitting** — applies the Taubin algebraic method to boundary points, yielding centre coordinates and radius
7. **Rmax fitting** — quadratic fit around the peak radius to interpolate the true maximum

## Reference

Circle fitting algorithm:

> G. Taubin, "Estimation Of Planar Curves, Surfaces And Nonplanar Space Curves Defined By Implicit Equations, With Applications To Edge And Range Image Segmentation", IEEE Trans. PAMI, Vol. 13, pp 1115-1138, 1991.

## License

For academic and research use.
