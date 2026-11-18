# PyInstaller spec for Pharmacy CRM (Windows, directory distribution).
from PyInstaller.utils.hooks import collect_all

pdf_datas, pdf_binaries, pdf_hidden = collect_all("pdfplumber")

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=pdf_binaries,
    datas=pdf_datas,
    hiddenimports=pdf_hidden,
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
    [],
    exclude_binaries=True,
    name="PharmacyCRM",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PharmacyCRM",
)
