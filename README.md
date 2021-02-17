# X-Road Security Server Toolkit

## About the repository 

This repository contains information about the X-Road Security Server Toolkit, source code, its development, installation and documentation.

## X-Road Security Server Toolkit source code

[Source code](https://github.com/nordic-institute/X-Road-Security-Server-toolkit) of X-Road Security Server Toolkit is open for all and it is licenced under MIT licence.

## Introduction to X-Road Security Server Toolkit

User Guide [X-Road Security Server Toolkit User Guide](https://github.com/nordic-institute/X-Road-Security-Server-toolkit/docs/xroad_security_server_toolkit_user_guide.md)


## Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

## Testing

In order to run unit tests with code coverage the following target in the `Makefile` should be run:
```
$ make test

```

In order to run unit tests with integration tests the following target in the `Makefile` should be run:
```
$ make test-all

```

End to end tests are run using the following script:
```
$ run_end_to_end_tests.sh

More details about the required input parameters are provided in the script file
```

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate

```

### Updating project version

* Update patch/minor/major/releaae/build (major.minor.patch-release.build)
```
$ bump2version patch/minor/major/release/build (e.g. bump2version minor)
```

### Releasing

Use the included helper function via the `Makefile`:

```
$ make dist
```

## Deployments

### Docker

Included is a basic `Dockerfile` for building and distributing `X-Road Security Server Toolkit`,
and can be built with the included `make` helper:

```
$ make docker

$ docker run -it xrdsst --help
```
