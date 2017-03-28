# Adam Wujek CERN 2017
#
# Wrapper to run bash script
#
import sys
import os
import subprocess

ret_val = subprocess.call("/nfs/cs-ccr-nfs3/vol1/u1/white_rabbit/tools/wrs-config-generator/ccde_cmd", stdin=sys.stdin, stdout=sys.stderr)
# We need to return SUCCESS if all went ok
if ret_val == 0:
    sys.stdout.write('SUCCESS')
else:
    sys.stdout.write('FAIL')

sys.exit(ret_val)
