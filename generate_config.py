#!/usr/bin/env python2.7

# Adam Wujek,      CERN, 2017
# Jean-Claude Bau, CERN, 2019

import json
import requests
import base64
import sys, getopt
import getpass
import subprocess
import os
import time
import re

import settings
import ports

# -----------------------------------------------------------------------------

def print_help(prog_name):
    print """Usage:
""" + prog_name + """ <--json=<file>|--stdin> [--config=<file>] [--no-use-defaults]
""" + prog_name + """ <--ccde|--ccde-dev> --dev=<name> --user=<user> [--password=<password>] [--ccde-out=<file>] [--config=<file>] [--no-use-defaults]

Options:
--json=<file>		Get the json data directly from file
--ccde			Get the json data from the CCDE
--ccde-dev		Get the json data from the dev version of CCDE
--ccde-out=<file>	Save data from CCDE to the file. Requires ccde or ccde-dev to be used
--stdin			Get the json data from stdin
--user=<user>		User to CCDE. If not specified system username will be used.
--password=<password>	Password to CCDE. If not provided it will be prompted.
--config=<file>		Save generated dot-config in the file. By default in the file "dot-config".
--dev=<name>		Specify device name
--no-use-defaults	Don't use defaults for configuration items not defined in json/CCDE
"""
    print "Script version:",
    # the directory of the script being run
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print os.popen("cd "+script_dir+"; git describe --always --dirty").read()


def get_data_ccde(wrs_name, url, user, password):
    authData = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
    s = requests.Session()
    s.post(url + 'acw/login', data={'authentication':authData}, verify=False)
    r = s.get(url + 'whiterabbit/switches/' + wrs_name + '/configuration', verify=False)
    return r.text



# -----------------------------------------------------------------------------

inputfile = ''
outputfile = ''
ccde_url = ''
ccde_user = ''
ccde_password = ''
config_file = "dot-config"
ccde_json_file = ''
json_stdin = 'no'
ccde_dev_name = ''
file_json_in = ''
config_use_defaults = 'yes'

#url_ccde = 'https://ccde.cern.ch:9094/api/'
url_ccde = 'https://ccde.cern.ch/api/'
url_ccde_dev = 'https://ccde-dev.cern.ch/api/'

try:
    opts, args = getopt.getopt(sys.argv[1:],"h",
			       ["help", "ccde", "ccde-dev", "json=", "stdin", "config=",
				"ccde-out=", "user=", "password=", "dev=",
				"no-use-defaults"])
except getopt.GetoptError:
    print_help(sys.argv[0])
    sys.exit(1)

if len(opts) == 0:
    print_help(sys.argv[0])
    sys.exit()
for opt, arg in opts:
    if opt in ("-h", "--help"):
	print_help(sys.argv[0])
	sys.exit()
    elif opt == "--ccde":
	ccde_url = url_ccde
    elif opt == "--ccde-dev":
	ccde_url = url_ccde_dev
    elif opt == "--json":
	file_json_in = arg
    elif opt == "--stdin":
	json_stdin = 'yes'
    elif opt == "--config":
	config_file = arg
    elif opt == "--ccde-out":
	ccde_json_file = arg
    elif opt == "--user":
	ccde_user = arg
    elif opt == "--password":
	ccde_password = arg
    elif opt == "--dev":
	ccde_dev_name = arg
    elif opt == "--no-use-defaults":
	config_use_defaults = "no"
    else:
	print "unknown parameter" + opt

# count number of provided sources
source_n = (int)(ccde_url != '') \
	 + (int)(file_json_in != '') \
	 + (int)(json_stdin != 'no')

if (source_n > 1):
    print "Please specify only one --ccde[-dev], --json or --stdin"
    sys.exit(1)

if (source_n < 1):
    print "Please specify source of json data. One of --ccde[-dev], --json or --stdin"
    sys.exit(1)

