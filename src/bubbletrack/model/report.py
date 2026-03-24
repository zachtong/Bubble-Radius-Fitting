"""Generate PDF summary report of analysis results."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np


def generate_report(
    filepath: str,
    state,
    chart_image_path: str | None = None,
) -> None:
    """Generate a PDF report with parameters, statistics, and R-t chart.

    Parameters
    ----------
    filepath : str
        Output PDF path.
    state : AppState
        Current application state with results.
    chart_image_path : str or None
        Optional path to a chart screenshot to embed.

    Raises
    ------
    ImportError
        If fpdf2 is not installed.
    """
    from fpdf import FPDF  # lazy import to avoid hard dependency

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "BubbleTrack Analysis Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.ln(10)

    # Parameters section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    folder = state.folder_path or state.video_path or "(none)"
    params = {
        "Source": folder,
        "Threshold": f"{state.img_thr:.2f}",
        "Removing Factor": str(state.removing_factor),
        "ROI": f"rows {state.gridx}, cols {state.gridy}",
        "FPS": f"{state.fps:.0f} Hz",
        "Scale": f"{state.um2px:.2f} um/px",
    }
    for key, value in params.items():
        pdf.cell(50, 6, key + ":", new_x="RIGHT")
        pdf.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    # Statistics
    if state.radius is not None:
        valid = np.asarray(state.radius)
        valid = valid[valid > 0]
    else:
        valid = np.array([])

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Results Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    stats = {
        "Total Frames": str(state.total_frames),
        "Valid Fits": str(len(valid)),
        "Min Radius": f"{valid.min():.2f} px" if len(valid) else "N/A",
        "Max Radius": f"{valid.max():.2f} px" if len(valid) else "N/A",
        "Mean Radius": f"{valid.mean():.2f} px" if len(valid) else "N/A",
    }
    for key, value in stats.items():
        pdf.cell(50, 6, key + ":", new_x="RIGHT")
        pdf.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    # Chart image
    if chart_image_path and Path(chart_image_path).exists():
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "R-t Chart", new_x="LMARGIN", new_y="NEXT")
        pdf.image(chart_image_path, w=170)

    pdf.output(filepath)
