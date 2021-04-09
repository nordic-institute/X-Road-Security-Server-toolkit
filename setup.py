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
        'cement',
        'pyyaml',
        'networkx',
        'tabulate',
        'setuptools',
        'urllib3',
        'confuse',
        'certifi',
        'six',
        'gitpython',
        'docker',
        'yq',
        'jq',
        'requests',
        'python-dateutil'
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
