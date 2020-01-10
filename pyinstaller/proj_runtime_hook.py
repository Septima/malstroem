import sys
import os
from pathlib import Path

# This is a runtime hook which sets the PROJ_LIB env var to point at 
# the bundled proj data
proj_lib = os.environ.get("PROJ_LIB")
if not proj_lib:
    proj_path = Path(sys._MEIPASS) / "proj_data"
    os.environ['PROJ_LIB'] = str(proj_path)