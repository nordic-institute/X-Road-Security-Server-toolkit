# Changelog

All notable changes to this project will be documented in this file.

## [0.3.2-alpha.0] - 2021-03-29
- Make SSH user configurable for api key creation

## [0.3.1-alpha.0] - 2021-03-26
- Add the external FQDN specification support for certificates and service providers.

## [0.3.0-alpha.0] - 2021-03-24
- Update security server API client to current spec, 1.0.31 (was 1.0.30)

## [0.2.8-alpha.0] - 2021-03-22
- default configuration file config/(base.yaml) -> (xrdsst.yml)
- replace security server 'name' use for SSH connection attempts with /host/
- remove all YAML loading not done via safe_load (SafeLoader)

## [0.2.7-alpha.0] - 2021-03-17
- added failure handling / error interpretation and recovery section to user guide
- output tuning for 'token init-keys' reporting
- mention 'cert downloads-csrs' directly when 'cert import' execution is reached
  but missing 'certificates' element for security server

## [0.2.6-alpha.0] - 2021-03-12
- Extended proxy error handling and feedback, ASCII diagrams included.

## [0.2.5-alpha.0] - 2021-02-23
- add ``xrdsst service`` subcommand ``update-parameters``

## [0.2.4-alpha.0] - 2021-02-22
- add ``xrdsst service`` subcommand ``add-access``

## [0.2.3-alpha.0] - 2021-02-22
- Autoconfiguration to be sequential per-security server.
- Defined operation completion criteria.
- Operations made aware of operational context.
- Configuration file validated on global level (keys) and operation level (required keys, value sanity)
- Autoconfiguration stops after operation that could not be completed
- Autoconfiguration shows base operation statuses when ended / stopped.

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
