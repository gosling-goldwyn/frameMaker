# -*- mode: python ; coding: utf-8 -*-

import sys
from os import environ
from pathlib import Path

# Set paths
project_dir = Path('__file__').parent.resolve()
sys.path.append(str(project_dir))

# Read environment variables
environ["PYTHONPATH"] = str(project_dir)

# PyInstaller configuration
block_cipher = None

a = Analysis(
    ['run_pywebview.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        ('html/*', 'html'),
        ('html/images/*', 'html/images'),
        ('html/js/*', 'html/js'),
        ('src/*', 'src'),
    ],
    hiddenimports=[],
    hookspath=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='frame-maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='frame-maker',
)