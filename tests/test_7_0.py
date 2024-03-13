import pytest
import json
import sys

from helpers import *
sys.path.insert(0, "..")
import settings

SW_VERSION = "7.0"

@pytest.fixture
def json_data():
    with open("test_{0}.json".format(SW_VERSION), "r") as f:
        data = json.load(f)
    assert data["CONFIG_DOTCONF_FW_VERSION"] == SW_VERSION
    return data


@pytest.fixture
def encoder():
    encoder = settings.getEncoder(SW_VERSION)
    return encoder


def test_timing_gm(encoder, json_data):
    """ Timing mode set to grandmaster """
    json_set_item(json_data, "CONFIG_TIME_GM", "true")
    json_set_item(json_data, "CONFIG_TIME_BC", "false")
    json_set_item(json_data, "CONFIG_TIME_FM", "false")

    dotconfig = execute_generate(json_data)

    assert(dotconfig["CONFIG_TIME_GM"].value == True)
    assert(dotconfig["CONFIG_TIME_BC"].value == None)
    assert(dotconfig["CONFIG_TIME_FM"].value == None)

    # Options dependent on the timing mode
    assert(dotconfig["CONFIG_PTP_OPT_TIME_SOURCE_VAL"].value == 0x20)
    assert(dotconfig["CONFIG_PTP_OPT_CLOCK_CLASS_VAL"].value == 6)


def test_timing_bc(encoder, json_data):
    """ Timing mode set to boundary clock """
    json_set_item(json_data, "CONFIG_TIME_GM", "false")
    json_set_item(json_data, "CONFIG_TIME_BC", "true")
    json_set_item(json_data, "CONFIG_TIME_FM", "false")

    dotconfig = execute_generate(json_data)

    assert(dotconfig["CONFIG_TIME_GM"].value == None)
    assert(dotconfig["CONFIG_TIME_BC"].value == True)
    assert(dotconfig["CONFIG_TIME_FM"].value == None)

    # Options dependent on the timing mode
    assert(dotconfig["CONFIG_PTP_OPT_TIME_SOURCE_VAL"].value == 0xa0)
    assert(dotconfig["CONFIG_PTP_OPT_CLOCK_CLASS_VAL"].value == 248)


def test_timing_fm(encoder, json_data):
    """ Timing mode set to free-running master """
    json_set_item(json_data, "CONFIG_TIME_GM", "false")
    json_set_item(json_data, "CONFIG_TIME_BC", "false")
    json_set_item(json_data, "CONFIG_TIME_FM", "true")

    dotconfig = execute_generate(json_data)

    assert(dotconfig["CONFIG_TIME_GM"].value == None)
    assert(dotconfig["CONFIG_TIME_BC"].value == None)
    assert(dotconfig["CONFIG_TIME_FM"].value == True)

    # Options dependent on the timing mode
    assert(dotconfig["CONFIG_PTP_OPT_TIME_SOURCE_VAL"].value == 0xa0)
    assert(dotconfig["CONFIG_PTP_OPT_CLOCK_CLASS_VAL"].value == 193)


def test_ext_port_cfg_enable(encoder, json_data):
# TODO add more test cases (different port setups)
    for i in PORTS_RANGE:
        if i == 1:
            role = "slave"
        else:
            role = "master"

        json_set_port(json_data, i, "ptpRole", role)

    dotconfig = execute_generate(json_data)

    assert(dotconfig["CONFIG_PTP_OPT_BMCA_STANDARD"].value == None)
    assert(dotconfig["CONFIG_PTP_OPT_BMCA_EXT_PORT_CONFIG"].value == True)


def test_ext_port_cfg_disable(encoder, json_data):
    for i in PORTS_RANGE:
        json_set_port(json_data, i, "ptpRole", "slave")

    dotconfig = execute_generate(json_data)

    assert(dotconfig["CONFIG_PTP_OPT_BMCA_STANDARD"].value == True)
    assert(dotconfig["CONFIG_PTP_OPT_BMCA_EXT_PORT_CONFIG"].value == None)


def test_ptp_role_master(encoder, json_data):
    for port in PORTS_RANGE:
        json_set_port(json_data, port, "ptpRole", "master")

        dotconfig = execute_generate(json_data)

        cfg_prefix = "CONFIG_PORT{0:02}".format(port)
        assert(dotconfig["{0}_INSTANCE_COUNT_0".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INSTANCE_COUNT_1".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_PROFILE_PTP".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INST01_PROFILE_HA_WR".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_EXTENSION_WR".format(cfg_prefix)].value == True)
        # TODO these options depend on ext_port_cfg (1 slave port, all other ports are masters)
        # assert(dotconfig["{0}_INST01_DESIRADE_STATE_MASTER".format(cfg_prefix)].value == True)
        # assert(dotconfig["{0}_INST01_DESIRADE_STATE_SLAVE".format(cfg_prefix)].value == None)


def test_ptp_role_slave(encoder, json_data):
    for port in PORTS_RANGE:
        json_set_port(json_data, port, "ptpRole", "slave")

        dotconfig = execute_generate(json_data)

        cfg_prefix = "CONFIG_PORT{0:02}".format(port)
        assert(dotconfig["{0}_INSTANCE_COUNT_0".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INSTANCE_COUNT_1".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_PROFILE_PTP".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INST01_PROFILE_HA_WR".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_EXTENSION_WR".format(cfg_prefix)].value == True)


def test_ptp_role_non_wr(encoder, json_data):
    for port in PORTS_RANGE:
        json_set_port(json_data, port, "ptpRole", "non-wr")

        dotconfig = execute_generate(json_data)

        cfg_prefix = "CONFIG_PORT{0:02}".format(port)
        assert(dotconfig["{0}_INSTANCE_COUNT_0".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INSTANCE_COUNT_1".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_PROFILE_PTP".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INST01_PROFILE_HA_WR".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_EXTENSION_WR".format(cfg_prefix)].value == True)


def test_ptp_role_ptp(encoder, json_data):
    for port in PORTS_RANGE:
        json_set_port(json_data, port, "ptpRole", "ptp")

        dotconfig = execute_generate(json_data)

        cfg_prefix = "CONFIG_PORT{0:02}".format(port)
        assert(dotconfig["{0}_INSTANCE_COUNT_0".format(cfg_prefix)].value == None)
        assert(dotconfig["{0}_INSTANCE_COUNT_1".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_PROFILE_PTP".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INST01_PROFILE_HA_WR".format(cfg_prefix)].value == None)


def test_ptp_role_none(encoder, json_data):
    for port in PORTS_RANGE:
        json_set_port(json_data, port, "ptpRole", "none")

        dotconfig = execute_generate(json_data)

        cfg_prefix = "CONFIG_PORT{0:02}".format(port)
        assert(dotconfig["{0}_INSTANCE_COUNT_0".format(cfg_prefix)].value == True)
        assert(dotconfig["{0}_INSTANCE_COUNT_1".format(cfg_prefix)].value == None)


# TODO protocol
# TODO vlans
