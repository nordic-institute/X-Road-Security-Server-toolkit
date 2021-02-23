# Changelog

All notable changes to this project will be documented in this file.

## [0.2.4-alpha.0] - 2021-02-23
- add ``xrdsst service`` subcommand ``update-parameters``

## [0.2.3-alpha.0] - 2021-02-22
- add ``xrdsst service`` subcommand ``add-rights``

## [0.2.2-alpha.0] - 2021-02-03
- Add examination of configured server statuses with ``xrdsst status``

## [0.2.1-alpha.0] - 2021-01-27

- move adding and enabling of service descriptions to ServiceController
  so that adding is performed with``xrdsst service`` subcommand ``add-description``
  and enabling with ``xrdsst service`` subcommand ``enable-description``

## [0.2.0-alpha.0] - 2021-01-21

- add ``xrdsst client`` subcommand ``add-service-description``

## [0.1.20-alpha.0] - 2021-01-21

- add ``xrdsst apply`` autoconfiguration command, rework log error handling

## [0.1.19-alpha.0] - 2021-01-12

- add ``xrdsst client`` subcommand ``register``

## [0.1.18-alpha.0] - 2021-01-07

- add ``xrdsst client`` and subcommand ``add``

## [0.1.17-alpha.0] - 2020-12-31

- add ``xrdsst cert`` commands ``activate`` and ``download-csrs``

## [0.1.16-alpha.0] - 2020-12-22

- add ``xrdsst cert`` commands ``import`` and ``register``

## [0.1.15-alpha.0] - 2020-12-20

- add end to end tests for init, token login, token init-keys and timestamp init

## [0.1.14-alpha.0] - 2020-12-15

- add automatic api key creation

## [0.1.13-alpha.0] - 2020-12-10

- add integration tests for init, token login, token init-keys and timestamp init

## [0.1.12-alpha.0] - 2020-12-08

- add ``token`` sub-command ``init-keys``

## [0.1.11-alpha.0] - 2020-12-03

- create Makefile tasks for testing

## [0.1.10-alpha.0] - 2020-11-27

- add ``timestamp`` sub-command with ``init`` and some listing proto-bonuses

## [0.1.9-alpha.0] - 2020-11-24

- add bump2version to handle automatic version updates

## [0.1.4-alpha.0] - 2020-11-20

- add PyLint to the project so that the code will conform to formatting rules

## [0.1.3-alpha.0] - 2020-11-19

- add script for automatic reset of security servers and creation of api-keys

## [0.1.2-alpha.0] - 2020-11-18

- add support for tabulated / json output render
- token listing to use Cement rendering

## [0.1.1-alpha.0] - 2020-11-16

- add token listing and login (for default software token) methods

## [0.1.0-alpha.0] - 2020-11-10

- add methods for uploading configuration anchor and initializing security server
- create initial unit tests
- create initial documentation
- update changelog and build version
- update license
- delete unrelated folders and files
- add logging

## [0.0.2-alpha.0] - 2020-11-04

- update license
- update configuration file

## [0.0.1-alpha.0] - 2020-11-03

- create initial project files
