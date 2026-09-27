# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pdf-renamer-v2.py'],
    pathex=[],
    binaries=[],
    # Loaded at runtime via resource_path(): window/taskbar icon and the Help window's text.
    datas=[('app.ico', '.'), ('HELP.md', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pdf-renamer-v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',  # the .exe's icon in Explorer
)
