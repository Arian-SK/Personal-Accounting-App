# main.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['source_code.py'],  # Your main script
    pathex=[],
    binaries=[],
    datas=[
        ('MainWindow.ui', '.'), 
        ('SignUpPage.ui', '.'), 
        ('LoginPage.ui', '.'), 
        ('PasswordRecoveryPage.ui', '.'),
        ('resources/*', 'resources/'),
        ('database/*', 'database/')
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
    [],
    exclude_binaries=True,
    name='Personal Accounting App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Change to False if you want to hide the console
    icon='main icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Personal Accounting App',
)
