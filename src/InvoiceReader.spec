# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyQt6.QtCore import QLibraryInfo

block_cipher = None

# Ottenere il percorso Qt in modo dinamico
qt_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PrefixPath)

# Se QLibraryInfo non funziona, usa questo come fallback
if not os.path.exists(qt_path):
    # Cerca nella directory di installazione di Python
    python_path = os.path.dirname(sys.executable)
    qt_path = os.path.join(python_path, 'Lib', 'site-packages', 'PyQt6', 'Qt6')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Qt DLLs
        (os.path.join(qt_path, 'bin', 'Qt6Core.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_path, 'bin', 'Qt6Gui.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_path, 'bin', 'Qt6Widgets.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_path, 'bin', 'Qt6Network.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_path, 'bin', 'Qt6Svg.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_path, 'plugins', 'platforms', 'qwindows.dll'), 'PyQt6/Qt6/plugins/platforms'),
        (os.path.join(qt_path, 'plugins', 'styles'), 'PyQt6/Qt6/plugins/styles'),
        (os.path.join(qt_path, 'plugins', 'imageformats'), 'PyQt6/Qt6/plugins/imageformats'),
    ],
    hiddenimports=[
        'PyQt6.sip',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.QtCore',
        'PyQt6.QtNetwork',
        'PyQt6.QtSvg',
        'fitz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='InvoiceReader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Imposta su True per vedere i messaggi di errore durante il test
    icon=r"C:\Users\emmes\Documents\Python Scripts\InvoiceReader\assets\invoice.ico"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='InvoiceReader'
)