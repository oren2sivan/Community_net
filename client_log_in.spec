# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\ORENS\\תכנות\\VENV\\venv_oren\\project\\client\\client_log_in.py'],
    pathex=[],
    binaries=[],
    datas=[('config\\dependencies-1.bat', 'config'), ('config\\ipfs_config.bat', 'config')],
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
    name='client_log_in',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
