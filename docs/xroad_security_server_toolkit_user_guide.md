# X-Road Security Server Toolkit User Guide

**Technical Specification**

Version: 1.2.2
Doc. ID: XRDSST-CONF

---

## Version history <!-- omit in toc -->
| Date       | Version     | Description                                                                  | Author             |
|------------|-------------|------------------------------------------------------------------------------|--------------------|
| 10.11.2020 | 1.0.0       | Initial draft                                                                | Bert Viikmäe       |
| 12.11.2020 | 1.1.0       | Documentation of initialization functionality                                | Bert Viikmäe       |
| 16.11.2020 | 1.1.1       | Documentation of token login functionality                                   | Taimo Peelo        |
| 08.12.2020 | 1.1.2       | Documentation of token key initializations                                   | Taimo Peelo        |
| 15.12.2020 | 1.1.3       | Documentation of api-key parameterization                                    | Bert Viikmäe       |
| 22.12.2020 | 1.1.4       | Brief notes on certificate management                                        | Taimo Peelo        |
| 30.12.2020 | 1.1.5       | Note on certificate activation                                               | Taimo Peelo        |
| 12.01.2021 | 1.1.6       | Notes on client management                                                   | Taimo Peelo        |
| 20.01.2021 | 1.1.7       | Notes on adding service descriptions                                         | Bert Viikmäe       |
| 27.01.2021 | 1.1.8       | Notes on enabling service descriptions                                       | Bert Viikmäe       |
| 03.02.2021 | 1.1.9       | Notes on server status query                                                 | Taimo Peelo        |
| 17.02.2021 | 1.2.0       | Updates to the user guide                                                    | Bert Viikmäe       |
| 22.02.2021 | 1.2.1       | Update service management                                                    | Bert Viikmäe       |
| 23.02.2021 | 1.2.2       | Update service management                                                    | Bert Viikmäe       |

## Table of Contents <!-- omit in toc -->

<!-- toc -->
<!-- vim-markdown-toc GFM -->

