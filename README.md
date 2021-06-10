# X-Road Security Server Toolkit

## About the repository 

This repository contains information about the X-Road Security Server Toolkit, source code, its development, installation and documentation.

## X-Road Security Server Toolkit source code

[Source code](https://github.com/nordic-institute/X-Road-Security-Server-toolkit) of X-Road Security Server Toolkit is open for all and it is licenced under MIT licence.

## Introduction to X-Road Security Server Toolkit

[X-Road Security Server Toolkit User Guide](https://github.com/nordic-institute/X-Road-Security-Server-toolkit/blob/master/docs/xroad_security_server_toolkit_user_guide.md)


## Installing the latest development version

Installation is performed with pip (use pip or pip3, whichever is used)

```
$ git clone https://github.com/nordic-institute/X-Road-Security-Server-toolkit.git

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
### Project versioning

Pre-release:

```
$ 0.x.x-alpha.0
```

First release:

```
$ 1.0.0-final.0
```

Post first release:

```
$ 1.x.x-beta.0
```


### Updating project version

* Update patch/minor/major/release/build (major.minor.patch-release.build)
```
$ bump2version patch/minor/major/release/build (e.g. bump2version minor)
```
In case of minor updates, use `bump2version patch`
In case of major updates, use `bump2version minor`
When releasing, use `bump2version major`

In case of releasing, also `bump2version release` should be performed
to update the release part of the version number, which can contain values: 
```
beta
final
```

### Releasing

Use the included helper function via the `Makefile`:

```
$ make dist
```
