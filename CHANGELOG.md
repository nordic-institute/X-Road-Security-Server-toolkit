# Changelog
All notable changes to this project will be documented in this file.

## [2.4.4-beta.0] - 2021-07-20
- add ``xrdsst diagnostics`` and sub-commands ``global-configuration``, ``ocsp-responders`` and ``timestamping-services``
- add ``xrdsst client`` and sub-command ``make-owner``
- add ``xrdsst endpoint`` and sub-command ``list``

## [2.4.3-beta.0] - 2021-07-15
- add ``xrdsst backup`` and sub-command ``restore``

## [2.4.2-beta.0] - 2021-07-15
- add ``xrdsst backup`` and sub-command ``delete``

## [2.4.1-beta.0] - 2021-07-14
- add ``xrdsst backup`` and sub-commands ``list``, ``add`` and ``download``
- add ``xrdsst local-group`` and sub-commands ``add``, ``add-member``, ``list`` and ``delete``

## [2.4.0-beta.0] - 2021-07-09
- add ``xrdsst service`` and sub-commands ``list-access`` and ``delete-access``
- add ``xrdsst client`` and sub-commands ``unregister`` and ``delete``

## [2.3.0-beta.0] - 2021-07-05
- add ``xrdsst service`` and sub-commands ``update-descriptions``, ``refresh-descriptions`` and ``disable-descriptions``

## [2.2.0-beta.0] - 2021-07-01
- add ``xrdsst service`` and sub-command ``delete-descriptions``
- add certificate renewal support

## [2.1.2-beta.0] - 2021-06-28
- add ``xrdsst service`` and sub-command ``list-services``

## [2.1.1-beta.0] - 2021-06-25
- Fix ``xrdsst member`` sub-command ``list-classes`` to list classes for current instance when command-line parameter not provided
- add ``xrdsst service`` and sub-command ``list-descriptions``

## [2.1.4-beta.0] - 2021-06-28
- add ``xrdsst token create-new-keys`` command
- refactor code to been able to register cert when multiple auth certificates

## [2.1.0-beta.0] - 2021-06-22
- add ``xrdsst member`` and sub-command ``list-classes``
- add ``xrdsst cert`` and sub-commands ``delete`` and ``unregister``

## [2.0.2-beta.0] - 2021-06-18
- add ``xrdsst member`` and sub-command ``find``
- add ``xrdsst cert`` and sub-commands ``list`` and ``disable``

## [2.0.1-beta.0] - 2021-06-16
- Add Jenkinsfile for running integration tests on pull requests
- Add Docker support
- Fix validation of optional parameters

## [2.0.0-final.0] - 2021-06-11
- X-Road-Security Server Toolkit release version 2.0

## [1.4.0-beta.0] - 2021-06-11
- add ``xrdsst client`` and sub-command ``import-tls-certs``
- fix spelling mistake in sub-command ``download-internal-tls``
- fix adding of service description to not require ``rest_service_code`` parameter and ``endpoints`` section in the configuration
- update the documentation to be more clear

## [1.3.0-beta.0] - 2021-05-31
- Refactorization of end to end and integration tests to support negative cases and multiple security servers

## [1.2.0-beta.0] - 2021-05-28
- add ``xrdsst service`` sub-command ``apply``
- add multi-tenancy support

## [1.1.1-beta.0] - 2021-05-21
- fixed sonar issues
- add ``xrdsst cert`` and sub-command ``download-internal-tsl``

## [1.1.0-beta.0] - 2021-05-14
- add ``xrdsst client`` and sub-command ``update``

## [1.0.9-beta.0] - 2021-05-13
- Added section into the User Guide about using the Toolkit to configure highly available services using the built-in security server internal load balancing

## [1.0.8-beta.0] - 2021-05-10
- Added section into the User Guide about Load Balancer setup description

## [1.0.7-beta.0] - 2021-05-04
- add sub-command ``add-access`` to ``xrdsst endpoint`` and refacto ``add-access`` of ``xrdsst service`` to allow adding access to any member

## [1.0.6-beta.0] - 2021-05-03
- Dockerfile and respective Makefile target removed

## [1.0.5-beta.0] - 2021-04-27
- Fix auto-configuration to show configuration status in the end of run for multiple security servers

## [1.0.4-beta.0] - 2021-04-27
- API keys in configuration files kept as environment variables instead of plain text to reduce security risks

## [1.0.3-beta.0] - 2021-04-26
- add ``xrdsst endpoint`` and sub-command ``add-endpoints``

## [1.0.2-beta.0] - 2021-04-20
- Secrets in configuration files kept as environment variables instead of plain text to reduce security risks

## [1.0.1-beta.0] - 2021-04-19
- Toolkit optimised to run against multiple clean installed security servers 

## [1.0.0-final.0] - 2021-04-09
- X-Road-Security Server Toolkit release version 1.0

## [0.4.2-alpha.0] - 2021-04-09
- Documentation updates related to package verification

## [0.4.1-alpha.0] - 2021-04-06
- add ``xrdsst user`` and sub-command ``create-admin``

## [0.4.0-alpha.0] - 2021-04-05
- Mask API key representations in log files.
- Represent API key in configuration as UUID, without HTTP header prefix.
- init logging after config key-level validation, non-mutable ops undifferentiated.

## [0.3.3-alpha.0] - 2021-04-05
- remove undocumented configuration element ``api_key_roles``
- Stop toolkits' attempts to further communicate with security server when API
  key unavailable or access denied.

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
- add ``xrdsst service`` sub-command ``update-parameters``

## [0.2.4-alpha.0] - 2021-02-22
- add ``xrdsst service`` sub-command ``add-access``

## [0.2.3-alpha.0] - 2021-02-22
- Auto-configuration to be sequential per-security server.
- Defined operation completion criteria.
- Operations made aware of operational context.
- Configuration file validated on global level (keys) and operation level (required keys, value sanity)
- Auto-configuration stops after operation that could not be completed
- Auto-configuration shows base operation statuses when ended / stopped.

## [0.2.2-alpha.0] - 2021-02-03
- Add examination of configured server statuses with ``xrdsst status``

## [0.2.1-alpha.0] - 2021-01-27

- move adding and enabling of service descriptions to ServiceController
  so that adding is performed with``xrdsst service`` sub-command ``add-description``
  and enabling with ``xrdsst service`` sub-command ``enable-description``

## [0.2.0-alpha.0] - 2021-01-21

- add ``xrdsst client`` sub-command ``add-service-description``

## [0.1.20-alpha.0] - 2021-01-21

- add ``xrdsst apply`` auto-configuration command, rework log error handling

## [0.1.19-alpha.0] - 2021-01-12

- add ``xrdsst client`` sub-command ``register``

## [0.1.18-alpha.0] - 2021-01-07

- add ``xrdsst client`` and sub-command ``add``

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
