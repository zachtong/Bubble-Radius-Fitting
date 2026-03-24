# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Bubble Radius Fitting."""

import os

block_cipher = None

ROOT = os.path.abspath('.')
SRC = os.path.join(ROOT, 'src', 'bubbletrack')

a = Analysis(
    [os.path.join(SRC, 'app.py')],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=[],
    datas=[
        (os.path.join(SRC, 'resources', 'style.qss'), os.path.join('bubbletrack', 'resources')),
        (os.path.join(SRC, 'resources', 'icon.ico'), os.path.join('bubbletrack', 'resources')),
    ],
    hiddenimports=[
        # UI
        'bubbletrack.ui.main_window',
        'bubbletrack.ui.header_bar',
        'bubbletrack.ui.status_bar',
        'bubbletrack.ui.left_panel',
        'bubbletrack.ui.image_panel',
        'bubbletrack.ui.image_source',
        'bubbletrack.ui.tab_bar',
        'bubbletrack.ui.pretune_tab',
        'bubbletrack.ui.manual_tab',
        'bubbletrack.ui.automatic_tab',
        'bubbletrack.ui.post_processing',
        'bubbletrack.ui.radius_chart',
        'bubbletrack.ui.frame_scrubber',
        'bubbletrack.ui.widgets',
        'bubbletrack.ui.shortcuts',
        'bubbletrack.ui.image_compare',
        'bubbletrack.ui.welcome_dialog',
        # Controller
        'bubbletrack.controller.base',
        'bubbletrack.controller.controller',
        'bubbletrack.controller.file_controller',
        'bubbletrack.controller.pretune_controller',
        'bubbletrack.controller.manual_controller',
        'bubbletrack.controller.auto_controller',
        'bubbletrack.controller.export_controller',
        'bubbletrack.controller.display_mixin',
        'bubbletrack.controller.worker',
        # Model
        'bubbletrack.model.anomaly',
        'bubbletrack.model.auto_optimize',
        'bubbletrack.model.batch_experiments',
        'bubbletrack.model.cache',
        'bubbletrack.model.circle_fit',
        'bubbletrack.model.config',
        'bubbletrack.model.constants',
        'bubbletrack.model.conventions',
        'bubbletrack.model.detection',
        'bubbletrack.model.export',
        'bubbletrack.model.image_io',
        'bubbletrack.model.presets',
        'bubbletrack.model.removing_factor',
        'bubbletrack.model.report',
        'bubbletrack.model.session',
        'bubbletrack.model.state',
        'bubbletrack.model.undo',
        # Core
        'bubbletrack.event_bus',
        'bubbletrack.logging_config',
        # Third-party
        'pyqtgraph',
        'openpyxl',
        'fpdf',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "unittest", "email", "xml",
        "PyQt5", "PySide2", "PySide6",
        "PyQt6.QtWebEngine", "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets",
        "PyQt6.Qt3D", "PyQt6.QtBluetooth", "PyQt6.QtMultimedia",
        "PyQt6.QtNetwork", "PyQt6.QtSql", "PyQt6.QtTest",
        "PyQt6.QtQml", "PyQt6.QtQuick",
        "matplotlib",
        "IPython", "sphinx", "docutils", "nbformat", "dask",
        "black", "yapf_third_party", "astroid",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BubbleRadiusFitting',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(SRC, 'resources', 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BubbleRadiusFitting',
)
