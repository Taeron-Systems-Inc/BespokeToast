import os
import sys

HERE = os.path.dirname(__file__)
FIRMWARE = os.path.abspath(os.path.join(HERE, "..", "firmware"))

# APPENDED, not inserted. firmware/ contains code.py, which is the
# CircuitPython entry point and also the name of a standard library module.
# Putting firmware/ at the front of sys.path shadows it, and anything that
# imports `code` -- pytest does, internally -- gets a module that expects to
# be running on a SAMD51.
if FIRMWARE not in sys.path:
    sys.path.append(FIRMWARE)
sys.path.insert(0, HERE)
