# X-Road Security Server Toolkit User Guide
Version: 1.3.10
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
| 17.03.2021 | 1.2.3       | Describe failure interpretation and recovery                                 | Taimo Peelo        |
| 22.03.2021 | 1.2.4       | Default configuration from config/base.yaml -> config/xrdsst.yml             | Taimo Peelo        |
| 26.03.2021 | 1.2.5       | Add 'fqdn' key for security server, fix service field descriptions           | Taimo Peelo        |
| 31.03.2021 | 1.2.6       | Refactorization of configuration file related to SSH and api key parameters  | Bert Viikmäe       |
| 01.04.2021 | 1.2.7       | Describe backup use, clarify toolkits' error interpretation role, remove undocumented ``api_key_roles`` configuration element | Taimo Peelo        |
| 05.04.2021 | 1.2.8       | Remove HTTP header value prefix from 'api_key' configuration element         | Taimo Peelo        |
| 06.04.2021 | 1.2.9       | Describe different security server access possibilities                      | Taimo Peelo        |
| 06.04.2021 | 1.2.10      | Notes on user management                                                     | Bert Viikmäe       |
| 09.04.2021 | 1.2.11      | Added description about signing and verification of packages                 | Bert Viikmäe       |
| 20.04.2021 | 1.3.0       | Substituting plain text secrets in configuration with environment variables  | Bert Viikmäe       |
| 26.04.2021 | 1.3.1       | Added description about adding endpoints to the REST and OpenAPI services.   | Alberto Fernandez  |
| 27.04.2021 | 1.3.2       | Substituting plain text api key in configuration with environment variable   | Bert Viikmäe       |
| 04.05.2021 | 1.3.3       | Added description about endpoint access                                      | Alberto Fernandez  |
| 10.05.2021 | 1.3.4       | Added Load Balancer setup description                                        | Alberto Fernandez  |            
| 13.05.2021 | 1.3.5       | Added description about load-balancing                                       | Bert Viikmäe       |
| 14.05.2021 | 1.3.6       | Notes on client management                                                   | Bert Viikmäe       |
| 24.05.2021 | 1.3.7       | Added download-internal-tsl command                                          | Alberto Fernandez  |
| 28.05.2021 | 1.3.8       | Added member name property  and multitenancy section                         | Alberto Fernandez  |
| 28.05.2021 | 1.3.9       | Update service management                                                    | Bert Viikmäe       |
| 04.06.2021 | 1.3.10       | Refactor documentation                                                       | Alberto Fernandez  |
## Table of Contents <!-- omit in toc -->

<!-- toc -->
<!-- vim-markdown-toc GFM -->

