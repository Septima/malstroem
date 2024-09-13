import sys
import os
from pathlib import Path

# This is a runtime hook which sets the PROJ_LIB env var to point at 
# the bundled proj data

proj_path = Path(sys._MEIPASS) / "proj_data"
os.environ['PROJ_DATA'] = str(proj_path)