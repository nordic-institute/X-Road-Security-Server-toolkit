"""Module for getting project version"""
from cement.utils.version import get_version as cement_get_version

current_version = "0.0.2-alpha.0"


def convert_version(version_str):
    version_parts = version_str.split(sep=".")
    major = version_parts[0].split(".")[0]
    minor = version_parts[0].split(".")[1]
    patch = version_parts[0].split(".")[2]
    release = version_parts[1].split(".")[0]
    build = version_parts[1].split(".")[1]
    version = (major, minor, patch, release, build)
    return version


VERSION = convert_version(current_version)


def get_version(version=VERSION):
    """Function for getting project version"""
    return cement_get_version(version)
