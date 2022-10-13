# X-Road Security Server Toolkit

[![Go to X-Road Community Slack](https://img.shields.io/badge/Go%20to%20Community%20Slack-grey.svg)](https://jointxroad.slack.com/)
[![Get invited](https://img.shields.io/badge/No%20Slack-Get%20invited-green.svg)](https://x-road.global/community)

## About the repository 

This repository contains information about the X-Road Security Server Toolkit, source code, its development, installation and documentation.

## X-Road Security Server Toolkit source code

[Source code](https://github.com/nordic-institute/X-Road-Security-Server-toolkit) of X-Road Security Server Toolkit is open for all and it is licenced under MIT licence.

## Introduction to X-Road Security Server Toolkit

[X-Road Security Server Toolkit User Guide](https://github.com/nordic-institute/X-Road-Security-Server-toolkit/blob/master/docs/xroad_security_server_toolkit_user_guide.md)


## Installing the latest development version from GitHub

**Prerequisites to Installation**

* Ubuntu 18.04 LTS or 20.04 LTS
* Python version 3.6+
* apt-get update needs to be run before installing
* PIP 21.0+
  - apt install -y python3-pip
  - python3 -m pip install --upgrade pip
  - pip3 install cement
* Installed X-Road security server packages on target machine(s)

**Installation is performed with pip (use pip or pip3, whichever is used)**

```bash
$ git clone https://github.com/nordic-institute/X-Road-Security-Server-toolkit.git

$ cd X-Road-Security-Server-toolkit

$ pip3 install -r requirements.txt

$ python3 setup.py install
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

## Testing

In order to run unit tests with code coverage the following target in the `Makefile` should be run:

```bash
$ make test

```

In order to run unit tests with integration tests the following target in the `Makefile` should be run:

```bash
$ make test-all

```

End to end tests are run using the following script:

```bash
$ run_end_to_end_tests.sh

```

More details about the required input parameters are provided in the script file

### Environment Setup

The following demonstrates setting up and working with a development environment:

```bash
### create a virtualenv for development

$ pip3 install virtualenv

$ make virtualenv

$ source env/bin/activate

```

### Project versioning

Pre-release:

```bash
$ 0.x.x-alpha.0
```

First release:

```bash
$ 1.0.0-final.0
```

Post first release:

```bash
$ 1.x.x-beta.0
```


### Updating project version

* Update patch/minor/major/release/build (major.minor.patch-release.build)

```bash
$ bump2version patch/minor/major/release/build (e.g. bump2version minor)
```

In case of minor updates, use `bump2version patch`
In case of major updates, use `bump2version minor`
When releasing, use `bump2version major`

In case of releasing, also `bump2version release` should be performed
to update the release part of the version number, which can contain values: 

* `beta`
* `final`

### Releasing

Use the included helper function via the `Makefile`:

```bash
$ make dist
```
