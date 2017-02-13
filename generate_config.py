#!/usr/bin/env python2.7

import json
import requests
import base64
import sys, getopt
import getpass
import subprocess
import os

# Supported FW versions
fw_version_supported = [
	"5.0",
	"5.0-dev"
	]

# configuration items to skip
items_skip = {
	"5.0" : [
		"CONFIG_SNMP_SWCORESTATUS_HP_FRAME_RATE",
		"CONFIG_SNMP_SWCORESTATUS_RX_FRAME_RATE",
		"CONFIG_SNMP_SWCORESTATUS_RX_PRIO_FRAME_RATE"
		],
	"5.0-dev" : [
		"CONFIG_SNMP_SWCORESTATUS_HP_FRAME_RATE",
		"CONFIG_SNMP_SWCORESTATUS_RX_FRAME_RATE",
		"CONFIG_SNMP_SWCORESTATUS_RX_PRIO_FRAME_RATE"
		]
	}

# configuration items to convert from string to int
items_conv_num = {
	"5.0" : [
		"CONFIG_SNMP_TEMP_THOLD_FPGA",
		"CONFIG_SNMP_TEMP_THOLD_PLL",
		"CONFIG_SNMP_TEMP_THOLD_PSL",
		"CONFIG_SNMP_TEMP_THOLD_PSR",
		"CONFIG_NIC_THROTTLING_VAL",
		"CONFIG_FAN_HYSTERESIS_T_ENABLE",
		"CONFIG_FAN_HYSTERESIS_T_DISABLE",
		"CONFIG_FAN_HYSTERESIS_PWM_VAL"
		],
	"5.0-dev" : [
		"CONFIG_SNMP_TEMP_THOLD_FPGA",
		"CONFIG_SNMP_TEMP_THOLD_PLL",
		"CONFIG_SNMP_TEMP_THOLD_PSL",
		"CONFIG_SNMP_TEMP_THOLD_PSR",
		"CONFIG_NIC_THROTTLING_VAL",
		"CONFIG_FAN_HYSTERESIS_T_ENABLE",
		"CONFIG_FAN_HYSTERESIS_T_DISABLE",
		"CONFIG_FAN_HYSTERESIS_PWM_VAL"
		]

	}

# -----------------------------------------------------------------------------

def print_help(prog_name):
    print """
    Usage:
    """ + prog_name + """ --json=<file> [--config=<file>] [--use-defaults]
    """ + prog_name + """ <--ccde|--ccde-dev> --dev=<name> --user=<user> [--password=<password>] [--ccde-out=<file>] [--config=<file>] [--use-defaults]

    Options:
    --json=<file>		Get the data directly from file
    --ccde			Get the data from the CCDE
    --ccde-dev			Get the data from the dev version of CCDE
    --ccde-out=<file>		Save data from CCDE to the file. Requires ccde or ccde-dev to be used
    --user=<user>		User to CCDE. If not specified system username will be used.
    --password=<password>	Password to CCDE. If not provided it will be prompted.
    --config=<file>		Save generated dot-config in the file. By default in the file "dot-config".
    --dev=<name>		Specify device name
    --use-defaults		Use defaults for configuration items not defined in json/CCDE
    """

def get_data_ccde(wrs_name, url, user, password):
    authData = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
    s = requests.Session()
    s.post(url + 'login', data={'authentication':authData}, verify=False)
    r = s.get(url + 'switches/' + wrs_name + '/configuration', verify=False)
    return r.text



# -----------------------------------------------------------------------------

inputfile = ''
outputfile = ''
ccde_url = ''
ccde_user = ''
ccde_password = ''
config_file = "dot-config"
ccde_json_file = ''
ccde_dev_name = ''
file_json_in = ''
config_use_defaults = 'no'

url_ccde = 'https://ccde.cern.ch:9094/api/'
url_ccde_dev = 'https://ccde-dev.cern.ch:9094/api/'

try:
    opts, args = getopt.getopt(sys.argv[1:],"h",
			       ["help", "ccde", "ccde-dev", "json=", "config=",
				"ccde-out=", "user=", "password=", "dev=",
				"use-defaults"])
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
	ccde_url = 'https://ccde.cern.ch:9094/api/'
    elif opt == "--ccde-dev":
	ccde_url = 'https://ccde-dev.cern.ch:9094/api/'
    elif opt == "--json":
	file_json_in = arg
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
    elif opt == "--use-defaults":
	config_use_defaults = "yes"
    else:
	print "unknown parameter" + opt

