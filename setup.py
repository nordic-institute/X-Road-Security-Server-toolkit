
from setuptools import setup, find_packages
from sstoolkit.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='sstoolkit',
    version=VERSION,
    description='A toolkit for configuring security server',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Bert Viikmäe',
    author_email='bert.viikmae@gofore.com',
    url='https://github.com/bertvi/sstoolkit',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'sstoolkit': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        sstoolkit = sstoolkit.main:main
    """,
)
