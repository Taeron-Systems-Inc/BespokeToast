import os
import sys

HERE = os.path.dirname(__file__)
# The firmware package is what ships to the device; tests import it directly.
sys.path.insert(0, os.path.join(HERE, "..", "firmware"))
# and the simulator lives beside the tests
sys.path.insert(0, HERE)
