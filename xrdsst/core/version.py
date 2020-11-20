"""Module for getting project version"""
from cement.utils.version import get_version as cement_get_version

VERSION = (0, 1, 4, 'alpha', 0)


def get_version(version=VERSION):
    """Function for getting project version"""
    return cement_get_version(version)
