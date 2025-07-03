# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cfab_browser.py'],
    pathex=[],
    binaries=[],
    datas=[('core/resources', 'core/resources'), ('config.json', '.')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'core.main_window', 'core.json_utils', 'core.amv_tab', 'core.pairing_tab', 'core.tools_tab', 'core.file_utils', 'core.scanner', 'logging', 'json', 'pathlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython', 'jupyter', 'notebook', 'pydoc', 'doctest', 'unittest', 'test', 'PyQt6.QtNetwork', 'PyQt6.QtSql', 'PyQt6.QtTest', 'PyQt6.QtBluetooth', 'PyQt6.QtLocation', 'PyQt6.QtMultimedia', 'PyQt6.QtWebEngineWidgets'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    exclude_binaries=True,
    name='CFAB_Browser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['core\\resources\\img\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['ucrtbase.dll'],
    name='CFAB_Browser',
)
