import re


def get_version():
    with open("semantic_release/__init__.py", "r") as fd:
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
        ).group(1)
    return version
