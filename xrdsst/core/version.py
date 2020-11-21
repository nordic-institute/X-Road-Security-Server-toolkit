"""Module for getting project version"""
from cement.utils.version import get_version as cement_get_version

current_version = "0.1.5-dev0"


def convert_version(current_version):
    return 0, 1, 4, 'alpha', 0


VERSION = convert_version(current_version)


def get_version(version=VERSION):
    """Function for getting project version"""
    return cement_get_version(version)
