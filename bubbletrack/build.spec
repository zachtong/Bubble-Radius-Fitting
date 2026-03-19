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
        'bubbletrack.controller.controller',
        'bubbletrack.controller.worker',
        'bubbletrack.model.circle_fit',
        'bubbletrack.model.detection',
        'bubbletrack.model.export',
        'bubbletrack.model.image_io',
        'bubbletrack.model.removing_factor',
        'bubbletrack.model.state',
        'pyqtgraph',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
