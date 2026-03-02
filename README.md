# Bubble Radius Fitting

Desktop application for extracting bubble radius vs. time data from high-speed camera image sequences. Detects bubble boundaries via adaptive thresholding and morphological filtering, then fits circles using the Taubin algebraic method.

Originally developed in MATLAB; now available as a cross-platform Python/PyQt6 application.

## Features

- **Three analysis modes**
  - **Pre-tune** — adjust threshold, removing factor, advanced filters, and edge-crossing flags on a single frame; click **Fit Current Frame** to preview the result
  - **Manual** — click 3+ points on the bubble boundary, then click **Done** to fit a circle through the selected points
  - **Automatic** — batch-process a range of frames in a background thread with real-time progress and live image updates

- **Side-by-side image viewer** — original greyscale image and processed binary mask displayed together with zoom/pan controls and overlay visualizations (ROI rectangle, detected edge points, fitted circle)

- **Interactive ROI selection** — drag a rectangle directly on the image to define the region of interest

- **Advanced image filters** — optional pre-processing pipeline (Gaussian Blur, CLAHE, Morphological Open/Close) with toggle controls, saveable/loadable presets

- **R(t) scatter chart** — live-updating radius-vs-frame scatter plot

- **Data export** — save results to `.mat` files compatible with MATLAB:
  - **Export Pixel Data** — raw radii (px), circle centres, edge coordinates
  - **Export Physical Data** — physical-unit R(t) with configurable FPS and um/px scale, plus quadratic Rmax interpolation

- **Radius outlier filtering** — automatically rejects fitted circles whose radius exceeds the image's long-side dimension

## Project Structure

```
Bubble_Radius_Fitting/
├── bubbletrack/                  # Python implementation
│   ├── src/bubbletrack/
│   │   ├── app.py                #   Entry point
│   │   ├── model/                #   Core algorithms (no GUI dependency)
│   │   │   ├── circle_fit.py     #     Taubin circle fitting
│   │   │   ├── detection.py      #     Bubble boundary detection pipeline
│   │   │   ├── export.py         #     .mat file export
│   │   │   ├── image_io.py       #     Image loading, normalisation, binarisation
│   │   │   ├── removing_factor.py#     Logarithmic slider-to-area mapping
│   │   │   └── state.py          #     Application state dataclass
│   │   ├── controller/
│   │   │   ├── controller.py     #     Main MVC controller
│   │   │   └── worker.py         #     QThread worker for batch processing
│   │   ├── ui/                   #     PyQt6 widgets
│   │   │   ├── main_window.py    #       Top-level 3-panel layout
│   │   │   ├── image_panel.py    #       QGraphicsView image viewer with overlays
│   │   │   ├── pretune_tab.py    #       Pre-tune parameter controls
│   │   │   ├── manual_tab.py     #       Manual point-selection controls
│   │   │   ├── automatic_tab.py  #       Batch processing controls
│   │   │   ├── radius_chart.py   #       Matplotlib R(t) scatter chart
│   │   │   ├── post_processing.py#       Export panel (FPS, scale, Rmax fit)
│   │   │   ├── widgets.py        #       Reusable UI primitives
│   │   │   └── ...               #       Header, status bar, sidebar, etc.
│   │   └── resources/
│   │       ├── icon.ico           #   Application icon
│   │       └── style.qss          #   QSS stylesheet
│   ├── tests/                     #   pytest test suite (49 tests)
│   └── pyproject.toml
├── matlab_implementation/         # Original MATLAB implementation
│   ├── GUI_source_code_1_19.m     #   Monolithic GUI class
│   ├── +bubblefit/                #   Modularised MATLAB package
│   └── example/                   #   Sample TIFF image sequence
└── Modern GUI Design for Tabs/    # Figma design reference (React/Tailwind)
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

1. Click **Browse** to select a folder of image files (TIFF, PNG, JPG, BMP)
2. The first image loads automatically; use the **frame scrubber** slider to navigate
3. Switch to the **Pre-tune** tab:
   - Drag on the image to select an ROI (region of interest)
   - Adjust **Threshold** and **Removing Factor** sliders until the bubble boundary is clean in the binary mask
   - Expand **Advanced Filters** to enable Gaussian Blur, CLAHE, Morph Open/Close if needed
   - Check edge-crossing flags if the bubble extends beyond the ROI boundary
   - Click **Fit Current Frame** to run detection + circle fitting
4. For single-frame analysis, use **Manual** mode: click 3+ points on the bubble boundary, then click **Done**
5. For batch processing, use **Automatic** mode: set the frame range and click **Run All**
6. In the **Post Processing** section, set FPS and um/px scale, then click **Export Pixel Data** or **Export Physical Data** to save results as `.mat` files

### Parameter Guide

| Parameter | Effect |
|-----------|--------|
| **Threshold** | Adaptive binarisation sensitivity. Higher = more white pixels (bubble interior brighter). Lower = stricter foreground detection. |
| **Removing Factor** | Remove small white speckles from the binary image. Higher = removes larger noise regions. |
| **Gaussian Blur** | Smooths the greyscale image before binarisation to suppress small noise (e.g. tracer beads). |
| **CLAHE** | Contrast Limited Adaptive Histogram Equalisation. Improves local contrast when lighting is uneven. |
| **Morph Close** | Fills small holes and gaps inside the bubble boundary after binarisation. |
| **Morph Open** | Removes thin protrusions and spurs on the bubble edge after binarisation. |
| **Edge flags** | Check the edges where the bubble extends beyond the ROI boundary. The algorithm expands the image in the opposite direction to handle partial bubbles. |

## Running Tests

```bash
cd bubbletrack
pip install -e ".[dev]"
pytest tests/ -v
```

## Algorithm Overview

1. **Adaptive binarisation** — converts greyscale images to binary using local mean thresholding (OpenCV `adaptiveThreshold`, matching MATLAB's `imbinarize('adaptive')`)
2. **Optional pre-filters** — Gaussian blur for noise suppression, CLAHE for contrast normalisation (applied before binarisation)
3. **Small object removal** — filters noise by removing connected components below a size threshold (logarithmically mapped from the slider value)
4. **Boundary expansion** — doubles the image along a non-crossing edge to handle bubbles that extend beyond the ROI
5. **Optional morphological operations** — opening removes spurs; closing fills gaps (applied after binarisation)
6. **Blob filtering** — selects the largest blob after rejecting regions that are too elongated (axis ratio > 2.2 or eccentricity > 1.6)
7. **Edge detection** — extracts the boundary via morphological gradient (dilation XOR original)
8. **Circle fitting** — applies the Taubin algebraic method to boundary points, yielding centre coordinates and radius
9. **Rmax fitting** — quadratic interpolation around the peak radius to find the true maximum with sub-frame precision

## Reference

Circle fitting algorithm:

> G. Taubin, "Estimation Of Planar Curves, Surfaces And Nonplanar Space Curves Defined By Implicit Equations, With Applications To Edge And Range Image Segmentation", IEEE Trans. PAMI, Vol. 13, pp 1115-1138, 1991.

## License

For academic and research use.
