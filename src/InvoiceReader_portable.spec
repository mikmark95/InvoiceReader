# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Percorso dinamico a Qt6
try:
    import PyQt6
    pyqt_path = os.path.dirname(PyQt6.__file__)
    qt_path = os.path.join(pyqt_path, 'Qt6')
except ImportError:
    qt_path = r"C:/Users/emmes/AppData/Local/Programs/Python/Python312/Lib/site-packages/PyQt6/Qt6"

# Plugin Qt
qt_plugins = os.path.join(qt_path, 'plugins')
qt_bins = os.path.join(qt_path, 'bin')

a = Analysis(
    ['main.py'],
    pathex=['.'],  # assumi che sia lanciato da src
    binaries=[],
    datas=[
        (os.path.join(qt_bins, 'Qt6Core.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_bins, 'Qt6Gui.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_bins, 'Qt6Widgets.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_bins, 'Qt6Network.dll'), 'PyQt6/Qt6/bin'),
        (os.path.join(qt_bins, 'Qt6Svg.dll'), 'PyQt6/Qt6/bin'),

        (os.path.join(qt_plugins, 'platforms'), 'PyQt6/Qt6/plugins/platforms'),
        (os.path.join(qt_plugins, 'styles'), 'PyQt6/Qt6/plugins/styles'),
        (os.path.join(qt_plugins, 'imageformats'), 'PyQt6/Qt6/plugins/imageformats'),
    ],
    hiddenimports=[
        'PyQt6.sip',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtSvg',
        'fitz',  # se usi PyMuPDF
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='InvoiceReader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=r"C:\Users\emmes\Documents\Python Scripts\InvoiceReader\assets\invoice.ico" ,
)
