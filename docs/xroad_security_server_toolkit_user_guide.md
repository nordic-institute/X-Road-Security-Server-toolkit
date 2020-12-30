# X-Road Security Server Toolkit configuration guide

**Technical Specification**

Version: 1.1.5
Doc. ID: XRDSST-CONF

| Date       | Version     | Description                                                                  | Author             |
|------------|-------------|------------------------------------------------------------------------------|--------------------|
| 10.11.2020 | 1.0.0       | Initial draft                                                                | Bert Viikmäe       |
| 12.11.2020 | 1.1.0       | Documentation of initialization functionality                                | Bert Viikmäe       |
| 16.11.2020 | 1.1.1       | Documentation of token login functionality                                   | Taimo Peelo        |
| 08.12.2020 | 1.1.2       | Documentation of token key initializations                                   | Taimo Peelo        |
| 15.12.2020 | 1.1.3       | Documentation of api-key parameterization                                    | Bert Viikmäe       |
| 22.12.2020 | 1.1.4       | Brief notes on certificate management                                        | Taimo Peelo        |
| 30.12.2020 | 1.1.5       | Note on certificate activation                                               | Taimo Peelo        |


## Table of Contents



<!-- vim-markdown-toc GFM -->

* [License](#license)
* [1 Introduction](#1-introduction)
* [2 Configuration of X-Road Security Server](#2-configuration-of-x-road-security-server)
	* [2.1 General](#21-general)
	* [2.2 Format of configuration file](#22-format-of-configuration-file)
* [3 Running the X-Road Security Server Toolkit](#3-running-the-x-road-security-server-toolkit)
	* [3.1 The automatic configuration of a single security server](#31-the-automatic-configuration-of-a-single-security-server)
	* [3.2 Logging in a single software token](#32-logging-in-a-single-software-token)
	* [3.3 Listing security server tokens](#33-listing-security-server-tokens)
	* [3.4 Configuring security server to use single approved timestamping service](#34-configuring-security-server-to-use-single-approved-timestamping-service)
	* [3.5 Initializing token keys and corresponding certificate signing requests](#35-initializing-token-keys-and-corresponding-certificate-signing-requests)
	* [3.6 Certificate management](#36-certificate-management)

<!-- vim-markdown-toc -->

## License

This document is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

## 1 Introduction

This specification describes automatic configuration of X-Road security servers using X-Road Security Server Toolkit

## 2 Configuration of X-Road Security Server

### 2.1 General

The automatic configuration of X-Road security servers using the X-Road Security Server Toolkit relies on configuration files, where exact configuration values have to be specified

### 2.2 Format of configuration file
```
api-key:
- credentials: <SECURITTY_SERVER_CREDENTIALS>
  key: /path/to/ssh_private_key
  roles:
  - <SECURITY_SERVER_ROLE_NAME>
  url: https://localhost:4000/api/v1/api-keys
logging:
- file: /path/to/xrdsst.log
  level: <LOG_LEVEL>
security-server:
- api_key: X-Road-apikey token=<API_KEY>
  configuration_anchor: /path/to/configuration-anchor.xml
  certificates:
    - /path/to/signcert
    - /path/to/authcert
  name: <SECURITY_SERVER_NAME>
  owner_dn_country: <OWNER_DISTINGUISHED_NAME_COUNTRY>
  owner_dn_org: <OWNER_DISTINGUISHED_NAME_ORGANIZATION>
  owner_member_class: <MEMBER_CLASS>
  owner_member_code: <MEMBER_CODE>
  security_server_code: <SERVER_CODE>
  software_token_id: <SOFT_TOKEN_ID>
  software_token_pin: <SOFT_TOKEN_PIN>
  url: https://<SECURITY_SERVER_FQDN_OR_IP>:4000/api/v1
```

The ``api-key`` section is for configuring the automatic api key generation parameters for security server
The ``logging`` section is for configuring the logging parameters of the X-Road Security Server Toolkit
The ``security-server`` section is for configuring security server parameters

* <SECURITY_SERVER_CREDENTIALS> X-Road Security Server credentials, e.g. xrd:secret
* ``/path/to/ssh_private_key`` should be substituted with the correct path to the ssh private key file, e.g. home/user/id_rsa
* <SECURITY_SERVER_ROLE_NAME> parameter required for security server api key, should be substituted with a security server role name, e.g. XROAD_SYSTEM_ADMINISTRATOR    
* ``/path/to/xrdsst.log`` should be substituted with the correct path to the log file, e.g. "/var/log/xroad/xrdsst.log"
* <LOG_LEVEL> parameter for configuring the logging level for the X-Road Security Server Toolkit, e.g INFO
* <API_KEY> will be automatically substituted with the api-key of the installed security server
* ``/path/to/configuration-anchor.xml`` should be substituted with the correct path to the configuration anchor file, e.g. "/etc/xroad/configuration-anchor.xml"
* <SECURITY_SERVER_NAME> should be substituted with the installed security server name, e.g. ss1
* <OWNER_DISTINGUISHED_NAME_COUNTRY> should be ISO 3166-1 alpha-2 two letter code for server owner country. This is used in certificate generation.
* <OWNER_DISTINGUISHED_NAME_ORGANIZATION> should be set to server owner organization. This is used in certificate generation.
* <MEMBER_CLASS> should be substituted with the member class obtained from the Central Server, e.g. GOV
* <MEMBER_CODE> should be substituted with the member code obtained from the Central Server, e.g. 1234
* <SERVER_CODE> should be substituted with the server code of the installed security server, e.g. SS1
* <SOFT_TOKEN_ID> default software token ID, normally 0 (zero).
* <SOFT_TOKEN_PIN> should be substituted with a desired numeric pin code
* <SECURITY_SERVER_FQDN_OR_IP> should be substituted with the IP address or host name of the installed security server, e.g. ss1
* ``/path/to/signcert`` and ``/path/to/authcert`` should be given as paths referring to certificate locations,
in fact any number of certificates can be imported for the keys labelled ``default-auth-key`` and ``default-sign-key``
(but not all of them can be in use / registered)

## 3 Running the X-Road Security Server Toolkit

The X-Road Security Server Toolkit is run from the command line by typing:

```
$ xrdsst
```

Which currently gives further information about tool invocation options and subcommands.

### 3.1 The automatic configuration of a single security server

```
$ xrdsst init
```

In the first stage of the automatic process, the security server(s) will be initialized according to the configuration data specified
in the configuration file (base.yaml). First, a configuration anchor is uploaded and then the initialization of the security server
is performed with respective <MEMBER_CLASS>, <MEMBER_CODE>, <SERVER_CODE> and <SOFT_TOKEN_PIN> values.

### 3.2 Logging in a single software token

Default software token login can be logged on with ``xrdsst token login``

### 3.3 Listing security server tokens

All tokens known to security server can be listed with ``xrdsst token list``

### 3.4 Configuring security server to use single approved timestamping service

Single timestamping service approved for use in central server can be configured for security server by invoking ``timestamp`` subcommand
as ``xrdsst timestamp init``.

### 3.5 Initializing token keys and corresponding certificate signing requests

Token keys for authentication and signatures can be created with ``xrdsst token init-keys``, which creates
two keys and generates corresponding certificate signing requests (one for authentication, other for signing).
The key labels used are conventionally with suffixes ``default-auth-key`` and ``default-sign-key``, if
those already exist, they will not be duplicated and command acts as no-op for such security server.

### 3.6 Certificate management

Certificates are imported with ``xrdsst cert import`` and imported authentication certificate registration (deduced
from being attached to key labelled with suffix ``default-auth-key`` at central server can be initiated with ``xrdsst
cert register``, final activation with ``xrdsst cert activate``.
