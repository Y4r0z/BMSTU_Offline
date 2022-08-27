# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['source\\main.py'],
    pathex=[],
    binaries=[],
    datas=
    [
        ('source\\windows\\AuthForm.ui','windows'),
        ('source\\windows\\SettingsForm.ui','windows'),
        ('source\\windows\\SplashScreenForm.ui','windows'),
        ('source\\windows\\UniversalForm.ui','windows'),
        ('source\\windows\\PropertyForm.ui','windows')
    ],
    hiddenimports=[],
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
    name='BMSTU_Desktop_Debug',
    debug=True,
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
    icon='icons\\BMSTU_cut.ico',
)
