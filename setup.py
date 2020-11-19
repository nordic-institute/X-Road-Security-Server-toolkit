import sys

from setuptools import setup, find_packages
from xrdsst.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='xrdsst',
    version=VERSION,
    description='A toolkit for configuring X-Road Security Server',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Bert Viikmäe',
    author_email='bert.viikmae@gofore.com',
    url='https://github.com/nordic-institute/X-Road-Security-Server-toolkit',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'xrdsst': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        xrdsst = xrdsst.main:main
    """,
)
