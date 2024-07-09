#!/usr/bin/python3
# Adam Wujek,      CERN, 2017
# Jean-Claude Bau, CERN, 2019
# Maciej Suminski, CERN, 2024

import sys
import subprocess
import os
import settings


def generate(args, json_data):
    config_fd = open(args.config_file, 'w')
    print ("Saving dot-config to a file: %s" % args.config_file)

    if not ("switchName" in json_data):
        raise RuntimeError("Switch %s does not exist in DB" % args.ccde_dev_name)

    print ("Switch name %s" % json_data["switchName"])
    print ("HW version: %s" % json_data["CONFIG_DOTCONF_HW_VERSION"])

    fw_version = args.fw_version if args.fw_version is not None \
                    else json_data["CONFIG_DOTCONF_FW_VERSION"]
    if settings.isFirmwareSupported(fw_version):
        print ("FW version: %s" % fw_version)
    else:
        raise RuntimeError("FW version %s not supported" % fw_version)

    encoder = settings.getEncoder(fw_version)
    if encoder == None:
        raise RuntimeError("Cannot get encoder for FW version %s" % fw_version)

    # Run the encoder
    lines = encoder.encode(json_data)

    # print lines into the dot-config file
    for line in lines:
        config_fd.write("%s\n" % line)

    # close dot-config file
    config_fd.close()


    # the directory of the script being run
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # find the abs path of dot-config file
    config_file_abs = os.path.dirname(os.path.abspath(args.config_file)) + "/" \
                    + os.path.basename(args.config_file)
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
        print ("Errors:\n%s\n" % error.decode('ascii'))
    if output:
        print ("Missing configuration items 1:\n%s\n" % output.decode('ascii'))

    if (not args.config_use_defaults and (error or output)):
        raise RuntimeError("Dot-config contains errors")

    if args.config_use_defaults:
        verify_dot_config_command = "../../bin/conf -s --olddefconfig Kconfig"
        process = subprocess.Popen(verify_dot_config_command.split(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=kconfig_path,
                                env=verify_dot_config_env)
        output, error = process.communicate()

        if error:
            print ("Errors:\n%s\n" % error.decode('ascii'))
        if output:
            print ("Missing configuration items 2:\n%s\n" % output.decode('ascii'))


if __name__ == '__main__':
    import requests
    import base64
    import json
    import getpass
    import argparse

    #URL_CCDE = 'https://ccde.cern.ch:9094/api/'
    URL_CCDE = 'https://ccde.cern.ch/api/'
    URL_CCDE_DEV = 'https://ccde-dev.cern.ch/api/'

    script_dir = os.path.dirname(os.path.abspath(__file__)) # script location directory
    try:
        version = os.popen("cd " + script_dir + "; git describe --always --dirty").read().strip()
    except:
        version = 'unknown'

    parser = argparse.ArgumentParser('WR Switch dot-config generator (version %s)' % version)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--ccde', action='store_const', const=URL_CCDE, dest='ccde_url',
            help='Get the JSON data from the CCDE.')
    input_group.add_argument('--ccde-dev', action='store_const', const=URL_CCDE_DEV, dest='ccde_url',
            help='Get the JSON data from the dev version of CCDE.')
    input_group.add_argument('--json', action='store', dest='file_json_in',
            help='Get the JSON data from file.')
    input_group.add_argument('--stdin', action='store_true', dest='json_stdin',
            help='Get the JSON data from stdin.')
    parser.add_argument('--ccde-out', action='store', dest='ccde_json_file',
            help='Save data from CCDE to the file. Requires ccde or ccde-dev to be used.')
    parser.add_argument('--user', action='store', dest='ccde_user',
            help='CCDE user. If not specified, system username will be used.')
    parser.add_argument('--password', action='store', dest='ccde_password',
            help='CCDE password. If not provided it will be prompted.' )
    parser.add_argument('--config', action='store', dest='config_file', default='dot-config',
            help='Save generated dot-config in the file.')
    parser.add_argument('--dev', action='store', dest='ccde_dev_name',
            help='Specify device name')
    parser.add_argument('--fw-version', action='store', dest='fw_version',
            help='Enforces a specific firmware version')
    parser.add_argument('--no-use-defaults', action='store_false', dest='config_use_defaults',
            help='Do not use defaults for configuration items not defined in JSON/CCDE.')
    args = parser.parse_args()


    def get_data_ccde(wrs_name, url, user, password):
        authData = base64.b64encode('{0}:{1}'.format(user, password).encode('ascii'))
        s = requests.Session()
        s.post(url + 'acw/login', data={'authentication':authData}, verify=False)
        r = s.get(url + 'whiterabbit/switches/' + wrs_name + '/configuration', verify=False)
        return r.text


    # Get data from CCDE
    if args.ccde_url is not None:
        if args.ccde_dev_name is None:
            print ("Please specify device name for CCDE access")
            sys.exit(1)
        if args.ccde_user is None:
            args.ccde_user = getpass.getuser()
            print ("Using system username for CCDE: %s" % args.ccde_user)
        if args.ccde_password is None:
            args.ccde_password = getpass.getpass("Password for user %s to access CCDE:" % args.ccde_user)

        ccde_data = get_data_ccde(args.ccde_dev_name, args.ccde_url, args.ccde_user, args.ccde_password)

        if args.ccde_json_file is not None:
            print ("Save CCDE data to file: %s" % args.ccde_json_file)
            ccdb_json_file_out = open(args.ccde_json_file, 'w')
            ccdb_json_file_out.write(ccde_data)
            ccdb_json_file_out.close()
        try:
            json_data = json.loads(ccde_data)
        except ValueError:
            print ("ERROR: Unable to get valid json data from CCDE.")
            if args.ccde_json_file is not None:
                print ("Please check the file for CCDE response %s" % args.ccde_json_file)
            else:
                print ("Please use parameter --ccde-out check the file for CCDE response %s" % args.ccde_json_file)
            sys.exit(1)

    # Get data from local file
    if args.file_json_in is not None:
        print ("Reading data from file: %s" % args.file_json_in)
        with open(args.file_json_in) as data_file:
            try:
                json_data = json.load(data_file)
            except ValueError:
                print ("Error: Syntax error in file: " + args.file_json_in)
                sys.exit(1)
        data_file.close()

    # Get data from stdin
    if args.json_stdin:
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
            print ("Error: Syntax error in stdin data")
            sys.exit(1)

    try:
        generate(args, json_data)
    except RuntimeError as e:
        print ("Error: {0}".format(e))
