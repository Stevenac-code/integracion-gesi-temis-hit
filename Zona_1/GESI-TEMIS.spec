# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('utils/*.py', 'utils'),
    ('config/*.py', 'config'),
    ('core/*.py', 'core'),
    ('automation/*.py', 'automation'),
    ('data/*.py', 'data')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'pandas', 
        'numpy', 
        'shareplum', 
        'pyautogui', 
        'keyboard',
        'utils.logger',
        'config.settings',
        'core.sharepoint_manager',
        'core.temis_manager',
        'automation.gui_automation',
        'automation.resources',
        'data.data_processor'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GESI-TEMIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icono.png'
)