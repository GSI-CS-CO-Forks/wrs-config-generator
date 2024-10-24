from enum import Enum
from typing import Any
from dataclasses import dataclass

class ValueType(Enum):
    """ Value types supported by dotconfig files """
    NOT_SET = 0
    BOOL = 1
    INT = 2
    STRING = 3


@dataclass
class Entry:
    """ Represents one configuration line in a dotconfig file """
    #name: str
    value: Any
    type: ValueType


class DotConfig:
    """ Simple dotconfig parser with a dict-like interface """
    def __init__(self):
        self._entries = {}


    @staticmethod
    def from_lines(lines):
        new_obj = DotConfig()

        for line in lines:
            new_obj._process_line(line.strip())

        return new_obj


    @staticmethod
    def from_file(filename):
        new_obj = DotConfig()

        with open(filename, "r") as dotconfig_file:
            for line in dotconfig_file:
                new_obj._process_line(line.strip())

        return new_obj


    def _process_line(self, line):
        if len(line) == 0:
            return

        if line[0] == '#':  # either a regular comment or "is not set"
            if line.endswith('is not set'):
                name = line.split(' ')[1]
                assert(name.startswith('CONFIG_'))
                assert(name not in self._entries)
                self._entries[name] = Entry(None, ValueType.NOT_SET)

        else:               # regular CONFIG_xxx=value line
            split = line.find('=')
            name = line[:split]
            value = line[split + 1:]
            assert(name.startswith('CONFIG_'))
            assert(name not in self._entries)

            if value[0] == value[-1] == '"':
                self._entries[name] = Entry(value[1:-1], ValueType.STRING)
            elif len(value) == 1 and (value[0] == 'y' or value[0] == 'n'):
                self._entries[name] = Entry(value == 'y', ValueType.BOOL)
            else:
                self._entries[name] = Entry(int(value), ValueType.INT)


    def is_set(self, name):
        return name in self._entries and self._entries[name].type != ValueType.NOT_SET


    def __getitem__(self, key):
        return self._entries[key]


    def __contains__(self, key):
        return key in self._entries


    def __len__(self):
        return len(self._entries)


    def values(self):
        return self._entries.values()


    def items(self):
        return self._entries.items()