# Get data from CCDE
if (ccde_url != ''):
    if (ccde_user == ''):
	ccde_user = getpass.getuser()
	print "Using current user's username for CCDE: " + ccde_user
    if (ccde_password == ''):
	ccde_password = getpass.getpass("Password for user " + ccde_user + " to access CCDE:")
    if (ccde_dev_name == ''):
	print "Please specify device name for CCDE access"
	sys.exit(1)
    ccde_data = get_data_ccde(ccde_dev_name, ccde_url, ccde_user, ccde_password)
    if (ccde_json_file != ''):
	print "Save ccde data to file: " + ccde_json_file
	ccdb_json_file_out = open(ccde_json_file, 'w')
	ccdb_json_file_out.write(ccde_data)
	ccdb_json_file_out.close()
    try:
	json_data = json.loads(ccde_data)
    except ValueError:
	print "ERROR: Unable to get valid json data from CCDE."
	if (ccde_json_file != ''):
	    print "Please check the file for CCDE response " + ccde_json_file
	else:
	    print "Please use parameter --ccde-out check the file for CCDE response " + ccde_json_file
	sys.exit(1)

# Get data from local file
if (file_json_in != ''):
    print "Reading data from file: " + file_json_in
    with open(file_json_in) as data_file:
	try:
	    json_data = json.load(data_file)
	except ValueError:
	    print "Error: Syntax error in file: " + file_json_in
	    sys.exit(1)
    data_file.close()

# Get data from stdin
if (json_stdin == 'yes'):
    stdin_data = ""
    while True:
	stdin_line = sys.stdin.readline()
	if len(stdin_line) == 0:
	    break
	stdin_data += stdin_line
    # try to convert stdin_data to json
    try:
	json_data = json.loads(stdin_data)
    except ValueError:
	print "Error: Syntax error in stdin data"
	sys.exit(1)

config_fd = open(config_file, 'w')
print "Saving dot-config to a file: " + config_file

if not ("switchName" in json_data):
    print "Switch %s does not exist in DB" % ccde_dev_name
    sys.exit(1)

print "Switch name %s" % json_data["switchName"]
print "HW version: %s" % json_data["CONFIG_DOTCONF_HW_VERSION"]

fw_version=json_data["CONFIG_DOTCONF_FW_VERSION"]
if settings.isFirmwareSupported(fw_version):
    print "FW version: %s" % fw_version
else:
    print "FW version %s not supported! Exiting!" % fw_version
    sys.exit(1)

encoder=settings.getEncoder(fw_version) 
if encoder== None :
    print "Cannot get encoder  for FW version %s ! Exiting!" % fw_version
    sys.exit(1)

# Run the encoder
lines=encoder.encode(json_data)

# print lines into the dot-config file
for line in lines:
    print >>config_fd, line

# close dot-config file
config_fd.close()


# the directory of the script being run
script_dir = os.path.dirname(os.path.abspath(__file__))
# find the abs path of dot-config file
config_file_abs = os.path.dirname(os.path.abspath(config_file)) + "/" \
				  + os.path.basename(config_file)
# set the path to Kconfig from particular FW release
kconfig_path = script_dir + "/kconfigs/v" + fw_version
# KCONFIG_CONFIG points to the dot-config file
verify_dot_config_env = os.environ.copy()
verify_dot_config_env["KCONFIG_CONFIG"] = config_file_abs
# Avoid creating temp file in the same dir as conf binary. When temp file and
# the destination file were in the different drives, conf failed to generate
# final config. As a side effect we don't keep .old file.
verify_dot_config_env["KCONFIG_OVERWRITECONFIG"] = "y"
verify_dot_config_command = "../../bin/conf --listnewconfig Kconfig"

process = subprocess.Popen(verify_dot_config_command.split(),
			   stdout=subprocess.PIPE,
			   stderr=subprocess.PIPE,
			   cwd=kconfig_path,
			   env=verify_dot_config_env)
output, error = process.communicate()

if error:
    print "Errors:"
    print error
    print ""
if output:
    print "Missing configuration items:"
    print output
    print ""

if (config_use_defaults != "yes" and (error or output)):
    print "Dot-config contains errors! Exiting!"
    sys.exit(1)

if (config_use_defaults == "yes"):
    verify_dot_config_command = "../../bin/conf -s --olddefconfig Kconfig"
    process = subprocess.Popen(verify_dot_config_command.split(),
			       stdout=subprocess.PIPE,
			       stderr=subprocess.PIPE,
			       cwd=kconfig_path,
			       env=verify_dot_config_env)
    output, error = process.communicate()
    if error:
	print "Errors:"
	print error
	print ""
    if output:
	print "Missing configuration items:"
	print output
	print ""