if (ccde_url != '') and (file_json_in != ''):
    print "Please specify only one --ccde[-dev] or --json"
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

config_fd = open(config_file, 'w')
print "Saving dot-config to a file: " + config_file

if not ("switchName" in json_data):
    print "Switch %s does not exist in DB" % ccde_dev_name
    sys.exit(1)

print "Switch name %s" % json_data["switchName"]
print "HW version: %s" % json_data["CONFIG_DOTCONF_HW_VERSION"]
print >>config_fd, "CONFIG_DOTCONF_HW_VERSION=\"%s\"" % json_data["CONFIG_DOTCONF_HW_VERSION"]

fw_version=json_data["CONFIG_DOTCONF_FW_VERSION"]
if fw_version in fw_version_supported:
    print "FW version: %s" % fw_version
else:
    print "FW version %s not supported! Exiting!" % fw_version
    sys.exit(1)
print >>config_fd, "CONFIG_DOTCONF_FW_VERSION=\"%s\"" % json_data["CONFIG_DOTCONF_FW_VERSION"]

for config_item in json_data["configurationItems"]:
    if ((fw_version in items_skip) and (config_item["itemConfig"] in items_skip[fw_version])):
	# skip configuration item
	continue
    elif config_item["itemValue"] == "true":
	print >>config_fd, "%s=y" % config_item["itemConfig"]
    elif config_item["itemValue"] == "false":
	print >>config_fd, "# %s is not set" % config_item["itemConfig"]
    elif config_item["itemValue"] == None:
	continue
    elif ((fw_version in items_conv_num) and (config_item["itemConfig"] in items_conv_num[fw_version])):
	print >>config_fd, "%s=%u" % (config_item["itemConfig"], int(config_item["itemValue"]))
    else:
	print >>config_fd, "%s=\"%s\"" % (config_item["itemConfig"], config_item["itemValue"])

# Add CONFIG_PORTXX_PARAMS
for port_item in json_data["configPorts"]:
    # check the range of ports
    if not (1 <= int(port_item["portNumber"]) <= 18):
	print "Error: Port " + port_item["portNumber"] + " out of range!"
	continue
    print >>config_fd, "CONFIG_PORT%02u_PARAMS=\"name=wri%u,proto=%s,tx=%u,rx=%u,role=%s,fiber=%s\""	% (
	int(port_item["portNumber"]),
	int(port_item["portNumber"]),
	port_item["proto"],
	int(port_item["dtx"]),
	int(port_item["drx"]),
	port_item["ptpRole"],
	port_item["fiber"]
	)
# Add CONFIG_SFP00_PARAMS
for sfp_item in json_data["configSfp"]:
    # check the range of sfps
    if not (0 <= int(sfp_item["sfpId"]) <= 9):
	print "Error: Port " + sfp_item["sfpId"] + " out of range!"
	continue
    print >>config_fd, "CONFIG_SFP%02u_PARAMS=\"vs=%s,pn=%s," % (
	int(sfp_item["sfpId"]),
	sfp_item["vendorName"],
	sfp_item["partNumber"],
	),
    if (sfp_item["vendorSerial"] != None):
	print >>config_fd, "vs=%s," % (sfp_item["vendorSerial"]),
    print >>config_fd, "tx=%u,rx=%u,wl_txrx=%s\"" % (
	int(sfp_item["dtx"]),
	int(sfp_item["drx"]),
	sfp_item["wavelengths"]
	)
# Add CONFIG_SFP00_PARAMS
for fiber_item in json_data["configFibers"]:
    # check the range of fibers
    if not (0 <= int(fiber_item["fiberId"]) <= 3):
	print "Error: Port " + fiber_item["fiberId"] + " out of range!"
	continue
    print >>config_fd, "CONFIG_FIBER%02u_PARAMS=\"alpha_%s=%s\"" % (
	int(fiber_item["fiberId"]),
	fiber_item["waveLength"],
	fiber_item["alpha"],
	)

# close dot-config file
config_fd.close()

# the directory of the script being run
script_dir = os.path.dirname(os.path.abspath(__file__))

# set the path to Kconfig from particular FW release
kconfig_path = script_dir + "/kconfigs/v" + fw_version
# KCONFIG_CONFIG points to the dot-config file
verify_dot_config_env = os.environ.copy()
verify_dot_config_env["KCONFIG_CONFIG"] = "../../" + config_file
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
