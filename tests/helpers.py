from dataclasses import dataclass
import tempfile
import sys

from dotconfig import DotConfig
sys.path.insert(0, "..")
from generate_config import generate


# Switch port constants
PORTS_COUNT = 18
PORTS_RANGE = range(1, PORTS_COUNT + 1)


@dataclass
class GenerateArgs:     # only arguments used by generate() function
    config_file: str
    config_use_defaults: bool


def execute_generate(json_data, use_defaults=True):
    """ Generates a dotconfig file using specific JSON data """
    config_file = tempfile.NamedTemporaryFile().name
    generate(GenerateArgs(config_file, use_defaults), json_data)
    return DotConfig.from_file(config_file)


def dump_lines(filename, lines):
    """ Saves an array of text lines to a file """
    with open(filename, "w") as output:
        for l in lines:
            output.write("{0}\n".format(l))


def json_set_item(json_data, item_name, value):
    """ Modifies an entry in configurationItems section of JSON data """
    for item in json_data["configurationItems"]:
        if item["itemConfig"] == item_name:
            item["itemValue"] = value
            return

    raise RuntimeError("Item {0} not found".format(item_name))


def json_set_port(json_data, port_nr, attribute, value):
    """ Modifies a port attribute in JSON data """
    if port_nr not in PORTS_RANGE:
        raise RuntimeError("Invalid port number")

    port_data = json_data["configPorts"][port_nr - 1]
    assert(port_data["portNumber"] == str(port_nr))
    assert(attribute in port_data)
    port_data[attribute] = str(value)