* [License](#license)
   * [1. Introduction](#1-introduction)
      * [1.1 Target Audience](#11-target-audience)
      * [1.2 References](#12-references)
   * [2. Installation](#2-installation)
      * [2.1 Prerequisites to Installation](#21-prerequisites-to-installation)
      * [2.2 Installing the official released version](#22-installing-the-official-released-version)
   * [3 Configuration of X-Road Security Server](#3-configuration-of-x-road-security-server)
      * [3.1 Prerequisites to Configuration](#31-prerequisites-to-configuration)
         * [3.1.1 Toolkit access to security servers](#311-toolkit-access-to-security-servers)
            * [3.1.1.1 Using API keys](#3111-using-api-keys)
            * [3.1.1.2 Using SSH](#3112-using-ssh)
      * [3.2 Format of configuration file](#32-format-of-configuration-file)
         * [3.2.1 Access Configuration](#321-access-configuration)
         * [3.2.2 Security Servers Configuration](#322-security-servers-configuration)
         * [3.2.3 Client Configuration](#323-client-configuration)
         * [3.2.3 Services Configuration](#323-services-configuration)
      * [3.3 Different ways of using the configuration file](#33-different-ways-of-using-the-configuration-file)
   * [4 Running the X-Road Security Server Toolkit](#4-running-the-x-road-security-server-toolkit)
      * [4.1 The single command fully automatic configuration of security servers listed in configuration file](#41-the-single-command-fully-automatic-configuration-of-security-servers-listed-in-configuration-file)
      * [4.2 X-Road Security Server  Toolkit commands](#42-x-road-security-server--toolkit-commands)
         * [4.2.1 Creating admin user command](#421-creating-admin-user-command)
         * [4.2.2 Initializing the security server command](#422-initializing-the-security-server-command)
         * [4.2.3 Token commands](#423-token-commands)
            * [4.2.3.1 Token login command](#4231-token-login-command)
            * [4.2.3.2 Token list](#4232-token-list)
            * [4.2.3.3 Token init-keys](#4233-token-init-keys)
         * [4.2.4 Timestamp commands](#424-timestamp-commands)
            * [4.2.4.1 Timestamp init](#4241-timestamp-init)
            * [4.2.4.2 Timestamp list approved](#4242-timestamp-list-approved)
            * [4.2.4.3 Timestamp list configured](#4243-timestamp-list-configured)
         * [4.2.5 Certificate management commands](#425-certificate-management-commands)
            * [4.2.5.1 Certificate download CSRS](#4251-certificate-download-csrs)
            * [4.2.5.2 Certificate import](#4252-certificate-import)
            * [4.2.5.3 Certificate registration](#4253-certificate-registration)
            * [4.2.5.4 Certificate activation](#4254-certificate-activation)
            * [4.2.5.5 Download internal TSL certificates](#4255-download-internal-tsl-certificates)
         * [4.2.5 Client management commands](#425-client-management-commands)
            * [4.2.5.1 Client add](#4251-client-add)
            * [4.2.5.2 Client register](#4252-client-register)
            * [4.2.5.3 Client update](#4253-client-update)
         * [4.2.6 Service management commands](#426-service-management-commands)
            * [4.2.6.1 Service add description](#4261-service-add-description)
            * [4.2.6.2 Service add access rights](#4262-service-add-access-rights)
            * [4.2.6.3 Enable service](#4263-enable-service)
            * [4.2.6.4 Service update parameters](#4264-service-update-parameters)
            * [4.2.6.5 Service apply](#4265-service-apply)
         * [4.2.7 Endpoint management](#427-endpoint-management)
            * [4.2.7.1 Endpoint add](#4271-endpoint-add)
            * [4.2.7.2 Endpoint add access rights](#4272-endpoint-add-access-rights)
   * [5 Failure recovery and interpretation of errors](#5-failure-recovery-and-interpretation-of-errors)
      * [5.1 Configuration flow](#51-configuration-flow)
      * [5.2 First-run failures](#52-first-run-failures)
      * [5.3 Configuration file errors](#53-configuration-file-errors)
         * [5.3.1 Malformed YAML](#531-malformed-yaml)
         * [5.3.2 Other configuration file errors](#532-other-configuration-file-errors)
      * [5.4 Errors from internal and external systems](#54-errors-from-internal-and-external-systems)
      * [5.5 Recovery from misconfiguration](#55-recovery-from-misconfiguration)
   * [6 Load balancer setup](#6-load-balancer-setup)
   * [7 Using the Toolkit to configure highly available services using the built-in security server internal load balancing](#7-using-the-toolkit-to-configure-highly-available-services-using-the-built-in-security-server-internal-load-balancing)
   * [8 Multitenancy](#8-multitenancy)


<!-- vim-markdown-toc -->
<!-- tocstop -->

## License

This document is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

## 1. Introduction

### 1.1 Target Audience

The intended audience of this installation guide are the X-Road security server administrators responsible for installing and configuring the X-Road security server software.
The document is intended for readers with a good knowledge of Linux server management, computer networks, and the X-Road functioning principles.

### 1.2 References

* <a id="Ref_CS-UG" class="anchor"></a> [\[UG-CS\] X-Road: Central Server User Guide](https://docs.x-road.global/Manuals/ug-cs_x-road_6_central_server_user_guide.html)
* <a id="Ref_SS-UG" class="anchor"></a> [\[UG-SS\] X-Road: Security Server User Guide](https://docs.x-road.global/Manuals/ug-ss_x-road_6_security_server_user_guide.html)
* <a id="Ref_YAML_1_1" class="anchor"></a> [\[YAML-1.1\] YAML Ain’t Markup Language (YAML™) Version 1.1](https://yaml.org/spec/1.1)


## 2. Installation

### 2.1 Prerequisites to Installation

* Python version 3.6+
* PIP 21.0+
* Installed X-Road security server packages

## 2.2 Installation

Installation is performed with pip (use pip or pip3, whichever is used)

```
$ pip install -r requirements.txt

$ pip install setup.py
```

### 2.2 Installing the official released version

The X-Road Security Server Toolkit package can be installed using PIP (use pip or pip3, whichever is used):

```
$ pip install --extra-index-url http://xroad-toolkit.s3-website-eu-west-1.amazonaws.com/ xrdsst --trusted-host xroad-toolkit.s3-website-eu-west-1.amazonaws.com
```

Package signing public key for can be retrieved from SKS keyserver pool (pool.sks-keyservers.net), key fingerprint is ``BEC35825BBAB4288933F0354116AC90A8F670D74``, publisher ``Jenkins (X-Road Development Signing Key) <jenkins@niis.org>``.

Signature ``xrdsst-1.0.0.sig`` of signed package can be downloaded from: http://xroad-toolkit.s3-website-eu-west-1.amazonaws.com/xrdsst/xrdsst-1.0.0.sig

Downloaded packages with detached signatures can be verified after adding signing public key to local keyring:
```
$ gpg --keyserver pool.sks-keyservers.net --search-keys  BEC35825BBAB4288933F0354116AC90A8F670D74
$ gpg --verify xrdsst-1.0.0.sig xrdsst-1.0.0.tar.gz
```

After installation, ``xrdsst`` command runs the toolkit, when invoked without any parameters,
it will give the overview of available options and sub-commands. Sub-commands themselves can
also have further subcommands, so for example all the supported token operations can be listed
with ``xrdsst token``:

```
$ xrdsst token
usage: xrdsst token [-h] [-v] {init-keys,list,login} ...
```


## 3 Configuration of X-Road Security Server

### 3.1 Prerequisites to Configuration

* X-Road central server. In development, this is best run in the mode where auto-approvals
are enabled, to be able to register authentication certificates and manage security server
clients without taking separate actions at central server, see [UG-CS](#Ref_CS-UG) about
``auto-approve-auth-cert-reg-requests`` and ``auto-approve-client-reg-requests``.
* Single or multiple security servers to be configured and maintained. Supported and tested
platforms for the security servers are Ubuntu 18.04/20.04 LTS, Red Hat Enterprise Linux
(RHEL) 7/8 on an x86-64 platform, and
[X-Road Security Server Sidecar](https://github.com/nordic-institute/X-Road-Security-Server-sidecar)
running in a Docker container.
* X-Road security server with subsystem acting as service provider for X-Road management
services, in separate security server.
* Toolkit access to configured security servers.

#### 3.1.1 Toolkit access to security servers

To be able to use the toolkit for configuring security server(s), one of the following access combinations
is needed:

1. Access to REST API of configured security server + existing API key.
1. Access to REST API of configured security server + SSH access to the security server machine + X-Road security server administrative credentials.

Security server REST API is ordinarily exposed at security server port 4000 and is separated into
two parts:
  1. invocable over network -- API calls for performing most of the functionality available from
     web administration console, accessible with API key.
  1. invocable only locally (in default configuration), i.e. when accessed via 'localhost' or
     equivalent and passed security server administrative credentials via HTTP basic access
     authentication -- API calls that allow API key management operations.

##### 3.1.1.1 Using API keys

The API key used by toolkit against REST API needs following roles for full toolkit
functionality:
 1. XROAD_SYSTEM_ADMINISTRATOR
 1. XROAD_SERVICE_ADMINISTRATOR
 1. XROAD_SECURITY_OFFICER
 1. XROAD_REGISTRATION_OFFICER

On freshly installed and completely unconfigured security server, API key can be obtained from
the server with local API invocation, e.g.:
```sh
$ curl -k --silent \
    -X POST \
    --header 'Content-Type: application/json' \
    --data '["XROAD_SYSTEM_ADMINISTRATOR", "XROAD_SERVICE_ADMINISTRATOR"]' \
    -u user:pass https://localhost:4000/api/v1/api-keys \
 | jq
{
   "id":122,
   "key":"55f0a0ce-46d6-4217-a15a-43e026c4a9c5",
   "roles":["XROAD_SYSTEM_ADMINISTRATOR","XROAD_SERVICE_ADMINISTRATOR"]
}
```

In the above sample command, role list was shortened for readability, ``user:pass`` to use are
X-Road security server administrative access credentials. In the output sample,
``key`` is the UUID to be used as REST API key. This UUID is only retrievable once for
API key, as it is not stored in plaintext at the security server. If dealing with security
server that already has some basic configuration done (anchors, ownership information
and software token configuration finished), this API key can also be created from the web
administration console (from "Keys and certificates" -> "API keys" submenu).

##### 3.1.1.2 Using SSH

For ease of automation and development experiments, toolkit is also able to perform operations
when not supplied with API key, but given SSH access credentials to configurable server and security
server administration credentials. In this case, it will create transient API keys for performing
the configuration operations, in the same way as described above, and these API keys are normally
revoked when the toolkit command finishes. However, in case of e.g. electricity or network
connection loss these keys could remain on the security server indefinitely.

If SSH access is configured for sudo-capable or root account, this also enables creation of (additional)
administrative accounts for the security server.

  
### 3.2 Format of configuration file

Configuration file is in YAML 1.1 format [YAML-1.1](#Ref_YAML_1_1). Avoid using tabs, which
are considered underspecified in YAML. In below configuration skeleton sample, '#' are comments,
and texts between ``<>`` angle brackets are placeholders that (sometimes optionally) should be
filled in the configuration skeleton. The meaning of these placeholders is documented in more
details after the sample. Optional elements that are not to be used can be removed completely.


```
admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
ssh_access:
  user: <SSH_USER_OS_ENV_VAR_NAME>
  private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
security_server:
- api_key: <API_KEY_ENV_VAR_NAME>
  api_key_url: https://localhost:4000/api/v1/api-keys
  admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
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
  fqdn: <SECURITY_SERVER_EXTERNAL_FQDN>
  url: https://<SECURITY_SERVER_INTERNAL_FQDN_OR_IP>:4000/api/v1
  ssh_user: <SSH_USER_OS_ENV_VAR_NAME>
  ssh_private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
  clients:
    - member_class: <MEMBER_CLASS>
      member_code: <MEMBER_CODE>
      member_name: <MEMBER_NAME>
      subsystem_code: <SUBSYSTEM_CODE>
      connection_type: <CONNECTION_TYPE>
      service_descriptions:
        - url: <SERVICE_DESCRIPTION_URL>
          rest_service_code: <REST_SERVICE_CODE>
          type: <SERVICE_TYPE>
          access:
            - <SERVICE_CLIENT_ID>
          url_all: <SERVICE_URL_FOR_ALL>
          timeout_all: <SERVICE_TIMEOUT_FOR_ALL>
          ssl_auth_all: <SERVICE_USE_SSL_AUTH_FOR_ALL>
          services:
            - service_code: <SERVICE_CODE>
              access:
                - <SERVICE_CLIENT_ID>
              timeout: <SERVICE_TIMEOUT>
              ssl_auth: <SERVICE_USE_SSL_AUTH>
              url: <SERVICE_URL>
          endpoints:
			- path: <ENDPOINT_PATH>
			  method: <ENDPOINT_METHOD>
			  access: 
			    - <SERVICE_CLIENT_ID>
```

#### 3.2.1 Access Configuration

This section shows how to configure the security server access as described in
[3.1.1 Toolkit access to security servers](#311-toolkit-access-to-security-servers)
```
admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
ssh_access:
  user: <SSH_USER_OS_ENV_VAR_NAME>
  private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
```
* <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME> Environment variable name to hold X-Road Security Server admin credentials, e.g. if the variable is set like ``export TOOLKIT_ADMIN_CREDENTIALS=user:pass`` the value to use here is ``TOOLKIT_ADMIN_CREDENTIALS`` (if specified in the separate section, one value will be 
  used for all configurable security servers, but if specified in the ``security_server`` section, the value will be overridden for specific 
  configurable security server)
* <SSH_USER_OS_ENV_VAR_NAME> Environment variable name to hold SSH username, e.g. if the variable is set like ``export TOOLKIT_SSH_USER=ssh_user`` the value to use here is ``TOOLKIT_SSH_USER`` (if specified in ``ssh_access`` section, one value will be used for all configurable security servers, 
  but if specified in the ``security_server`` section, the value will be overridden for specific configurable security server)
* <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME> Environment variable name to hold full path to SSH private key, e.g. if the variable is set like ``export TOOLKIT_SSH_PRIVATE_KEY=/home/user/private_key`` the value to use here is ``TOOLKIT_SSH_PRIVATE_KEY``
  (if specified in ``ssh_access`` section, one value will be used for all configurable security servers, 
  but if specified in the ``security_server`` section, the value will be overridden for specific configurable security server)    

#### 3.2.2 Security Servers Configuration

This section shows how to set up the security server information. It is possible to configure multiple security servers at the same time. The toolkit will execute the configurations sequentially.
```
security_server:
- api_key: <API_KEY_ENV_VAR_NAME>
  api_key_url: https://localhost:4000/api/v1/api-keys
  admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
  configuration_anchor: <CONFIGURATION_ANCHOR_PATH>
  certificates:
    - <SIGN_CERT_PATH>
    - <AUTH_CERT_PATH>
  name: <SECURITY_SERVER_NAME>
  owner_dn_country: <OWNER_DISTINGUISHED_NAME_COUNTRY>
  owner_dn_org: <OWNER_DISTINGUISHED_NAME_ORGANIZATION>
  owner_member_class: <OWNER_MEMBER_CLASS>
  owner_member_code: <OWNER_MEMBER_CODE>
  security_server_code: <SERVER_CODE>
  software_token_id: <SOFT_TOKEN_ID>
  software_token_pin: <SOFT_TOKEN_PIN>
  fqdn: <SECURITY_SERVER_EXTERNAL_FQDN>
  url: https://<SECURITY_SERVER_INTERNAL_FQDN_OR_IP>:4000/api/v1
  ssh_user: <SSH_USER_OS_ENV_VAR_NAME>
  ssh_private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
```
* <API_KEY_ENV_VAR_NAME> Environment variable name to hold X-Road Security Server API key (e.g. if the variable is set like ``export TOOLKIT_API_KEY=f13d5108-7799-426d-a024-1300f52f4a51`` the value to use here is ``TOOLKIT_API_KEY``) or left as-is/any for toolkit to attempt creation of transient API key
* <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME> (Optional) If is set it will overwrite the <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME> property described in the [access section](#3.2.1-access-configuration)
* <CONFIGURATION_ANCHOR_PATH> Path to the configuration anchor file, e.g. "/etc/xroad/configuration-anchor.xml"
*  <SIGN_CERT_PATH> should be given as path referring to sign certificates location.
*  <AUTH_CERT_PATH> should be given as path referring to auth certificate location.
* <SECURITY_SERVER_NAME> should be substituted with the installed security server name, e.g. ss1
* <OWNER_DISTINGUISHED_NAME_COUNTRY> should be ISO 3166-1 alpha-2 two letter code for server owner country. This is used in certificate generation.
* <OWNER_DISTINGUISHED_NAME_ORGANIZATION> should be set to server owner organization. This is used in certificate generation.
* <OWNER_MEMBER_CLASS> should be substituted with the member class obtained from the Central Server, e.g. GOV.
* <OWNER_MEMBER_CODE> should be substituted with the member code obtained from the Central Server, e.g. 1234.
* <SERVER_CODE> should be substituted with the server code of the installed security server, e.g. SS1
* <SOFT_TOKEN_ID> default software token ID, normally 0 (zero).
* <SOFT_TOKEN_PIN> should be substituted with a desired numeric pin code.
* <SECURITY_SERVER_EXTERNAL_FQDN> externally accessible FQDN for the security server. It's applied to the security server certificates.
* <SECURITY_SERVER_INTERNAL_FQDN_OR_IP> should be substituted with internal IP address or host name of the installed security server, e.g. ``ss1``
* <SSH_USER_OS_ENV_VAR_NAME> (Optional) If set, it will overwrite the <SSH_USER_OS_ENV_VAR_NAME> property described in the [access section](#3.2.1-access-configuration)
* <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME> (Optional) If set, it will overwrite the <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME> property described in the [access section](#3.2.1-access-configuration)

#### 3.2.3 Client Configuration

The security server client information is configured in this section. It is possible to set up a list of subsystems belonging to the owner member
configured in the [security server configuration](#322-security-servers-configuration) or add them to a new member as described
in [8 Multitenancy](#8-multitenancy).
```
clients:
	- member_class: <MEMBER_CLASS>
	  member_code: <MEMBER_CODE>
	  member_name: <MEMBER_NAME>
	  subsystem_code: <SUBSYSTEM_CODE>
	  connection_type: <CONNECTION_TYPE>
```

* <MEMBER_CLASS> should be substituted with the member class obtained from the Central Server, e.g. GOV.
It must have the same value as <OWNER_MEMBER_CLASS> if is a subsystem of the owner client.
* <OWNER_MEMBER_CODE> should be substituted with the member code obtained from the Central Server, e.g. 1234
It must have the same value as <OWNER_MEMBER_CLASS> if is a subsystem of the owner client.
* <MEMBER_NAME> should be substituted with the member name obtained from the Central Server, e.g. COMPANY.
It must have the same value as <OWNER_DISTINGUISHED_NAME_ORGANIZATION>  if is a subsystem of the owner client.
* <SUBSYSTEM_CODE> (Optional, not required for members) X-Road member/client subsystem code.
* <CONNECTION_TYPE> Connection protocol selection, from among ``HTTP``, ``HTTPS``, ``HTTPS_NO_AUTH``.

#### 3.2.3 Service Configuration

In this section services with type ``OPENAPI3``, ``REST``, ``WSDL`` can be configured by adding a service description
with parameters ``url``, ``rest_service_code``, ``type`` and ``access``. In order to provide access to the services added with that
service description to different subsystems, the parameter ``access`` should contain a list of subsystem codes. To configure specific services
described with the service description, the parameters ``service_code`` and ``access`` must be configured in the section ``services``. 
```
service_descriptions:
	- url: <SERVICE_DESCRIPTION_URL>
	  rest_service_code: <REST_SERVICE_CODE>
	  type: <SERVICE_TYPE>
	  access:
		- <SERVICE_DESCRIPTION_ACCESS>
	  url_all: <SERVICE_URL_FOR_ALL>
	  timeout_all: <SERVICE_TIMEOUT_FOR_ALL>
	  ssl_auth_all: <SERVICE_USE_SSL_AUTH_FOR_ALL>
	  services:
            - service_code: <SERVICE_CODE>
              access:
                - <SERVICE_ACCESS>
              timeout: <SERVICE_TIMEOUT>
              ssl_auth: <SERVICE_USE_SSL_AUTH>
              url: <SERVICE_URL>
          endpoints:
			- path: <ENDPOINT_PATH>
			  method: <ENDPOINT_METHOD>
			  access: 
			    - <ENDPOINTS_ACCESS>
```
<strong>Service description (Optional):</strong>

* <SERVICE_DESCRIPTION_URL> URL for service description.
* <REST_SERVICE_CODE> rest service code, not used for WSDL services.
* <SERVICE_TYPE> type of service, value from ``OPENAPI3``, ``REST``, ``WSDL``.
* <SERVICE_DESCRIPTION_ACCESS> (Optional) list of subsystems ids, composed by <INSTANCE>:<MEMBER_CLASS>:<MEMBER_CODE>:<SUBSYSTEM_CODE>, or security serverver owners composed 
by <INSTANCE>:security-server-owners.
* <SERVICE_URL_FOR_ALL> boolean value determining if the URL prefix should be applied for all the services.
* <SERVICE_TIMEOUT_FOR_ALL> boolean value specifying if the timeout should be applied for all the services in the service description.
* <SERVICE_USE_SSL_AUTH_FOR_ALL> boolean value specifying whether SSL authentication should be used for all the services in the service description.

<strong>Services (Optional):</strong>
It's possible to create services manually but usually it's not required because they are parsed from the service descriptions automatically. Adding a service manually is needed when a service description isn't available, there is a need to customize the access rights, or there is a need to customize the parameters.

* <SERVICE_CODE> code for single service.
* <SERVICE_ACCESS> (Optional) same as <SERVICE_DESCRIPTION_ACCESS>, if its defined, it will overwrite the values defined in <SERVICE_DESCRIPTION_ACCESS>
for the single service.
* <SERVICE_TIMEOUT> timeout for service in seconds.
* <SERVICE_USE_SSL_AUTH> boolean value for specifying whether SSL authentication should be used.
* <SERVICE_URL> URL for single service

<strong>Endpoints (Optional):</strong>
The endpoints are only available for service descriptions of type REST or OPENAPI3.

* <ENDPOINT_PATH> path for the endpoint.
* <ENDPOINT_METHOD> method for the endpoint (GET, POST, PUT...)
* <ENDPOINTS_ACCESS> (Optional) same as <SERVICE_ACCESS> or <SERVICE_DESCRIPTION_ACCESS> but for grant endpoint access rights.

### 3.3 Different ways of using the configuration file

* default configuration in ``config/xrdsst.yml``
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
For performing the configuration step by step instead, please start from [4.3 Initializing the security server](#43-initializing-the-security-server)


### 4.2 X-Road Security Server  Toolkit commands

* Access rights: All commands require at least the role XROAD_SYSTEM_ADMINISTRATOR.

#### 4.2.1 Creating admin user command

X-Road admin user can be created with 
```
xrdsst user create-admin
```
Configuration parameters involved are described in [3.2.1 Access Configuration](#321-access-configuration). Specifically, the administrator user will have the `name: password` defined in the property `admin_credentials`.


Note: This is an optional step in the configuration process and should only be run if the admin user has not been created before. 
      SSH (SSH user and a private key) is used for creating the admin user. If the admin user has been created before, then it is 
      enough to just add the credentials to the configuration file as ``admin_credentials`` and this step can be skipped totally.

**It is a security risk to store the SSH access-related credentials into to configuration file as plain text.**

#### 4.2.2 Initializing the security server command

* Access rights: XROAD_SYSTEM_ADMINISTRATOR, XROAD_SECURITY_OFFICER

Initializes the security server and upload the configuration anchor by typing:
```
xrdsst init
```

Configuration parameters involved are the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)

#### 4.2.3 Token commands

Configuration parameters related to tokens involved are `software_token_id` and `software_token_pin` the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)

##### 4.2.3.1 Token login command

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Default software token login can be logged on with:
```
xrdsst token login
```
Configuration parameters involved are `software_token_id` and `software_token_pin` the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)

##### 4.2.3.2 Token list

* Access rights: Any

All tokens known to security server can be listed with:
```
xrdsst token list
```

##### 4.2.3.3 Token init-keys

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER or XROAD_SECURITY_OFFICER

Token keys for authentication and signatures can be created with:
```
xrdsst token init-keys
``` 
Creates two keys and generates corresponding certificate signing requests (one for authentication, other for signing).
The key labels used are conventionally with suffixes ``default-auth-key`` and ``default-sign-key``, if
those already exist, they will not be duplicated and command acts as no-op for such security server.
If we are using [Multitenancy](#8-multitenancy) this command will also create an extra key and signing request with the 
key label suffix ``default-sign-key_<MEMBER_CODE>_<MEMBER_NAME>``

#### 4.2.4 Timestamp commands

Configuration parameters involved are the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)


##### 4.2.4.1 Timestamp init

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

Single timestamping service approved for use in central server can be configured for security server by invoking ``timestamp`` subcommand as: 
```
xrdsst timestamp init
```

##### 4.2.4.2 Timestamp list approved

* Access rights: Any

List the available timestamp services approved for the security server
```
xrdsst timestamp list-approved
```

##### 4.2.4.3 Timestamp list configured

* Access rights: Any

List the available timestamp services configured for the security server
```
xrdsst timestamp list-configured
```

#### 4.2.5 Certificate management commands

These commands allow us to perform certificate operations of a security server.

##### 4.2.5.1 Certificate download CSRS

* Access rights: XROAD_SECURITY_OFFICER

Certificate signing requests can be downloaded with 
```
xrdsst cert download-csrs
```

##### 4.2.5.2 Certificate import

* Access rights: XROAD_SYSTEM_ADMINISTRATOR, XROAD_REGISTRATION_OFFICER and XROAD_SECURITY_OFFICER

Configuration parameters involved are the `certificates` list described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)
In the `certificates` list we must set the path for the signed SIGN and AUTH certificates previously downloaded then can be imported with:
```
xrdsst cert import
```

##### 4.2.5.3 Certificate registration

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

Register the certificates previously imported in the central server with:
```
xrdsst cert register
```

##### 4.2.5.4 Certificate activation

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

AUTH certificate activation can be done with:
```
xrdsst cert activate
```

##### 4.2.5.5 Download internal TSL certificates

* Access rights: XROAD_SYSTEM_ADMINISTRATOR or XROAD_SECURITY_OFFICER or XROAD_REGISTRATION_OFFICER or XROAD_SERVICE_ADMINISTRATOR

Internal TSL certificates can be downloaded with:
```
xrdsst cert download-internal-tsl
```
This command will save a zip file in the `/tmp/` folder containing the public and private keys of the internal TSL certificates.

#### 4.2.5 Client management commands

Client are managed with ``xrdsst client`` subcommands.
Configuration parameters involved are the `certificates` list described in [3.2.3 Clients Configuration](#323-client-configuration)

##### 4.2.5.1 Client add

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER

New subsystem or members can be added with:
```
xrdsst client add
```

##### 4.2.5.2 Client register

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER

Subsystems and new members registration in central server can proceed with:
```
xrdsst client register
```

##### 4.2.5.3 Client update

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER

Subsystem parameters can be updated with:
```
xrdsst client update
```

#### 4.2.6 Service management commands

Services and service descriptions are managed with ``xrdsst service`` subcommands.
Configuration parameters involved are the described in [3.2.3 Services Configuration](#323-services-configuration)

##### 4.2.6.1 Service add description

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Adding REST/OPENAPI3/WSDL service can be done with:
```
xrdsst service add-description
```
For REST / OPENAPI3 type services, this command will auto-generate a service with the property name `rest_service_code`. 

For WSDL type services it is not necessary to fill in the `rest_service_code` property, when adding the description the services discovered in the WSDL URL are autogenerated.

The default values of the service properties will be of 60 for the `timeout` and False for the` ssl_auth`.

We must include the services when we want to modify any of their properties (for all or for single one).

##### 4.2.6.2 Service add access rights

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Access rights for a service can be done with:
```
xrdsst service add-access
```
This command will add for all the services the access rights defined in the property `access` of the` service_descriptions` section
except in the case that the `access` property of the `services` section is filled, in that case, this list will overwrite 
the access rights for the individual service. 

##### 4.2.6.3 Enable service

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Enabling the service description can be done with:
```
xrdsst service enable-description
```

##### 4.2.6.4 Service update parameters

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Updating the service parameters can be done with:
```
xrdsst service update-parameters
```
This command will update the parameters of the single services added to the configuration file, or it will update the parameters
for all the services in the description if the boolean parameters are set to True.

##### 4.2.6.5 Service apply

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

It is possible to run sequentially all the service commands described before in [4.2.6 Service management commands](#426-service-management-commands)
with:
```
xrdsst service apply
```
This command will execute the commands: ``xrdsst service add-description``, ``xrdsst service enable-description``, ``xrdsst service add-access``, ``xrdsst service update-parameters``.

#### 4.2.7 Endpoint management

Endpoints are managed with ``xrdsst endpoint`` subcommands.

Configuration parameters involved are the ``endpoint`` section described in [3.2.3 Services Configuration](#323-services-configuration)

Endpoints are only available for service types REST and OPENAPI3.

##### 4.2.7.1 Endpoint add

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Adding endpoints to a service can be done with:
```
xrdsst endpoint add
```
Endpoints in service type OPENAPI3 are autogenerated, so, the endpoints defined in the configuration 
will be created together with the autogenerated ones.

##### 4.2.7.2 Endpoint add access rights

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Access rights for a single endpoint can be add with:
```
xrdsst endpoint add-access
```

## 5 Failure recovery and interpretation of errors
> "In failure, software reveals its structure" -- Kevlin Henney

It is essential to have a firm grip on both *what* is going and *where* in the
distributed system to fix upcoming problems encountered while using the toolkit.
For single configuration operations, it is important that those are performed in
non-conflicting order, e.g. it is impossible to perform most token operations
before the token has been logged in. If this order is not respected, the output
from the application will refer to the commands which successful application
is required to be completed beforehand, e.g.:

```sh
$ xrdsst -c brandnew.yaml client add
SKIPPED 'ss8': has ['init', 'token login', 'token init-keys'] performed but also 
needs ['cert import', 'cert register', 'cert activate'] completion before continuing
with requested ['client add']
```
lists three certificate operations (``import``, ``register``, ``activate``)
that should be then given in specified order, and if these have been completed
succesfully, the desired command should also be ready for either successful execution
or a failure for completely new reason.

### 5.1 Configuration flow

As demonstrated above, the operation order is most relevant to understand when
using single-operations for (re-)applying some part of security server configuration.
When using the ``xrdsst apply`` autoconfiguration, operations will already be performed
in correct functional order.

The operation graph in its dependency order is shown below, node names matching
the single configuration operation commands of the toolkit. Non-continuous borders
either mark commands that are not part of autoconfiguration (``cert download-csrs``) or
take place entirely outside of the toolkit, like getting certificate signing requests
(CSRs) signed at the approved certificate authority (CA).


![Flow](img/flow.svg)

### 5.2 First-run failures

When autoconfiguration for the server fails at step that is required prerequisite
for successive operations, current server configuration will be stopped with error
message and current server status report shown (as from ``xrdsst status``), before
continuing with configuration of other servers, if any are present in the used
configuration.

Typical end for the first autoconfiguration run for a single server usually
is an error message that asks to download and sign the CSRs to acquire certificates
that are to be added to the configuration file:

```sh
$ xrdsst -c brandnew.yaml apply
API key "d8cd2476-c8dc-420a-bcc2-c8636766661b" for security server ss8 created.
AUTO ['init']->'ss8'
Uploading configuration anchor for security server: ss8
Upload of configuration anchor from "/home/user/demo-anchor.xml" successful
Initializing security server: ss8
Security server "ss8" initialized
# ..
# timestamp service initialization and token login operation output omitted here
# ...
AUTO ['token init-keys']->'ss8'
Generating software token 0 key labelled 'ss8-default-auth-key' and AUTH CSR:
Generating software token 0 key labelled 'ss8-default-sign-key' and SIGN CSR:
Created AUTHENTICATION CSR 'A75BC748F158319B7DC73FD85D9C7DBB373F91B5' for key 'D46DF41D2BE2FE2381A45DA312FA205B0531CA3C' as 'ss8-default-auth-key'
Created SIGNING CSR '681EAB6E3A6C53448B468B4A61E1E66086FCE44A' for key '2C3C75DABE875EA1F1DBE5A7368838A861288A16' as 'ss8-default-sign-key'
AUTO ['cert import']->'ss8'
SKIPPED 'ss8':
        'ss8' [cert import]: 'certificates' missing required value. Get CSRs ['cert download-csrs'] signed at approved CA and fill element accordingly.
AUTO ['cert import'] completion was NOT detected.
Some operations require waiting for global configuration renewal.
Next AUTO operation would have been ['cert register'].
AUTO ['status']->'ss8' AT THE END OF AUTOCONFIGURATION.

╒══════════════════╤═════════════════════════╤══════════════════════╤════════════════════╤══════════╤═════════════╤══════════╤══════════╤═════════╕
│ GLOBAL           │ SERVER                  │ ROLES                │ INIT               │ TSAS     │ TOKEN       │ KEYS     │ CSRS     │ CERTS   │
╞══════════════════╪═════════════════════════╪══════════════════════╪════════════════════╪══════════╪═════════════╪══════════╪══════════╪═════════╡
│ FAIL (INTERNAL)  │ ss8                     │ System Administrator │ ANCHOR INITIALIZED │ Test TSA │ ID 0        │ SIGN (1) │ SIGN (1) │         │
│ LAST 130913 0317 │ VER 6.25.0              │ Service Administrator│ CODE INITIALIZED   │          │ softToken-0 │ AUTH (1) │ AUTH (1) │         │
│ NEXT 131013 0317 │ DEV:GOV:9876:UNS-BRNDNW │ Registration Officer │ OWNER INITIALIZED  │          │ STATUS OK   │ 2 KEYS   │ 2 CSRS   │         │
│                  │                         │ Security Officer     │ TOKEN INITIALIZED  │          │ LOGIN YES   │          │          │         │
╘══════════════════╧═════════════════════════╧══════════════════════╧════════════════════╧══════════╧═════════════╧══════════╧══════════╧═════════╛
```

To continue from there, ``xrdsst cert download-csrs`` single operation should be
used to download certificate signing requests, which should then be submitted to
X-Road approved CA for signing. Global status failure (``INTERNAL``) reported in
the first status column here is also typical of the first run, as the state
synchronizations have not been completed yet, which should resolve in short time, at
the ``NEXT`` update time reported -- in any case long before the signed CSRs are
acquired from the approved CA.

Other columns in the given sample indicate that all operations have been success:
 * ``SERVER`` shows server information successfully acquired.
 * ``ROLES`` lists four roles for used API key, enough to execute all toolkit operations.
 * ``INIT`` lists four successful initializations.
 * ``TSAS`` shows single timestamping service selected successfully.
 * ``TOKEN`` lists sofware token ID 0, its name, functioning status and succesful login.
 * ``KEYS`` shows that token does have both SIGN and AUTH keys generated.
 * ``CSRS`` shows that certificate signing requests for corresponding token keys were created.

### 5.3 Configuration file errors

#### 5.3.1 Malformed YAML

Badly formed YAML results in parse error which gives exact line and column numbers to
indicate the error location. With hierarchical configuration, several of these can be given,
usually the last one reported refers to the actual error, e.g. misaligned client block at
line 32 below:

```yaml
# ... SNIPPED
security_server:                                                     # line 11
- api_key: TOOLKIT_API_KEY                                           # line 12
# ... SNIPPED
  clients:                                                           # line 27
    - member_class: GOV                                              # line 28
      member_code: 9876                                              # line 29
      subsystem_code: GOOD_SUB                                       # line 30
      connection_type: HTTPS                                         # line 31
   - member_class: GOV                                               # line 32
      member_code: 9876                                              # line 33
      subsystem_code: FAILED_SUB                                     # line 34
      connection_type: HTTPS                                         # line 35
# ... SNIPPED
```

is reported as:

```sh
Error parsing config: while parsing a block mapping
  in "block-err.yaml", line 12, column 3
expected <block end>, but found '<block sequence start>'
  in "block-err.yaml", line 32, column 4
```

indicating that object starting in 3rd column of line 12 could not be formed
successfully, concrete error being misaligned block at 4th column of line 32.

#### 5.3.2 Other configuration file errors

Configuration can also be rejected for syntax errors (misspelled elements) or
due to violation of logical constraints (e.g. multiple servers defined with the
same URL).

These messages should be mostly self-explanatory. In case of multiple elements,
missing some required fields, the **one**-based index of the erroneous element is
given, e.g:

```
security_server[1] missing required 'name' definition.
security_server[1] missing required 'url' definition.
security_server[3] missing required 'url' definition.
```
indicates that 1st and 3rd security server definitions with specified errors,
(NOT 2nd and 4th).

### 5.4 Errors from internal and external systems

As base configuration for the server gets sorted out, the likelihood of encountering
errors originating from other parts of the distributed system increases. Unless these
parts also happen to be under the control of the toolkit user, it means that failure
usually cannot be addressed immediately (though it might resolve with time) and most
direct way to proceed towards resolve will be to contact the IT-department or
administrators of the organization responsible for the X-Road system from where the error
originates.

Toolkit itself tries to point out the error source, CLIENT proxy errors happen straight
at the configured server and can be often addressed immediately, but SERVER proxy 
or Service PROVIDER errors will require reaching out externally. For client proxy errors
that are more common, toolkit offers additional messages about their possible causes and
sometimes even hints of possible solutions. For server proxy errors, as much of the
information is shown as acquired from SERVER proxy or service PROVIDER information
system behind SERVER proxy:

```sh
$ xrdsst client register
# ... SNIPPED ...
FAILED
  PUT /clients/{id}/register @ clients_api.py#register_client <- client.py#remote_register_client
  INTERNAL_SERVER_ERROR (500), error_code 'core.Server.ServerProxy.ServiceDisabled'
  ['Service SERVICE:DEV/GOV/9876/MANAGEMENT/clientReg is disabled: some reason']
  Security server (SERVER Proxy) has disabled the service, maybe temporarily.


  ╒═Trusted Network═╕                          . INTERNET .                         ╒═Trusted Network══╕
  │                 │      ╒══════════╕       .             .     ╒══════════╕      │                  │
  │                 │      │ Security │      |               |    │ Security │      │/ Service (REST)  │
  │  xrdsst (REST) -│- ->- │\ Server /│- ->- | - - ->- - - - | ->-│\ Server /│- ->- │                  │
  │                 │      │ - ->- -  │       .             .     │ - ->- -  │      │\ Service (SOAP)  │
  │                 │      ╘══════════╛        .          .       ╘══════════╛      │                  │
  ╘═════════════════╛                            INTRANET                           ╘══════════════════╛
  
   Service CONSUMER        CLIENT Proxy                           SERVER Proxy        Service PROVIDER

```

Above is example toolkit output for a case where management services in separate
security server have been disabled and ``xrdsst client register`` unable to proceed.
This is one of these cases where management services security server is somewhat 
likely to belong to the same organization, and thus the error might be
sorted out inside organization, getting the services enabled again. In any case,
the key to successfully resolving such situations is to pay careful attention
to the error messages and accompanying ASCII diagram with message flow, to not
spend time at searching for the problem in the wrong places.

### 5.5 Recovery from misconfiguration
This version of toolkit does not yet offer explicit support for backup and restore
operations of the security server (scheduled for next release of the toolkit). In
case something goes so wrong that way out or way back cannot be seen, it is possible
to use nightly backups that are kept at security server to revert to earlier state.
Overview of existing automatic backups is accessible from web administration console
of the security server, in the "Settings" menu. More information about functionality
can be found in [UG-SS](#Ref_SS-UG).


## 6 Load balancer setup

 It is possible to setup a Load balancer environment described in [X-Road: External Load Balancer Installation Guide](https://github.com/nordic-institute/X-Road/blob/develop/doc/Manuals/LoadBalancing/ig-xlb_x-road_external_load_balancer_installation_guide.md) 
 and configure it using the toolkit.

Under the [X-Road](https://github.com/nordic-institute/X-Road) project there are ansible 
scripts prepared to install the cluster, for doing that we must follow the instructions 
[Security server cluster setup](https://github.com/nordic-institute/X-Road/tree/develop/ansible/ss_cluster#security-server-cluster-setup).

Once the cluster is ready we can use the toolkit to configure the Load Balancer setup, for doing that, we must configure the Primary Security Server as any other single Security Server, setting in the
`SECURITY_SERVER_INTERNAL_FQDN_OR_IP` property with the FQDN belonging to the Primary.

## 7 Using the Toolkit to configure highly available services using the built-in security server internal load balancing

In order to configure a highly available service using the built-in security server load balancing, at least two security
servers need to be configured with the same subsystem/service.

An example configuration file to be used:

```
admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
ssh_access:
  user: <SSH_USER_OS_ENV_VAR_NAME>
  private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
security_server:
- api_key: <API_KEY_ENV_VAR_NAME>
  api_key_url: https://localhost:4000/api/v1/api-keys
  admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
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
  fqdn: <SECURITY_SERVER_EXTERNAL_FQDN>
  url: https://<SECURITY_SERVER_INTERNAL_FQDN_OR_IP>:4000/api/v1
  ssh_user: <SSH_USER_OS_ENV_VAR_NAME>
  ssh_private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
  clients:
    - member_class: <MEMBER_CLASS>
      member_code: <MEMBER_CODE>
      member_name: <MEMBER_NAME>
      subsystem_code: <SUBSYSTEM_CODE>
      connection_type: <CONNECTION_TYPE>
- api_key: <API_KEY_ENV_VAR_NAME>
  api_key_url: https://localhost:4000/api/v1/api-keys
  admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
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
  fqdn: <SECURITY_SERVER_EXTERNAL_FQDN>
  url: https://<SECURITY_SERVER_INTERNAL_FQDN_OR_IP>:4000/api/v1
  ssh_user: <SSH_USER_OS_ENV_VAR_NAME>
  ssh_private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
  clients:
    - member_class: <MEMBER_CLASS>
      member_code: <MEMBER_CODE>
      member_name: <MEMBER_NAME>
      subsystem_code: <SUBSYSTEM_CODE>
      connection_type: <CONNECTION_TYPE>
```

The ``clients`` section should have the same values used for the following parameters:
 * ``member_class`` member class of a subsystem.
 * ``member_code`` member code of a subsystem.
 * ``member_name`` member name of a subsystem.
 * ``subsystem_code`` X-Road member/client subsystem code.
 * ``connection_type`` Connection protocol selection, from among ``HTTP``, ``HTTPS``, ``HTTPS_NO_AUTH``.

When the placeholders in the configuration file have been amended with proper values, please start from 
[4 Running the X-Road Security Server Toolkit](#4-running-the-x-road-security-server-toolkit) and continue until(included) [4.9 Client management](#49-client-management)

## 8 Multitenancy
It's possible to add another members and subsystem to a security server using the toolkit.
For doing that we need to add the members and subsystems in the clients section of the configuration
file. 
For adding a new member we must delete the properties 'service_descriptions' and 'subsystem_code'.
For example if we have the owner member 'ORG/111/ORGANIZATION/SUB' and want to add the new member 'COM/12345/COMPANY', and the subsystem 'COM/12345/COMPANY/SUB' we must fill the
configuration file like this:

```
[...]
  clients:
    - member_class: ORG
      member_code: 111
      member_name: ORGANIZATION
      subsystem_code: SUB
      connection_type: HTTP
      service_descriptions:
        [...]
    - member_class: COM
      member_code: 12345
      member_name: COMPANY
      connection_type: HTTP	
    - member_class: COM
      member_code: 12345
      member_name: COMPANY
      subsystem_code: SUB
      connection_type: HTTP
      service_descriptions:	
      	[...]	    
```

Running the `apply` command will create the new member, create the certificate and register it,
but if we want to do step by step we need to: 
- Add the new members/subsystems with the command:
```
xrdsst client add-client
```
- Create the SIGN key and CSRS for the new member
```
xrdsst token init-keys
```

- Download this CSRS with the command:
```
xrdsst cert download-csrs 
```
Sign it and add it to the list of certificates in the configuration:
```
[...]
security_server:
- api_key: <API_KEY_ENV_VAR_NAME>
  api_key_url: https://localhost:4000/api/v1/api-keys
  admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
  configuration_anchor: /path/to/configuration-anchor.xml
  certificates:
    - /path/to/signcert
    - /path/to/authcert
    - /path/to/signcert_new_member
[...]
```
- Import the certificate:
```
xrdsst cert import
```
- Register the new member by running the command:
```
xrdsst client register
```

## 9 Renew expiring certificates

It is recommended to renew the certificates in advance before they expire. You can check the expiration date through the 
UI in the tab <strong>KEYS AND CERTIFICATE</strong> => <strong>SIGN AND AUTH KEYS</strong> column <strong>Expires</strong>.
To renew the certificates we must:

1. Go to the UI and generate new CRS keys for the certificates we want to renew:
2. Download and sign the new certificates.
3. Add the signed certificates to the [certificates list](#322-security-servers-configuration) of the security server 
   in the configuration file.
4. Import the certificates by running the [certificate import](#4252-certificate-import) command.
5. Activate the certificates by running the [certificate activation](#4254-certificate-activation) command.
6. Register the new certificates by running the [certificate registration](#4253-certificate-registration) command.
7. Wait until the new certificates have the OCSP is Good state and the Status in Registered. We can check this
   through the UI in the tab <strong>KEYS AND CERTIFICATE</strong> => <strong>SIGN AND AUTH KEYS</strong>. 
   It's recommended to wait at least one day so that the new certificates can be distributed for the access server does not crash.
8. Unregister and delete the old certifcates through the UI.

