# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pandas', 'pygame'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add additional data files
a.datas += [
    ('utils.py', 'utils.py', 'DATA'),
    ('timer_module.py', 'timer_module.py', 'DATA'),
    ('name_picker_module.py', 'name_picker_module.py', 'DATA'),
    ('tournament_display.py', 'tournament_display.py', 'DATA'),
    ('tournament_module.py', 'tournament_module.py', 'DATA'),
    ('timer_tick.wav', 'timer_tick.wav', 'DATA'),
    ('timer_end.wav', 'timer_end.wav', 'DATA'),
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='School Application',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # You can add an icon file if you have one
) 