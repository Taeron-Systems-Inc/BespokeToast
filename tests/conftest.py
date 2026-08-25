import os
import sys

# The firmware package is what ships to the device; tests import it directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))
