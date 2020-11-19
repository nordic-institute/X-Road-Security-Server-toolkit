import sys
from setuptools import setup, find_packages
from semantic_release import setup_hook, version


f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

try:
    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='xrdsst',
    version=version.get_version(),
    description='A toolkit for configuring X-Road Security Server',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Bert Viikmäe',
    author_email='bert.viikmae@gofore.com',
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
