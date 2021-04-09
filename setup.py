"""Project setup"""
from setuptools import setup, find_packages
from xrdsst.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='xrdsst',
    version=VERSION,
    description='A toolkit for configuring X-Road Security Server',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=[],
    install_requires=[
        'cement==3.0.4',
        'pyyaml~=5.3.1',
        'networkx~=2.5',
        'tabulate~=0.8.7',
        'setuptools~=45.2.0',
        'urllib3~=1.25.8',
        'confuse~=1.3.0',
        'certifi >= 14.05.14',
        'six >= 1.10',
        'pytest~=6.1.1',
        'pylint~=2.6.0',
        'pytest-pylint~=0.18.0',
        'bump2version~=1.0.1',
        'gitpython~=3.1.11',
        'docker~=4.1.0',
        'yq~=2.11.1',
        'jq~=1.1.1',
        'requests~=2.22.0',
        'python-dateutil~=2.8.1'
    ],
    author='Finnish Digital Agency',
    author_email='info@dvv.fi',
    url='https://github.com/nordic-institute/X-Road-Security-Server-toolkit',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'xrdsst': ['templates/*']},
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
    include_package_data=True,
    entry_points="""
        [console_scripts]
        xrdsst = xrdsst.main:main
    """,
)
