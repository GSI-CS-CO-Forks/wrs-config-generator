#!/usr/bin/env python2.7

# Adam Wujek CERN 2017
#

import json
import requests
import base64
import sys, getopt
import getpass
import subprocess
import os
import time

# Supported FW versions
fw_version_supported = [
	"5.0",
	"5.0.1",
	"5.0-dev"
	]

# configuration items to skip
items_skip = {
	"5.0" : [
		"CONFIG_SNMP_SWCORESTATUS_HP_FRAME_RATE",
		"CONFIG_SNMP_SWCORESTATUS_RX_FRAME_RATE",
		"CONFIG_SNMP_SWCORESTATUS_RX_PRIO_FRAME_RATE"
		],
	"5.0.1" : [
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

# configuration items to add
items_add = {
	"5.0" : [
		"CONFIG_KEEP_ROOTFS=y",
		'CONFIG_BR2_CONFIGFILE="wrs_release_br2_config"',
		'CONFIG_ROOT_PWD_CLEAR=""'
		],
	"5.0.1" : [
		"CONFIG_KEEP_ROOTFS=y",
		'CONFIG_BR2_CONFIGFILE="wrs_release_br2_config"',
		'CONFIG_ROOT_PWD_CLEAR=""'
		],
	"5.0-dev" : [
		"CONFIG_KEEP_ROOTFS=y",
		'CONFIG_BR2_CONFIGFILE="wrs_release_br2_config"',
		'CONFIG_ROOT_PWD_CLEAR=""'
		],
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
	"5.0.1" : [
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

PORT_DB_range=range(1, 19) # 1..18
SFP_DB_range=range(0, 10) # 0..9
FIBER_DB_range=range(0, 4) # 0..3
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



def fill_vlans(config_fd, json_data):
    # enable VLANs
    print >>config_fd, "CONFIG_VLANS_ENABLE=y"
    fill_vlans_ports(config_fd, json_data)
    fill_vlans_vlan(config_fd, json_data)



def fill_vlans_ports(config_fd, json_data):
    for vlan_port_data in json_data["configVlanPorts"]:
	vlanPortMode = vlan_port_data["vlanPortMode"]

	if vlanPortMode == "access":
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_MODE_ACCESS=y" % int(vlan_port_data["portNumber"])

	    if vlan_port_data["vlanPortUntag"] == "true":
		print >>config_fd, "CONFIG_VLANS_PORT%02u_UNTAG_ALL=y" % int(vlan_port_data["portNumber"])
		print >>config_fd, "# CONFIG_VLANS_PORT%02u_UNTAG_NONE is not set" % int(vlan_port_data["portNumber"])
	    else:
		print >>config_fd, "CONFIG_VLANS_PORT%02u_UNTAG_NONE=y" % int(vlan_port_data["portNumber"])
		print >>config_fd, "# CONFIG_VLANS_PORT%02u_UNTAG_ALL is not set" % int(vlan_port_data["portNumber"])
	else:
	     print >>config_fd, "# CONFIG_VLANS_PORT%02u_MODE_ACCESS is not set" % int(vlan_port_data["portNumber"])

	if vlanPortMode == "trunk":
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_MODE_TRUNK=y" % int(vlan_port_data["portNumber"])
	else:
	     print >>config_fd, "# CONFIG_VLANS_PORT%02u_MODE_TRUNK is not set" % int(vlan_port_data["portNumber"])

	if vlanPortMode == "unqualified":
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_MODE_UNQUALIFIED=y" % int(vlan_port_data["portNumber"])
	else:
	     print >>config_fd, "# CONFIG_VLANS_PORT%02u_MODE_UNQUALIFIED is not set" % int(vlan_port_data["portNumber"])

	if vlanPortMode == "disabled":
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_MODE_DISABLED=y" % int(vlan_port_data["portNumber"])
	else:
	     print >>config_fd, "# CONFIG_VLANS_PORT%02u_MODE_DISABLED is not set" % int(vlan_port_data["portNumber"])


	if vlan_port_data["vlanPortPrio"] != None:
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_PRIO=%d" % (int(vlan_port_data["portNumber"]), int(vlan_port_data["vlanPortPrio"]))

	if vlan_port_data["vlanPortVid"] != None:
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_VID=\"%s\"" % (int(vlan_port_data["portNumber"]), vlan_port_data["vlanPortVid"])
	else:
	    print >>config_fd, "CONFIG_VLANS_PORT%02u_VID=\"\"" % int(vlan_port_data["portNumber"])

def fill_vlans_vlan(config_fd, json_data):
    VLANs_range = range(0, 4095) # 0..4094
    vlans_enable_set = {}

    if json_data["configVlans"] == []:
	for i in range(1, 4): # 1..3
	    print >>config_fd, "# CONFIG_VLANS_ENABLE_SET%u is not set" % i
	return
    
    for vlan_data in json_data["configVlans"]:
	vlan_conf_string = ""
	if vlan_data["vid"] == None:
	    # this should never happen...
	    print "Error: Vid not defined!"
	    continue

	if not (0 <= int(vlan_data["vid"]) <= 4094):
	    # this should never happen...
	    print "Error: Vid not in the range!"
	    continue

	if vlan_data["fid"] != None:
	    vlan_conf_string += "fid=%s," % vlan_data["fid"]
	if vlan_data["prio"] != None:
	    vlan_conf_string += "prio=%s," % vlan_data["prio"]
	if vlan_data["drop"] == "true":
	    vlan_conf_string += "drop=y,"
	if vlan_data["ports"] != None:
	    vlan_conf_string += "ports=%s," % vlan_data["ports"]

	# remove trailing comma if needed
	vlan_conf_string = vlan_conf_string.rstrip(',')
	print >>config_fd, "CONFIG_VLANS_VLAN%0004u=\"%s\"" % (int(vlan_data["vid"]), vlan_conf_string)

	# remove current vid from the list
	VLANs_range.remove(int(vlan_data["vid"]))

	if (0 <= int(vlan_data["vid"]) <= 22):
	    vlans_enable_set["1"] = "y"
	if (22 < int(vlan_data["vid"]) <= 100):
	    vlans_enable_set["2"] = "y"
	if (100 < int(vlan_data["vid"]) <= 4094):
	    vlans_enable_set["3"] = "y"

    # add empty vid entries if needed
    for i in VLANs_range:
	print >>config_fd, "CONFIG_VLANS_VLAN%0004u=\"\"" % i

    for i in range(1, 4): # 1..3
	if vlans_enable_set.has_key(str(i)):
	    print >>config_fd, "CONFIG_VLANS_ENABLE_SET%u=y" % i
	else:
	    print >>config_fd, "# CONFIG_VLANS_ENABLE_SET%u is not set" % i
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

url_ccde = 'https://ccde.cern.ch:9094/api/'
url_ccde_dev = 'https://ccde-dev.cern.ch:9094/api/'

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
print >>config_fd, "CONFIG_DOTCONF_HW_VERSION=\"%s\"" % json_data["CONFIG_DOTCONF_HW_VERSION"]

fw_version=json_data["CONFIG_DOTCONF_FW_VERSION"]
if fw_version in fw_version_supported:
    print "FW version: %s" % fw_version
else:
    print "FW version %s not supported! Exiting!" % fw_version
    sys.exit(1)
print >>config_fd, "CONFIG_DOTCONF_FW_VERSION=\"%s\"" % json_data["CONFIG_DOTCONF_FW_VERSION"]

# get the current time
gen_time = time.strftime("%Y-%m-%d+%H:%M:%S")
dotconf_info = "gen_time=%s;" % gen_time

if "requestedByUser" in json_data:
    gen_user = json_data["requestedByUser"]
    dotconf_info+="gen_user=%s;" % gen_user

print "dotconf_info: %s" % dotconf_info 
print >>config_fd, "CONFIG_DOTCONF_INFO=\"%s\"" % dotconf_info

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
    port_id = int(port_item["portNumber"])
    # check the range of ports
    if not (1 <= port_id <= 18):
	print "Error: Port " + port_item["portNumber"] + " out of range!"
	continue

    # remove current port id from the list
    PORT_DB_range.remove(port_id)
    print >>config_fd, "CONFIG_PORT%02u_PARAMS=\"name=wri%u,proto=%s,tx=%u,rx=%u,role=%s,fiber=%s\""	% (
	port_id,
	port_id,
	port_item["proto"],
	int(port_item["dtx"]),
	int(port_item["drx"]),
	port_item["ptpRole"],
	port_item["fiber"]
	)

# add empty port entries if needed
for i in PORT_DB_range:
    print >>config_fd, "CONFIG_PORT%02u_PARAMS=\"\"" % (i)


# Add CONFIG_SFP00_PARAMS
for sfp_item in json_data["configSfp"]:
    sfp_id = int(sfp_item["sfpId"])
    sfp_entry = ""
    # check the range of sfps
    if not (0 <= sfp_id <= 9):
	print "Error: Port " + sfp_item["sfpId"] + " out of range!"
	continue
    # remove current sfp id from the list
    SFP_DB_range.remove(sfp_id)
    sfp_entry = "CONFIG_SFP%02u_PARAMS=\"vn=%s,pn=%s," % (
	sfp_id,
	sfp_item["vendorName"],
	sfp_item["partNumber"],
	)
    if (sfp_item["vendorSerial"] != None):
	sfp_entry += "vs=%s," % (sfp_item["vendorSerial"])
    sfp_entry += "tx=%u,rx=%u,wl_txrx=%s\"" % (
	int(sfp_item["dtx"]),
	int(sfp_item["drx"]),
	sfp_item["wavelength"]
	)
    print >>config_fd, sfp_entry
# add empty sfp entries if needed
for i in SFP_DB_range:
    print >>config_fd, "CONFIG_SFP%02u_PARAMS=\"\"" % (i)


# Add CONFIG_SFP00_PARAMS
for fiber_item in json_data["configFibers"]:
    fiber_id = int(fiber_item["fiberId"])
    # check the range of fibers
    if not (0 <= fiber_id <= 3):
	print "Error: Port " + fiber_item["fiberId"] + " out of range!"
	continue
    # remove current fiber id from the list
    FIBER_DB_range.remove(fiber_id)
    print >>config_fd, "CONFIG_FIBER%02u_PARAMS=\"alpha_%s=%s\"" % (
	fiber_id,
	fiber_item["waveLength"],
	fiber_item["alpha"],
	)

# add empty fiber entries if needed
for i in FIBER_DB_range:
    print >>config_fd, "CONFIG_FIBER%02u_PARAMS=\"\"" % (i)

# VLANs
fill_vlans(config_fd, json_data)

# Add items from items_add
for extra_item in items_add[fw_version]:
    print >>config_fd, "%s" % (extra_item)

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
