"""Windows launcher: runs cfab_browser.py without a console window.

Double-clicking this file (or `pythonw cfab_browser.pyw`) starts the app via
pythonw.exe, so no terminal pops up. All log/stdout/stderr output is captured
by the in-app Console tab.
"""

import os
import runpy
import sys


here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
sys.path.insert(0, here)

runpy.run_path(os.path.join(here, "cfab_browser.py"), run_name="__main__")
