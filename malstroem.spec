# -*- mode: python -*-
from os import environ
from pathlib import Path


block_cipher = None
datas = []
runtime_hooks = []


# Support new proj data style.
# If PROJ_DATA is set we assume new style. This means bundling proj data files with
# the exe and then setting PROJ_DATA to point at the bundled data in a runtime hook.
proj_data = environ.get("PROJ_DATA")
if proj_data:
    proj_lib_path = Path(proj_data)
    # https://pyinstaller.readthedocs.io/en/stable/spec-files.html#adding-data-files
    datas.append((str(proj_lib_path / "proj.db"), "proj_data"))
    runtime_hooks.append(Path("pyinstaller/proj_runtime_hook.py"))

a = Analysis(['malstroem/scripts/cli.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=["malstroem.algorithms.speedups._fill","malstroem.algorithms.speedups._flow","malstroem.algorithms.speedups._label", "cyarray.carray"],
             hookspath=[],
             runtime_hooks=runtime_hooks,
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='malstroem',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
