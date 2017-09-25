# Adam Wujek CERN 2017
#
# Wrapper to run bash script
#
import sys
import os
import subprocess

ret_val = subprocess.call("/app/data/ccde_cmd", stdin=sys.stdin, stdout=sys.stderr)
# We need to return SUCCESS if all went ok
if ret_val == 0:
    sys.stdout.write('SUCCESS')
else:
    sys.stdout.write('FAIL')

sys.exit(ret_val)
