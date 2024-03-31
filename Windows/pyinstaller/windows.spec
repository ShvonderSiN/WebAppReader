# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\..\\webappreader.py'],
    pathex=[],
    binaries=[('..\\..\\wget.exe', '.')],
    datas=[('..\\..\\src', 'src')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pysqlite2', 'MySQLdb', 'psycopg2'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='webappreader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity="Sergei Shekin",
    entitlements_file=None,
    version='..\\..\\version_file.txt',
    icon=['..\\..\\src\\logo.ico'],
)
coll = COLLECT(

    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='webappreader',
)
