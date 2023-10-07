# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

site_packages_dir = 'D:/PythonProjects/Rezker/venv/Lib/site-packages/'

a = Analysis(
    ['D:\\PythonProjects\\Rezker\\main.py'],
    pathex=[],
    binaries=[],
    datas=[(site_packages_dir+'plyer', './plyer'), ('./default/default_settings.json', 'default'), ('./assets/fonts/*.ttf', 'assets/fonts'), ('./assets/img/*.png', 'assets/img'), ('./libs/*.kv', 'libs'), ('./libs/Views/kv/*.kv', 'libs/Views/kv')],
    hiddenimports=['mutagen', 'bs4', 'validators', 'pySmartDL'],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    exclude_binaries=True,
    name='Rezker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./res/icon.ico',
	hide_console='hide-late',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Rezker',
)