- [License](#license)
- [1. Introduction](#1-introduction)
  - [1.1 Target Audience](#11-target-audience)
- [2. Installation](#2-installation)
  - [2.1 Prerequisites to Installation](#21-prerequisites-to-installation) 
  - [2.2 Installation procedure](#22-installation-procedure)  
- [3 Configuration of X-Road Security Server](#3-configuration-of-x-road-security-server)
  - [3.1 Prerequisites to Configuration](#31-prerequisites-to-configuration)
  - [3.2 Format of configuration file](#32-format-of-configuration-file)
  - [3.3 Different ways of using the configuration file](#33-different-ways-of-using-the-configuration-file)  
- [4 Running the X-Road Security Server Toolkit](#4-running-the-x-road-security-server-toolkit)
  - [4.1 The single command fully automatic configuration of security servers listed in configuration file](#41-the-single-command-fully-automatic-configuration-of-security-servers-listed-in-configuration-file)
  - [4.2 Initializing the security server](#42-initializing-the-security-server)
  - [4.3 Logging in a single software token](#43-logging-in-a-single-software-token)
  - [4.4 Listing security server tokens](#44-listing-security-server-tokens)
  - [4.5 Configuring security server to use single approved timestamping service](#45-configuring-security-server-to-use-single-approved-timestamping-service)
  - [4.6 Initializing token keys and corresponding certificate signing requests](#46-initializing-token-keys-and-corresponding-certificate-signing-requests)
  - [4.7 Certificate management](#47-certificate-management)
  - [4.8 Client management](#48-client-management)
  - [4.9 Service management](#49-service-management)
	
<!-- vim-markdown-toc -->
<!-- tocstop -->

## License

This document is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

## 1. Introduction

### 1.1 Target Audience

The intended audience of this installation guide are the X-Road security server administrators responsible for installing and configuring the X-Road security server software.
The document is intended for readers with a good knowledge of Linux server management, computer networks, and the X-Road functioning principles.

## 2. Installation

### 2.1 Prerequisites to Installation

* Python version 3.6+
* PIP

### 2.2 Installation procedure

The X-Road Security Server Toolkit package can be installed using PIP:

```
$ pip install xrdsst --extra-index-url https://xroad-toolkit.s3-eu-west-1.amazonaws.com/xrdsst
```

After the packages are installed, the following commands from the command line need to be run:
```
$ pip install -r requirements-dev.txt

$ pip install setup.py
```

## 3 Configuration of X-Road Security Server

### 3.1 Prerequisites to Configuration

* a central server running the Ubuntu 18.04 LTS or 20.04 LTS operating system, on an x86-64bit platform. 
* a security server providing management services. 
* single or multiple security servers(to be configured by the X-Road Security Server Toolkit) running the Ubuntu version 18.04 LTS or 20.04 LTS 
  or Redhat version 7 or 8 operating system, on an x86-64bit platform or X-Road Security Server Sidecar running in a Docker container
* configuration file in YAML format for configuring security server
  
### 3.2 Format of configuration file
```
api-key:
- credentials: <SECURITTY_SERVER_CREDENTIALS>
  key: /path/to/ssh_private_key
  roles:
  - <SECURITY_SERVER_ROLE_NAME>
  url: https://localhost:4000/api/v1/api-keys
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
  clients:
    - member_class: <MEMBER_CLASS>
      member_code: <MEMBER_CODE>
      subsystem_code: <SUBSYSTEM_CODE>
      connection_type: <CONNECTION_TYPE>
      service_descriptions:
        - url: <SERVICE_DESCRIPTION_URL>
          rest_service_code: <REST_SERVICE_CODE>
          type: <SERVICE_TYPE>
          access:
            - <SUBSYSTEM_CODE>
          url_all: <SERVICE_URL_FOR_ALL>
          timeout_all: <SERVICE_TIMEOUT_FOR_ALL>
          ssl_auth_all: <SERVICE_USE_SSL_AUTH_FOR_ALL>
          services:
            - service_code: <SERVICE_CODE>
              access:
                - <SUBSYSTEM_CODE>
              timeout: <SERVICE_TIMEOUT>
              ssl_auth: <SERVICE_USE_SSL_AUTH>
              url: <SERVICE_URL>
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
* <SUBSYSTEM_CODE> X-Road member/client subsystem code.
* <CONNECTION_TYPE> Connection protocol selection, from among ``HTTP``, ``HTTPS``, ``HTTPS_NO_AUTH``.
* <SERVICE_DESCRIPTION_URL> URL for service description
* <REST_SERVICE_CODE> rest service code, not used for WSDL services
* <SERVICE_TYPE> type of service, value from ``OPENAPI3``, ``REST``, ``WSDL``.
* <SERVICE_TIMEOUT> timeout for service in seconds
* <SERVICE_USE_SSL_AUTH> boolean value for specifying whether SSL authentication should be used
* <SERVICE_URL_FOR_ALL> boolean value for specifying URL for all services for a given service description
* <SERVICE_TIMEOUT_FOR_ALL> boolean value for specifying timeout for all services for a given service description
* <SERVICE_USE_SSL_AUTH_FOR_ALL> boolean value for specifying whether SSL authentication should be used for all services for a given service description
* <SERVICE_URL> URL for single service
* <SERVICE_CODE> code for single service.

In section ``service_descriptions`` service with type ``OPENAPI3``, ``REST``, ``WSDL`` can be configured by adding a service description
with parameters ``url``, ``rest_service_code``, ``type`` and ``access``. In order to provide access to the services added with that
service description to different subsystems, the parameter ``access`` should contain a list of subsystem codes. To configure specific services
described with the service description, the parameters ``service_code`` and ``access`` must be configured in the section ``services``. 


### 3.3 Different ways of using the configuration file

* default configuration in config/base.yaml
* overriding the default configuration by providing an extra parameter ``-c configfile`` when running the X-Road Security Server Toolkit

## 4 Running the X-Road Security Server Toolkit

The X-Road Security Server Toolkit is run from the command line by typing:

```
$ xrdsst
```

Which currently gives further information about tool invocation options and subcommands.
Base information about statuses of all defined security servers can be seen with read-only
``status`` operation:

```
$ xrdsst status
╒══════════════════╤══════════════════════╤═════════════════════════╤═══════════════════════╤══════════╤═════════════╤══════════╤═══════════╤═════════╕
│ GLOBAL           │ SERVER               │ ROLES                   │ INIT                  │ TSAS     │ TOKEN       │ KEYS     │ CSRS      │ CERTS   │
╞══════════════════╪══════════════════════╪═════════════════════════╪═══════════════════════╪══════════╪═════════════╪══════════╪═══════════╪═════════╡
│ OK (SUCCESS)     │ ss5                  │ System Administrator    │ ANCHOR INITIALIZED    │ Test TSA │ ID 0        │ SIGN (2) │ AUTH* (1) │ SIGN    │
│ LAST 131158 0202 │ VER 6.25.0           │ Service Administrator   │ CODE INITIALIZED      │          │ softToken-0 │ AUTH (2) │ 1 CSRS    │ AUTH    │
│ NEXT 131258 0202 │ DEV:GOV:9876:UNS-SS5 │ Registration Officer    │ OWNER INITIALIZED     │          │ STATUS OK   │ 4 KEYS   │           │         │
│                  │                      │ Security Officer        │ TOKEN INITIALIZED     │          │ LOGIN NO    │          │           │         │
│                  │                      │ Securityserver Observer │                       │          │             │          │           │         │
├──────────────────┼──────────────────────┼─────────────────────────┼───────────────────────┼──────────┼─────────────┼──────────┼───────────┼─────────┤
│ OK (SUCCESS)     │ ss3                  │ System Administrator    │ ANCHOR INITIALIZED    │ Test TSA │ ID 0        │ SIGN (1) │ SIGN (1)  │         │
│ LAST 131222 0202 │ VER 6.25.0           │ Service Administrator   │ CODE INITIALIZED      │          │ softToken-0 │ AUTH (1) │ AUTH (1)  │         │
│ NEXT 131322 0202 │ DEV:GOV:9876:UNS-SS3 │ Registration Officer    │ OWNER INITIALIZED     │          │ STATUS OK   │ 2 KEYS   │ 2 CSRS    │         │
│                  │                      │ Security Officer        │ TOKEN INITIALIZED     │          │ LOGIN NO    │          │           │         │
├──────────────────┼──────────────────────┼─────────────────────────┼───────────────────────┼──────────┼─────────────┼──────────┼───────────┼─────────┤
│ FAIL (INTERNAL)  │ ss4                  │ System Administrator    │ TOKEN NOT_INITIALIZED │          │             │ 0 KEYS   │ 0 CSRS    │         │
│ LAST 131217 0202 │ VER 6.25.0           │ Security Officer        │                       │          │             │          │           │         │
│ NEXT 131317 0202 │                      │                         │                       │          │             │          │           │         │
├──────────────────┼──────────────────────┼─────────────────────────┼───────────────────────┼──────────┼─────────────┼──────────┼───────────┼─────────┤
│                  │ ss9                  │ NO ACCESS               │                       │          │             │          │           │         │
╘══════════════════╧══════════════════════╧═════════════════════════╧═══════════════════════╧══════════╧═════════════╧══════════╧═══════════╧═════════╛
```

### 4.1 The single command fully automatic configuration of security servers listed in configuration file

The whole security server configuration in a fully automatic mode (all configuration from configuration file) can be run with ``xrdsst apply``
For performing the configuration step by step instead, please start from [4.2 Initializing the security server](#42-initializing-the-security-server)

### 4.2 Initializing the security server

Configuration anchor is added and the security server is initialized with ``xrdsst init``

### 4.3 Logging in a single software token

Default software token login can be logged on with ``xrdsst token login``

### 4.4 Listing security server tokens

All tokens known to security server can be listed with ``xrdsst token list``

### 4.5 Configuring security server to use single approved timestamping service

Single timestamping service approved for use in central server can be configured for security server by invoking ``timestamp`` subcommand
as ``xrdsst timestamp init``.

### 4.6 Initializing token keys and corresponding certificate signing requests

Token keys for authentication and signatures can be created with ``xrdsst token init-keys``, which creates
two keys and generates corresponding certificate signing requests (one for authentication, other for signing).
The key labels used are conventionally with suffixes ``default-auth-key`` and ``default-sign-key``, if
those already exist, they will not be duplicated and command acts as no-op for such security server.

### 4.7 Certificate management
Certificate signing requests can be downloaded with ``xrdsst cert download-csrs``, suitably signed
certificates can be imported with ``xrdsst cert import`` and imported authentication certificate registration (deduced
from being attached to key labelled with suffix ``default-auth-key`` at central server can be initiated with ``xrdsst
cert register``, final activation with ``xrdsst cert activate``.

### 4.8 Client management
Client subsystems are managed with ``xrdsst client`` subcommands, new subsystem client can be added with
``xrdsst client add``, the subsystem parameters should be specified in the configuration ``clients`` section.
Further subsystem registration can proceed with ``xrdsst client register``. 

### 4.9 Service management
Services and service descriptions are managed with ``xrdsst service`` subcommands. Adding REST/OPENAPI3/WSDL service descriptions
is performed with ``xrdsst service add-description``. Enabling of service descriptions is performed  with ``xrdsst service enable-description``.
Adding access to services is performed  with ``xrdsst service add-access``. Service parameters are updated with ``xrdsst service update-parameters``.
