# Project: Bubble Radius Fitting GUI

## Overview
MATLAB GUI app for bubble radius fitting from high-speed camera images.
Main file: `GUI_source_code_1_19.m` (class inheriting `matlab.apps.AppBase`).
Modularized into `+bubblefit/` package structure.

## GUI Redesign Reference (Figma)

### Figma Source
- **Figma Make URL**: https://www.figma.com/make/9l23iNi2VZaIrLa8504Ma0/Modern-GUI-Design-for-Tabs
- **Figma Design URL**: https://www.figma.com/design/9l23iNi2VZaIrLa8504Ma0/Modern-GUI-Design-for-Tabs
- **Local export**: `Modern GUI Design for Tabs/` directory (React + TypeScript + Tailwind)

### Design Layout (3-panel)
1. **Top Nav Bar** - Dark slate-900, app title "BubbleTrack v2.0", status indicator, settings buttons
2. **Main Area**:
   - **Left Sidebar** (300px, collapsible): Image source, mode tabs (Pre-tune/Manual/Automatic), post processing
   - **Right Content** (flex-1): Two image viewers side-by-side (Original + Binary), frame scrubber slider, R-t scatter chart
3. **Bottom Status Bar** - Frame info, format, scale, ROI coords, mode indicator

### Color Scheme
- Primary Blue: `#3B82F6` (active controls, sliders, buttons)
- Dark Navy: `#0F172A` (header/footer)
- Green: `#22C55E` (ROI rectangle, success)
- Red: `#EF4444` (edge detection, radius markers)
- Amber: `#FCD34D` (warnings/info)
- Slate grays for text/borders

### Key Design Components
| Component | File | Description |
|-----------|------|-------------|
| App layout | `src/app/App.tsx` | 3-panel layout, frame slider, sidebar toggle |
| Left panel | `src/app/components/LeftPanel.tsx` | Tabs, folder browser, mode selector |
| Pre-tune | `src/app/components/PreTuneTab.tsx` | ROI grid, threshold/RF sliders with dual input, edge checkboxes |
| Manual | `src/app/components/ManualTab.tsx` | Point counter with progress bar, instruction box |
| Automatic | `src/app/components/AutomaticTab.tsx` | Frame range, progress indicator, 3 action buttons |
| Image viewer | `src/app/components/ImagePanel.tsx` | Zoom controls, SVG bubble visualization, axis labels |
| R-t chart | `src/app/components/RadiusChart.tsx` | Recharts scatter plot, red cross markers |
| Post processing | `src/app/components/PostProcessing.tsx` | Collapsible, export paths, FPS/scale inputs, success states |
| UI primitives | `src/app/components/ui/` | 50+ shadcn/ui components |

### Design Features (vs current MATLAB GUI)
- Collapsible left sidebar for more image viewing space
- Integrated frame scrubber slider (not just number input)
- Zoom controls on image panels
- Visual progress indicator in Automatic mode (progress bar + percentage)
- Point counter with progress visualization in Manual mode
- Success state feedback on export buttons (green checkmark)
- Status bar showing current state
- Modern card-based layout with rounded corners and shadows

### Styling Reference
- CSS variables in `src/styles/theme.css` (oklch color space)
- Tailwind config in `src/styles/tailwind.css`
- Custom range input styling (blue gradient fill, white thumb)
- 4px scrollbar, slate colors

### Running the Design Preview
```bash
cd "Modern GUI Design for Tabs"
npm install
npm run dev
```
