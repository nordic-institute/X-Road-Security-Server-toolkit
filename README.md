# A toolkit for configuring security server

## Installation

```
$ pip3 install -r requirements.txt

$ pip3 install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.


### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run sstoolkit cli application

$ xrdsst --help


### run pytest with coverage and pylint to check code formatting

$ make test
```

### Updating project version

```
### Update patch (major.minor.patch-release.build)

$ bump2version patch

### Update minor (major.minor.patch-release.build)

$ bump2version minor

### Update major (major.minor.patch-release.build)

$ bump2version major

### Update release (major.minor.patch-release.build)

$ bump2version release

### Update build (major.minor.patch-release.build)

$ bump2version build

```

### Releasing to PyPi

Before releasing to PyPi, you must configure your login credentials:

**~/.pypirc**:

```
[pypi]
username = YOUR_USERNAME
password = YOUR_PASSWORD
```

Then use the included helper function via the `Makefile`:

```
$ make dist

$ make dist-upload
```

## Deployments

### Docker

Included is a basic `Dockerfile` for building and distributing `Security Server Toolkit`,
and can be built with the included `make` helper:

```
$ make docker

$ docker run -it xrdsst --help
```
