# X-Road Security Server Toolkit User Guide
Version: 2.3.3
Doc. ID: XRDSST-CONF

---

## Version history <!-- omit in toc -->
| Date       | Version | Description                                                                                                                   | Author           |
|------------|--------|-------------------------------------------------------------------------------------------------------------------------------|-------------------|
| 10.11.2020 | 1.0.0  | Initial draft                                                                                                                 | Bert Viikmäe      |
| 12.11.2020 | 1.1.0  | Documentation of initialization functionality                                                                                 | Bert Viikmäe      |
| 16.11.2020 | 1.1.1  | Documentation of token login functionality                                                                                    | Taimo Peelo       |
| 08.12.2020 | 1.1.2  | Documentation of token key initializations                                                                                    | Taimo Peelo       |
| 15.12.2020 | 1.1.3  | Documentation of api-key parameterization                                                                                     | Bert Viikmäe      |
| 22.12.2020 | 1.1.4  | Brief notes on certificate management                                                                                         | Taimo Peelo       |
| 30.12.2020 | 1.1.5  | Note on certificate activation                                                                                                | Taimo Peelo       |
| 12.01.2021 | 1.1.6  | Notes on client management                                                                                                    | Taimo Peelo       |
| 20.01.2021 | 1.1.7  | Notes on adding service descriptions                                                                                          | Bert Viikmäe      |
| 27.01.2021 | 1.1.8  | Notes on enabling service descriptions                                                                                        | Bert Viikmäe      |
| 03.02.2021 | 1.1.9  | Notes on server status query                                                                                                  | Taimo Peelo       |
| 17.02.2021 | 1.2.0  | Updates to the user guide                                                                                                     | Bert Viikmäe      |
| 22.02.2021 | 1.2.1  | Update service management                                                                                                     | Bert Viikmäe      |
| 23.02.2021 | 1.2.2  | Update service management                                                                                                     | Bert Viikmäe      |
| 17.03.2021 | 1.2.3  | Describe failure interpretation and recovery                                                                                  | Taimo Peelo       |
| 22.03.2021 | 1.2.4  | Default configuration from config/base.yaml -> config/xrdsst.yml                                                              | Taimo Peelo       |
| 26.03.2021 | 1.2.5  | Add 'fqdn' key for Security Server, fix service field descriptions                                                            | Taimo Peelo       |
| 31.03.2021 | 1.2.6  | Refactorization of configuration file related to SSH and api key parameters                                                   | Bert Viikmäe      |
| 01.04.2021 | 1.2.7  | Describe backup use, clarify toolkits' error interpretation role, remove undocumented ``api_key_roles`` configuration element | Taimo Peelo       |
| 05.04.2021 | 1.2.8  | Remove HTTP header value prefix from 'api_key' configuration element                                                          | Taimo Peelo       |
| 06.04.2021 | 1.2.9  | Describe different Security Server access possibilities                                                                       | Taimo Peelo       |
| 06.04.2021 | 1.2.10 | Notes on user management                                                                                                      | Bert Viikmäe      |
| 09.04.2021 | 1.2.11 | Added description about signing and verification of packages                                                                  | Bert Viikmäe      |
| 20.04.2021 | 1.3.0  | Substituting plain text secrets in configuration with environment variables                                                   | Bert Viikmäe      |
| 26.04.2021 | 1.3.1  | Added description about adding endpoints to the REST and OpenAPI services.                                                    | Alberto Fernandez |
| 27.04.2021 | 1.3.2  | Substituting plain text api key in configuration with environment variable                                                    | Bert Viikmäe      |
| 04.05.2021 | 1.3.3  | Added description about endpoint access                                                                                       | Alberto Fernandez |
| 10.05.2021 | 1.3.4  | Added Load Balancer setup description                                                                                         | Alberto Fernandez |
| 13.05.2021 | 1.3.5  | Added description about load-balancing                                                                                        | Bert Viikmäe      |
| 14.05.2021 | 1.3.6  | Notes on client management                                                                                                    | Bert Viikmäe      |
| 24.05.2021 | 1.3.7  | Added download-internal-tls command                                                                                           | Alberto Fernandez |
| 28.05.2021 | 1.3.8  | Added member name property  and multitenancy section                                                                          | Alberto Fernandez |
| 28.05.2021 | 1.3.9  | Update service management                                                                                                     | Bert Viikmäe      |
| 04.06.2021 | 1.3.10 | Refactor documentation                                                                                                        | Alberto Fernandez |
| 04.06.2021 | 1.3.11 | Added TLS certificates import                                                                                                 | Alberto Fernandez |
| 16.06.2021 | 1.3.12 | Added certificate list command description                                                                                    | Alberto Fernandez |
| 21.06.2021 | 2.0.0  | Notes on member management                                                                                                    | Bert Viikmäe      |
| 17.06.2021 | 2.0.1  | Added disable certificates command                                                                                            | Alberto Fernandez |
| 21.06.2021 | 2.0.2  | Added delete and unregister certificates command                                                                              | Alberto Fernandez |
| 22.06.2021 | 2.0.3  | Notes on member management                                                                                                    | Bert Viikmäe      |
| 25.06.2021 | 2.0.4  | Update service management with listing of service descriptions                                                                | Bert Viikmäe      |
| 25.06.2021 | 2.0.5  | Update service management with listing of service description services                                                        | Bert Viikmäe      |
| 28.06.2021 | 2.0.6  | Update renew certificates process                                                                                             | Alberto Fernandez |
| 30.06.2021 | 2.0.7  | Update service management with deletion of service descriptions                                                               | Bert Viikmäe      |
| 02.07.2021 | 2.0.8  | Update service management with update of service descriptions                                                                 | Bert Viikmäe      |
| 05.07.2021 | 2.0.9  | Update service management with refresh of service descriptions                                                                | Bert Viikmäe      |
| 05.07.2021 | 2.1.0  | Update service management with disabling of service descriptions                                                              | Bert Viikmäe      |
| 06.07.2021 | 2.1.1  | Add client unregister command                                                                                                 | Alberto Fernandez |
| 06.07.2021 | 2.1.2  | Add client delete command                                                                                                     | Alberto Fernandez |
| 09.07.2021 | 2.1.3  | Add listing and deletion of access rights for services                                                                        | Bert Viikmäe      |
| 13.07.2021 | 2.1.4  | Add local groups management                                                                                                   | Alberto Fernandez |
| 14.07.2021 | 2.1.5  | Add listing, creation and download of backups                                                                                 | Bert Viikmäe      |
| 15.07.2021 | 2.1.6  | Add deletion of backups                                                                                                       | Bert Viikmäe      |
| 16.07.2021 | 2.1.7  | Add restore from backups                                                                                                      | Bert Viikmäe      |
| 19.07.2021 | 2.1.8  | Add make owner command                                                                                                        | Alberto Fernandez |
| 16.07.2021 | 2.1.9  | Add list endpoints command                                                                                                    | Alberto Fernandez |
| 19.07.2021 | 2.2.0  | Add diagnostics management                                                                                                    | Bert Viikmäe      |
| 20.07.2021 | 2.2.1  | Add endpoint update and delete command                                                                                        | Alberto Fernandez |
| 22.07.2021 | 2.2.2  | Add endpoint list access and delete access commands                                                                           | Alberto Fernandez |
| 28.07.2021 | 2.2.3  | Add key management commands                                                                                                   | Alberto Fernandez |
| 29.07.2021 | 2.2.4  | Add CSR management commands                                                                                                   | Alberto Fernandez |
| 02.08.2021 | 2.2.5  | Add list instance command                                                                                                     | Alberto Fernandez |
| 03.08.2021 | 2.2.6  | Add Security Server list and version list commmands                                                                           | Alberto Fernandez |
| 04.08.2021 | 2.2.7  | Add client list command                                                                                                       | Alberto Fernandez |
| 09.08.2021 | 2.2.8  | Add tls certificate management commands                                                                                       | Alberto Fernandez |
| 10.08.2021 | 2.2.9  | Add certificate profiles support                                                                                              | Alberto Fernandez |
| 17.08.2021 | 2.3.0  | Pre-release documentation updates                                                                                             | Bert Viikmäe      |
| 26.07.2022 | 2.3.1  | Editorial updates                                                                                                             | Petteri Kivimäki  |
| 04.10.2022 | 2.3.2  | Updated documentation related to handover changes                                                                             | Raido Kaju        |
| 13.10.2022 | 2.3.3  | Update installation instructions regarding NIIS Artifactory                                                                   | Raido Kaju        |

## Table of Contents <!-- omit in toc -->

<!-- toc -->
<!-- vim-markdown-toc GFM -->

* [License](#license)
* [1. Introduction](#1-introduction)
  * [1.1 Target Audience](#11-target-audience)
  * [1.2 References](#12-references)
* [2. Installation](#2-installation)
* [2.1 Prerequisites to Installation](#21-prerequisites-to-installation)
* [2.2 Installation](#22-installation)
* [3 Configuration of X-Road Security Server](#3-configuration-of-x-road-security-server)
  * [3.1 Prerequisites to Configuration](#31-prerequisites-to-configuration)
    * [3.1.1 Toolkit access to Security Servers](#311-toolkit-access-to-security-servers)
      * [3.1.1.1 Using API keys](#3111-using-api-keys)
      * [3.1.1.2 Using SSH](#3112-using-ssh)
  * [3.2 Format of configuration file](#32-format-of-configuration-file)
    * [3.2.1 Access Configuration](#321-access-configuration)
    * [3.2.2 Security Servers Configuration](#322-security-servers-configuration)
    * [3.2.3 Client Configuration](#323-client-configuration)
    * [3.2.3 Service Configuration](#323-service-configuration)
  * [3.3 Different ways of using the configuration file](#33-different-ways-of-using-the-configuration-file)
* [4 Running the X-Road Security Server Toolkit](#4-running-the-x-road-security-server-toolkit)
   * [4.1 The single command fully automatic configuration of Security Servers listed in configuration file](#41-the-single-command-fully-automatic-configuration-of-security-servers-listed-in-configuration-file)
   * [4.2 X-Road Security Server  Toolkit commands](#42-x-road-security-server--toolkit-commands)
      * [4.2.1 Creating admin user command](#421-creating-admin-user-command)
      * [4.2.2 Initializing the Security Server command](#422-initializing-the-security-server-command)
      * [4.2.3 Token commands](#423-token-commands)
         * [4.2.3.1 Token login command](#4231-token-login-command)
         * [4.2.3.2 Token list](#4232-token-list)
         * [4.2.3.3 Token init-keys](#4233-token-init-keys)
         * [4.2.3.4 Token create-new-keys](#4234-token-create-new-keys)
      * [4.2.4 Timestamp commands](#424-timestamp-commands)
         * [4.2.4.1 Timestamp init](#4241-timestamp-init)
         * [4.2.4.2 Timestamp list approved](#4242-timestamp-list-approved)
         * [4.2.4.3 Timestamp list configured](#4243-timestamp-list-configured)
      * [4.2.5 Certificate management commands](#425-certificate-management-commands)
         * [4.2.5.1 Certificate download CSRS](#4251-certificate-download-csrs)
         * [4.2.5.2 Certificate import](#4252-certificate-import)
         * [4.2.5.3 Certificate registration](#4253-certificate-registration)
         * [4.2.5.4 Certificate activation](#4254-certificate-activation)
         * [4.2.5.5 List certificates](#4255-list-certificates)
         * [4.2.5.6 Certificate disable](#4256-certificate-disable)
         * [4.2.5.7 Certificate unregister](#4257-certificate-unregister)
         * [4.2.5.8 Certificate delete](#4258-certificate-delete)
      * [4.2.6 Client management commands](#426-client-management-commands)
         * [4.2.6.1 Client add](#4261-client-add)
         * [4.2.6.2 Client register](#4262-client-register)
         * [4.2.6.3 Client update](#4263-client-update)
         * [4.2.6.4 Client import TLS certificates](#4264-client-import-tls-certificates)
         * [4.2.6.5 Client unregister](#4265-client-unregister)
         * [4.2.6.6 Client delete](#4266-client-delete)
         * [4.2.6.7 Client change owner](#4267-client-change-owner)
         * [4.2.6.8 Client list](#4268-client-list)
      * [4.2.7 Service management commands](#427-service-management-commands)
         * [4.2.7.1 Service add description](#4271-service-add-description)
         * [4.2.7.2 Service add access rights](#4272-service-add-access-rights)
         * [4.2.7.3 Enable service](#4273-enable-service)
         * [4.2.7.4 Service update parameters](#4274-service-update-parameters)
         * [4.2.7.5 Service list descriptions](#4275-service-list-descriptions)
         * [4.2.7.6 Service list services](#4276-service-list-services)
         * [4.2.7.7 Service delete descriptions](#4277-service-delete-descriptions)
         * [4.2.7.8 Service update descriptions](#4278-service-update-descriptions)
         * [4.2.7.9 Service refresh descriptions](#4279-service-refresh-descriptions)
         * [4.2.7.10 Service disable descriptions](#42710-service-disable-descriptions)
         * [4.2.7.11 Service list access rights for services](#42711-service-list-access-rights-for-services)
         * [4.2.7.12 Service delete access rights for services](#42712-service-delete-access-rights-for-services)
         * [4.2.7.13 Service apply](#42713-service-apply)
      * [4.2.8 Endpoint management](#428-endpoint-management)
         * [4.2.8.1 Endpoint add](#4281-endpoint-add)
         * [4.2.8.2 Endpoint add access rights](#4282-endpoint-add-access-rights)
         * [4.2.8.3 Endpoint list](#4283-endpoint-list)
         * [4.2.8.4 Endpoint update](#4284-endpoint-update)
         * [4.2.8.5 Endpoint delete](#4285-endpoint-delete)
         * [4.2.8.6 Endpoint list access](#4286-endpoint-list-access)
         * [4.2.8.7 Endpoint delete access rights](#4287-endpoint-delete-access-rights)
      * [4.2.9 Member management](#429-member-management)
         * [4.2.9.1 Member find](#4291-member-find)
         * [4.2.9.2 Member list member classes](#4292-member-list-member-classes)
      * [4.2.10 Local groups management](#4210-local-groups-management)
         * [4.2.10.1 Local groups add](#42101-local-groups-add)
         * [4.2.10.2 Local groups add members](#42102-local-groups-add-members)
         * [4.2.10.3 Local groups list](#42103-local-groups-list)
         * [4.2.10.4 Local groups delete](#42104-local-groups-delete)
         * [4.2.10.5 Local groups member delete](#42105-local-groups-member-delete)
      * [4.2.11 Backup management](#4211-backup-management)
         * [4.2.11.1 Backup list](#42111-backup-list)
         * [4.2.11.2 Backup add](#42112-backup-add)
         * [4.2.11.3 Backup download](#42113-backup-download)
         * [4.2.11.4 Backup delete](#42114-backup-delete)
         * [4.2.11.5 Backup restore](#42115-backup-restore)
      * [4.2.12 Diagnostics management](#4212-diagnostics-management)
         * [4.2.12.1 Global configuration diagnostics](#42121-global-configuration-diagnostics)
         * [4.2.12.2 OCSP responders diagnostics](#42122-ocsp-responders-diagnostics)
         * [4.2.12.3 Timestamping services diagnostics](#42123-timestamping-services-diagnostics)
         * [4.2.12.4 All diagnostics](#42124-all-diagnostics)
      * [4.2.13 Keys management](#4213-keys-management)
         * [4.2.13.1 List keys](#42131-list-keys)
         * [4.2.13.2 Update keys](#42132-update-keys)
         * [4.2.13.3 Delete keys](#42133-delete-keys)
      * [4.2.14 CSR management](#4214-csr-management)
         * [4.2.14.1 List CSR](#42141-list-csr)
         * [4.2.14.2 Delete CSR](#42142-delete-csr)
      * [4.2.15 Instances management](#4215-instances-management)
         * [4.2.15.1 List instances:](#42151-list-instances)
      * [4.2.16 Security Server management](#4216-security-server-management)
         * [4.2.16.1 List Security Servers](#42161-list-security-servers)
         * [4.2.16.2 List Security Server version](#42162-list-security-server-version)
      * [4.2.17 Internal TLS certificate management](#4217-internal-tls-certificate-management)
         * [4.2.17.1 Download internal TLS certificate](#42171-download-internal-tls-certificate)
         * [4.2.17.2 Import internal TLS certificate](#42172-import-internal-tls-certificate)
         * [4.2.17.3 Generate new key internal TLS certificate](#42173-generate-new-key-internal-tls-certificate)
         * [4.2.17.4 Generate new key csr TLS certificate](#42174-generate-new-key-csr-tls-certificate)
* [5 Failure recovery and interpretation of errors](#5-failure-recovery-and-interpretation-of-errors)
   * [5.1 Configuration flow](#51-configuration-flow)
   * [5.2 First-run failures](#52-first-run-failures)
   * [5.3 Configuration file errors](#53-configuration-file-errors)
      * [5.3.1 Malformed YAML](#531-malformed-yaml)
      * [5.3.2 Other configuration file errors](#532-other-configuration-file-errors)
   * [5.4 Errors from internal and external systems](#54-errors-from-internal-and-external-systems)
   * [5.5 Recovery from misconfiguration](#55-recovery-from-misconfiguration)
* [6 Load balancer setup](#6-load-balancer-setup)
* [7 Using the Toolkit to configure highly available services using the built-in Security Server internal load balancing](#7-using-the-toolkit-to-configure-highly-available-services-using-the-built-in-security-server-internal-load-balancing)
* [8 Multitenancy](#8-multitenancy)
* [9 Renew expiring certificates](#9-renew-expiring-certificates)
* [10 Change Security Server owner](#10-change-security-server-owner)
* [11 Certificate profile support](#11-certificate-profile-support)

<!-- vim-markdown-toc -->
<!-- tocstop -->

## License

This document is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

## 1. Introduction

### 1.1 Target Audience

The intended audience of this installation guide are the X-Road Security Server administrators responsible for installing and configuring the X-Road Security Server software.
The document is intended for readers with a good knowledge of Linux server management, computer networks, and the X-Road functioning principles.

### 1.2 References

* <a id="Ref_SS-UG" class="anchor"></a> [\[UG-SS\] X-Road: Security Server User Guide](https://docs.x-road.global/Manuals/ug-ss_x-road_6_security_server_user_guide.html)
* <a id="Ref_YAML_1_1" class="anchor"></a> [\[YAML-1.1\] YAML Ain’t Markup Language (YAML™) Version 1.1](https://yaml.org/spec/1.1)


## 2. Installation

## 2.1 Prerequisites to Installation

* Ubuntu 18.04 LTS or 20.04 LTS
* Python version 3.6+
* `sudo apt-get update` needs to be run before installing
* PIP 21.0+
  ```bash
  sudo apt install -y python3-pip
  python3 -m pip install --upgrade pip
  pip3 install cement
  ```
* Installed X-Road Security Server packages on target machine(s)

## 2.2 Installation

The X-Road Security Server Toolkit package can be installed using PIP (use pip or pip3, whichever is used)

**Installing the official released version**

```bash
pip3 install --extra-index-url https://artifactory.niis.org/artifactory/xroad-extensions-release-pypi/ xrdsst --trusted-host artifactory.niis.org
```

**Upgrading the official released version from a previously released version**

```bash
pip3 install --upgrade --extra-index-url https://artifactory.niis.org/artifactory/xroad-extensions-release-pypi/ xrdsst --trusted-host artifactory.niis.org
```

After installation, ``xrdsst`` command runs the toolkit, when invoked without any parameters,
it will give the overview of available options and sub-commands. Sub-commands themselves can
also have further subcommands, so for example all the supported token operations can be listed
with ``xrdsst token``:

```bash
$ xrdsst token
usage: xrdsst token [-h] [-v] {init-keys,list,login} ...
```


## 3 Configuration of X-Road Security Server

### 3.1 Prerequisites to Configuration

* Single or multiple Security Servers to be configured and maintained.
* X-Road Security Server with subsystem acting as service provider for X-Road management
services, in separate Security Server.
* Toolkit access to configured Security Servers.

**NOTE when using X-Road Security Server Sidecar Slim version, all the Toolkit functionality will remain working, but the timestamping service will not be functional on the Security Server**

#### 3.1.1 Toolkit access to Security Servers

To be able to use the toolkit for configuring Security Server(s), one of the following access combinations
is needed:

1. Access to REST API of configured Security Server + existing API key.
1. Access to REST API of configured Security Server + SSH access to the Security Server machine + X-Road Security Server administrative credentials.

Security server REST API is ordinarily exposed at Security Server port `4000` and is separated into
two parts:
  1. Invocable over network -- API calls for performing most of the functionality available from
     web administration console, accessible with API key.
  1. Invocable only locally (in default configuration), i.e. when accessed via 'localhost' or
     equivalent and passed Security Server administrative credentials via HTTP basic access
     authentication -- API calls that allow API key management operations.

##### 3.1.1.1 Using API keys

The API key used by toolkit against REST API needs following roles for full toolkit
functionality:
 1. XROAD_SYSTEM_ADMINISTRATOR
 1. XROAD_SERVICE_ADMINISTRATOR
 1. XROAD_SECURITY_OFFICER
 1. XROAD_REGISTRATION_OFFICER

On freshly installed and completely unconfigured Security Server, API key can be obtained from
the server with local API invocation, e.g.:

```bash
curl -k --silent \
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
X-Road Security Server administrative access credentials. In the output sample,
``key`` is the UUID to be used as REST API key. This UUID is only retrievable once for
API key, as it is not stored in plaintext at the Security Server. If dealing with security
server that already has some basic configuration done (anchors, ownership information
and software token configuration finished), this API key can also be created from the web
administration console (from "Keys and certificates" -> "API keys" submenu).

##### 3.1.1.2 Using SSH

For ease of automation and development experiments, toolkit is also able to perform operations
when not supplied with API key, but given SSH access credentials to configurable server and security
server administration credentials. In this case, it will create transient API keys for performing
the configuration operations, in the same way as described above, and these API keys are normally
revoked when the toolkit command finishes. However, in case of e.g. electricity or network
connection loss these keys could remain on the Security Server indefinitely.

If SSH access is configured for sudo-capable or root account, this also enables creation of (additional)
administrative accounts for the Security Server.

  
### 3.2 Format of configuration file

Configuration file is in YAML 1.1 format [YAML-1.1](#Ref_YAML_1_1). Avoid using tabs, which
are considered underspecified in YAML. In below configuration skeleton sample, '#' are comments,
and texts between ``<>`` angle brackets are placeholders that (sometimes optionally) should be
filled in the configuration skeleton. The meaning of these placeholders is documented in more
details after the sample. Optional elements that are not to be used can be removed completely.


```yaml
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
  profile: <CERTIFICATE_PROFILE>
  tls_certificates:
  	- /path/to/tls_cert
  clients:
    - member_class: <MEMBER_CLASS>
      member_code: <MEMBER_CODE>
      member_name: <MEMBER_NAME>
      subsystem_code: <SUBSYSTEM_CODE>
      connection_type: <CONNECTION_TYPE>
      tls_certificates:
  		- /path/to/tls_cert
      local_groups:
        - code: <LOCAL_GROUP_CODE>
          description: <LOCAL_GROUP_DESCRIPTION>
          members:
            - <MEMBER_ID>
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

This section shows how to configure the Security Server access as described in
[3.1.1 Toolkit access to Security Servers](#311-toolkit-access-to-security-servers)

```yaml
admin_credentials: <SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>
ssh_access:
  user: <SSH_USER_OS_ENV_VAR_NAME>
  private_key: <SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>
```

* `<SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>`
  * Environment variable name to hold X-Road Security Server admin credentials, e.g., if the variable is set like ``export TOOLKIT_ADMIN_CREDENTIALS=user:pass`` the value to use here is ``TOOLKIT_ADMIN_CREDENTIALS`` (if specified in the separate section, one value will be 
  used for all configurable Security Servers, but if specified in the ``security_server`` section, the value will be overridden for specific 
  configurable Security Server).
* `<SSH_USER_OS_ENV_VAR_NAME>`
  * Environment variable name to hold SSH username, e.g., if the variable is set like ``export TOOLKIT_SSH_USER=ssh_user`` the value to use here is ``TOOLKIT_SSH_USER`` (if specified in ``ssh_access`` section, one value will be used for all configurable Security Servers, 
  but if specified in the ``security_server`` section, the value will be overridden for specific configurable Security Server).
* `<SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>`
  * Environment variable name to hold full path to SSH private key, e.g., if the variable is set like ``export TOOLKIT_SSH_PRIVATE_KEY=/home/user/private_key`` the value to use here is ``TOOLKIT_SSH_PRIVATE_KEY``
  (if specified in ``ssh_access`` section, one value will be used for all configurable Security Servers, 
  but if specified in the ``security_server`` section, the value will be overridden for specific configurable Security Server).  

#### 3.2.2 Security Servers Configuration

This section shows how to set up the Security Server information. It is possible to configure multiple Security Servers at the same time. The toolkit will execute the configurations sequentially.

```yaml
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
  tls_certificates:
    - <TLS_CERT_PATH>
  profile: <CERTIFICATE_PROFILE>
```

* `<API_KEY_ENV_VAR_NAME>`
  * Environment variable name to hold X-Road Security Server API key (e.g. if the variable is set like ``export TOOLKIT_API_KEY=f13d5108-7799-426d-a024-1300f52f4a51`` the value to use here is ``TOOLKIT_API_KEY``) or left as-is/any for toolkit to attempt creation of transient API key.
* `<SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>`
  * (Optional) If is set it will overwrite the `<SECURITY_SERVER_CREDENTIALS_OS_ENV_VAR_NAME>` property described in the [access section](#3.2.1-access-configuration).
* `<CONFIGURATION_ANCHOR_PATH>`
  * Path to the configuration anchor file, e.g., `/etc/xroad/configuration-anchor.xml`.
* `<SIGN_CERT_PATH>`
  * Should be given as path referring to sign certificates location.
* `<AUTH_CERT_PATH>`
  * Should be given as path referring to auth certificate location.
* `<SECURITY_SERVER_NAME>`
  * Should be substituted with the installed Security Server name, e.g., `ss1`.
* `<OWNER_DISTINGUISHED_NAME_COUNTRY>`
  * Should be ISO 3166-1 alpha-2 two letter code for server owner country. This is used in certificate generation.
* `<OWNER_DISTINGUISHED_NAME_ORGANIZATION>`
  * Should be set to server owner organization. This is used in certificate generation.
* `<OWNER_MEMBER_CLASS>`
  * Should be substituted with the member class obtained from the Central Server, e.g., `GOV`.
* `<OWNER_MEMBER_CODE>`
  * Should be substituted with the member code obtained from the Central Server, e.g., `1234`.
* `<SERVER_CODE>`
  * Should be substituted with the server code of the installed Security Server, e.g., `ss1`.
* `<SOFT_TOKEN_ID>`
  * Default software token ID, normally 0 (zero).
* `<SOFT_TOKEN_PIN>`
  * Should be substituted with a desired numeric pin code.
* `<SECURITY_SERVER_EXTERNAL_FQDN>`
  * Externally accessible FQDN for the Security Server. It's applied to the Security Server certificates.
* `<SECURITY_SERVER_INTERNAL_FQDN_OR_IP>`
  * Should be substituted with internal IP address or host name of the installed Security Server, e.g., `ss1`.
* `<SSH_USER_OS_ENV_VAR_NAME>`
  * (Optional) If set, it will overwrite the `<SSH_USER_OS_ENV_VAR_NAME>` property described in the [access section](#3.2.1-access-configuration).
* `<SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>`
  * (Optional) If set, it will overwrite the `<SSH_PRIVATE_KEY_OS_ENV_VAR_NAME>` property described in the [access section](#3.2.1-access-configuration).
* `<TLS_CERT_PATH>`
  * Path to the internal TLS certificated to be added to the whitelist of a member or subsystem, e.g., `/etc/xroad/cert.pem`.
* `<CERTIFICATE_HASH>`
  * List of certificate hash on which we are going to apply operations such as disable, unregister, delete.
* `<CERTIFICATE_PROFILE>`
  * (Optional) Profile name described in [11 Certificate profile support](#11-certificate-profile-support).

#### 3.2.3 Client Configuration

The Security Server client information is configured in this section. It is possible to set up a list of subsystems belonging to the owner member
configured in the [Security Server configuration](#322-security-servers-configuration) or add them to a new member as described
in [8 Multitenancy](#8-multitenancy).

```yaml
clients:
  - member_class: <MEMBER_CLASS>
    member_code: <MEMBER_CODE>
    member_name: <MEMBER_NAME>
    subsystem_code: <SUBSYSTEM_CODE>
    connection_type: <CONNECTION_TYPE>
    tls_certificates:
      - <TLS_CERT_PATH>
    local_groups:
      - code: <LOCAL_GROUP_CODE>
        description: <LOCAL_GROUP_DESCRIPTION>
        members:
          - <MEMBER_ID>
```

* `<MEMBER_CLASS>`
  * Should be substituted with the member class obtained from the Central Server, e.g., `GOV`.
It must have the same value as `<OWNER_MEMBER_CLASS>` if is a subsystem of the owner client.
* `<OWNER_MEMBER_CODE>`
  * Should be substituted with the member code obtained from the Central Server, e.g., `1234`. It must have the same value as `<OWNER_MEMBER_CLASS>` if is a subsystem of the owner client.
* `<MEMBER_NAME>`
  * Should be substituted with the member name obtained from the Central Server, e.g., `COMPANY`. It must have the same value as `<OWNER_DISTINGUISHED_NAME_ORGANIZATION>` if is a subsystem of the owner client.
* `<SUBSYSTEM_CODE>`
  * (Optional, not required for members) X-Road member/client subsystem code.
* `<CONNECTION_TYPE>`
  * Connection protocol selection, from among ``HTTP``, ``HTTPS``, ``HTTPS_NO_AUTH``.
* `<TLS_CERT_PATH>`
  * Path to the internal TLS certificated to be added to the whitelist of a member or subsystem, e.g., `/etc/xroad/cert.pem`.

<strong>Local groups (Optional):</strong>
* `<LOCAL_GROUP_CODE>`
  * Code for single local group. Must be unique for each Security Server client.
* `<LOCAL_GROUP_DESCRIPTION>`
  * Description for single local group.
* `<MEMBER_ID>`
  * (Optional) list of subsystems ids, composed by `<INSTANCE>:<MEMBER_CLASS>:<MEMBER_CODE>:<SUBSYSTEM_CODE>`.

#### 3.2.3 Service Configuration

In this section services with type ``OPENAPI3``, ``REST``, ``WSDL`` can be configured by adding a service description
with parameters ``url``, ``rest_service_code``, ``type`` and ``access``. In order to provide access to the services added with that
service description to different subsystems, the parameter ``access`` should contain a list of subsystem codes. To configure specific services
described with the service description, the parameters ``service_code`` and ``access`` must be configured in the section ``services``. 

```yaml
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

* `<SERVICE_DESCRIPTION_URL>`
  * URL for service description.
* `<REST_SERVICE_CODE>`
  * REST service code, not used for WSDL services.
* `<SERVICE_TYPE>`
  * Type of service, value from ``OPENAPI3``, ``REST``, ``WSDL``.
* `<SERVICE_DESCRIPTION_ACCESS>`
  * (Optional) list of subsystems ids, composed by `<INSTANCE>:<MEMBER_CLASS>:<MEMBER_CODE>:<SUBSYSTEM_CODE>`, or Security Server owners global group id composed by `<INSTANCE>:security-server-owners`.
* `<SERVICE_URL_FOR_ALL>`
  * Boolean value determining if the URL prefix should be applied for all the services.
* `<SERVICE_TIMEOUT_FOR_ALL>`
  * Boolean value specifying if the timeout should be applied for all the services in the service description.
* `<SERVICE_USE_SSL_AUTH_FOR_ALL>`
  * Boolean value specifying whether SSL authentication should be used for all the services in the service description.

<strong>Services (Optional):</strong>
It's possible to create services manually but usually it's not required because they are parsed from the service descriptions automatically. Adding a service manually is needed when a service description isn't available, there is a need to customize the access rights, or there is a need to customize the parameters.

* `<SERVICE_CODE>`
  * Code for single service.
* `<SERVICE_ACCESS>`
  * (Optional) same as `<SERVICE_DESCRIPTION_ACCESS>`, if its defined, it will overwrite the values defined in `<SERVICE_DESCRIPTION_ACCESS>` for the single service.
* `<SERVICE_TIMEOUT>`
  * Timeout for service in seconds.
* `<SERVICE_USE_SSL_AUTH>`
  * Boolean value for specifying whether SSL authentication should be used.
* `<SERVICE_URL>`
  * URL for single service.

<strong>Endpoints (Optional):</strong>
The endpoints are only available for service descriptions of type `REST` or `OPENAPI3`.

* `<ENDPOINT_PATH>`
  * Path for the endpoint.
* `<ENDPOINT_METHOD>`
  * Method for the endpoint (`GET`, `POST`, `PUT`, etc.).
* `<ENDPOINTS_ACCESS>`
  * (Optional) same as `<SERVICE_ACCESS>` or `<SERVICE_DESCRIPTION_ACCESS>` but for grant endpoint access rights.

### 3.3 Different ways of using the configuration file

* default configuration in ``config/xrdsst.yml``
* overriding the default configuration by providing an extra parameter ``-c configfile`` when running the X-Road Security Server Toolkit

## 4 Running the X-Road Security Server Toolkit

The X-Road Security Server Toolkit is run from the command line by typing:

```bash
$ xrdsst
```

Which currently gives further information about tool invocation options and subcommands.
Base information about statuses of all defined Security Servers can be seen with read-only
``status`` operation:

```bash
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

### 4.1 The single command fully automatic configuration of Security Servers listed in configuration file

The whole Security Server configuration in a fully automatic mode (all configuration from configuration file) can be run with ``xrdsst apply``
For performing the configuration step by step instead, please start from [4.2.2 Initializing the Security Server command](#422-initializing-the-security-server-command)


### 4.2 X-Road Security Server  Toolkit commands

* Access rights: All commands require at least the role XROAD_SYSTEM_ADMINISTRATOR.

#### 4.2.1 Creating admin user command

X-Road admin user can be created with 

```bash
xrdsst user create-admin
```

Configuration parameters involved are described in [3.2.1 Access Configuration](#321-access-configuration). Specifically, the administrator user will have the `name: password` defined in the property `admin_credentials`.


Note: This is an optional step in the configuration process and should only be run if the admin user has not been created before. 
      SSH (SSH user and a private key) is used for creating the admin user. If the admin user has been created before, then it is 
      enough to just add the credentials to the configuration file as ``admin_credentials`` and this step can be skipped totally.

**It is a security risk to store the SSH access-related credentials into to configuration file as plain text.**

#### 4.2.2 Initializing the Security Server command

* Access rights: XROAD_SYSTEM_ADMINISTRATOR, XROAD_SECURITY_OFFICER

Initializes the Security Server and upload the configuration anchor by typing:

```bash
xrdsst init
```

Configuration parameters involved are the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)

#### 4.2.3 Token commands

Configuration parameters related to tokens involved are `software_token_id` and `software_token_pin` the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)

##### 4.2.3.1 Token login command

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Default software token login can be logged on with:

```bash
xrdsst token login
```

Configuration parameters involved are `software_token_id` and `software_token_pin` the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)

##### 4.2.3.2 Token list

* Access rights: Any

All tokens known to Security Server can be listed with:

```bash
xrdsst token list
```

##### 4.2.3.3 Token init-keys

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER or XROAD_SECURITY_OFFICER

Token keys for authentication and signatures can be created with:

```bash
xrdsst token init-keys
``` 

Creates two keys and generates corresponding certificate signing requests (one for authentication, other for signing).
The key labels used are conventionally with suffixes ``default-auth-key`` and ``default-sign-key``, if
those already exist, they will not be duplicated and command acts as no-op for such Security Server.
If we are using [Multitenancy](#8-multitenancy) this command will also create an extra key and signing request with the 
key label suffix ``default-sign-key_<MEMBER_CODE>_<MEMBER_NAME>``

##### 4.2.3.4 Token create-new-keys

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER or XROAD_SECURITY_OFFICER

Token keys for authentication and signatures can be created with:

```bash
xrdsst token create-new-keys
``` 

This command works the same as the [4.2.3.3 Token init-keys](#4233-token-init-keys) command,
the difference is that this command will be used when the certificates already exist and we want to generate 
new keys to renew them.

#### 4.2.4 Timestamp commands

Configuration parameters involved are the described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)


##### 4.2.4.1 Timestamp init

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

Single timestamping service approved for use in Central Server can be configured for Security Server by invoking ``timestamp`` subcommand as: 

```bash
xrdsst timestamp init
```

##### 4.2.4.2 Timestamp list approved

* Access rights: Any

List the available timestamp services approved for the Security Server

```bash
xrdsst timestamp list-approved
```

##### 4.2.4.3 Timestamp list configured

* Access rights: Any

List the available timestamp services configured for the Security Server

```bash
xrdsst timestamp list-configured
```

#### 4.2.5 Certificate management commands

These commands allow us to perform certificate operations of a Security Server.

##### 4.2.5.1 Certificate download CSRS

* Access rights: XROAD_SECURITY_OFFICER

Certificate signing requests can be downloaded with 

```bash
xrdsst cert download-csrs
```

##### 4.2.5.2 Certificate import

* Access rights: XROAD_SYSTEM_ADMINISTRATOR, XROAD_REGISTRATION_OFFICER and XROAD_SECURITY_OFFICER

Configuration parameters involved are the `certificates` list described in [3.2.2 Security Servers Configuration](#322-security-servers-configuration)
In the `certificates` list we must set the path for the signed SIGN and AUTH certificates previously downloaded then can be imported with:

```bash
xrdsst cert import
```

##### 4.2.5.3 Certificate registration

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

Register the certificates previously imported in the Central Server with:

```bash
xrdsst cert register
```

##### 4.2.5.4 Certificate activation

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

AUTH certificate activation can be done with:

```bash
xrdsst cert activate
```

##### 4.2.5.5 List certificates

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

SIGN and AUTH certificate information of the Security Servers can be listed with:

```bash
xrdsst cert list
```

```bash
╒══════╤════════════════════════════════╤════════════════╤══════════════════════════════════════════╤══════════╤══════════════╤════════════════════╤════════════╤═════════════╕
│ ss   │ label                          │ type           │ hash                                     │ active   │ expiration   │ ocsp_status        │ status     │ subject     │
╞══════╪════════════════════════════════╪════════════════╪══════════════════════════════════════════╪══════════╪══════════════╪════════════════════╪════════════╪═════════════╡
│ ss1  │ ss1-default-auth-key           │ AUTHENTICATION │ 8EA19FE5CDD100390353EB40F6D6C2C70FE0AAFD │ True     │ 2041/06/10   │ OCSP_RESPONSE_GOOD │ REGISTERED │ DEV/ss1/ORG │
├──────┼────────────────────────────────┼────────────────┼──────────────────────────────────────────┼──────────┼──────────────┼────────────────────┼────────────┼─────────────┤
│ ss1  │ ss1-default-sign-key           │ SIGNING        │ 397401787220FCB20A2194DAD3066DF4A0C8C5A6 │ True     │ 2041/06/10   │ OCSP_RESPONSE_GOOD │ REGISTERED │ DEV/ss1/ORG │
├──────┼────────────────────────────────┼────────────────┼──────────────────────────────────────────┼──────────┼──────────────┼────────────────────┼────────────┼─────────────┤
│ ss1  │ ss1-default-sign-key_COM_12345 │ SIGNING        │ CF09F4944E0EC2B2E3B149C1AC9C0DD4990C62D6 │ True     │ 2041/06/10   │ OCSP_RESPONSE_GOOD │ REGISTERED │ DEV/ss1/COM │
╘══════╧════════════════════════════════╧════════════════╧══════════════════════════════════════════╧══════════╧══════════════╧════════════════════╧════════════╧═════════════╛
```

The table above shows the following information about the certificates:

* ss: Name of the Security Server where the certificate is installed.
* label: Label of the certificate.
* type: Type of the certificate, could be AUTHENTICATION or SIGNING
* hash: Unique identifier of the certificate
* active: Boolean for checking if the certificate is currently active.
* expiration: Expiration date expressed in 'yyyy/mm/dd'
* ocsp_status: OCSP status response
* status: Status of the certificate between: 'GLOBAL ERROR', 'SAVED', 'REGISTERED', 'REGISTRATION IN PROGRESS', 'DELETION IN PROGRESS', 'DELETED'
* subject: Owner member of the certificate. 

##### 4.2.5.6 Certificate disable

* Access rights: XROAD_SECURITY_OFFICER


A hash (or list of hashes separated by comma) of the certificates we want to disable has to be provided as parameter. We can get the hashes of the certificates
installed in each Security Server by running the command [4.2.5.6 List certificates](#4256-list-certificates):

Disable the certificates can be done with:

```bash
xrdsst cert disable --hash <CERTIFICATE_HASH>
```

##### 4.2.5.7 Certificate unregister

* Access rights: XROAD_SECURITY_OFFICER

A hash (or list of hashes separated by comma) of the authentication certificates we want to delete has to be provided as parameter. We can get the hashes of the certificates
installed in each Security Server by running the command [4.2.5.6 List certificates](#4256-list-certificates):

Unregister the authentication certificates can be done with:

```bash
xrdsst cert unregister --hash <CERTIFICATE_HASH>
```

##### 4.2.5.8 Certificate delete

* Access rights: XROAD_SECURITY_OFFICER

A hash (or list of hashes separated by comma) of the certificates we want to delete has to be provided as parameter. We can get the hashes of the certificates
installed in each Security Server by running the command [4.2.5.6 List certificates](#4256-list-certificates):

Delete the certificates can be done with:

```bash
xrdsst cert delete --hash <CERTIFICATE_HASH>
```

#### 4.2.6 Client management commands

Client are managed with ``xrdsst client`` subcommands.
Configuration parameters involved are the `certificates` list described in [3.2.3 Clients Configuration](#323-client-configuration)

##### 4.2.6.1 Client add

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER

New subsystem or members can be added with:

```bash
xrdsst client add
```

##### 4.2.6.2 Client register

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER

Subsystems and new members registration in Central Server can proceed with:

```bash
xrdsst client register
```

##### 4.2.6.3 Client update

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER

Subsystem parameters can be updated with:

```bash
xrdsst client update
```

##### 4.2.6.4 Client import TLS certificates

TLS certificates can be imported and added to a client's whitelist with

```bash
xrdsst client import-tls-certs
```

##### 4.2.6.5 Client unregister

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER
There are no configuration parameters involved, command line arguments are used instead
Subsystems and new members can be unregister with:

```bash
xrdsst client unregister --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id(s) of the client, e.g., DEV:GOV:1234:TEST,DEV:COM:12345:SUB

##### 4.2.6.6 Client delete

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_REGISTRATION_OFFICER
There are no configuration parameters involved, command line arguments are used instead
Subsystems and new members can be deleted with:

```bash
xrdsst client delete --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id(s) of the client, e.g., DEV:GOV:1234:TEST,DEV:COM:12345:SUB

The members or subsystem must be unregistered from the Security Server in order to delete it.

##### 4.2.6.7 Client change owner

* Access rights: XROAD_REGISTRATION_OFFICER
There are no configuration parameters involved, command line arguments are used instead
It is possible to make owner to members with:

```bash
xrdsst client delete --ss <SECURITY_SERVER_NAME> --member <MEMBER_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <MEMBER_ID> id of the member, e.g., DEV:GOV:1234

This command will submit a change owner request to the  X-Road governing authority according to the organizational
procedures of the X-Road instance. 
Once the owner change request is approved by the X-Road governing authority, the member will automatically become 
the Owner Member.
This command will create a new auth key and CSRS for the auth certificate of the new owner

##### 4.2.6.8 Client list

* Access rights: Any role

List clients (subsystem and members) can be done with:

```bash
xrdsst client list --ss <SECURITY_SERVER_NAME>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`

```bash
╒══════════════════╤════════════╤════════════════╤═══════════════╤═══════════════╤═════════════╤═════════╤════════════╤═════════════════╕
│ ID               │ INSTANCE   │ MEMBER CLASS   │   MEMBER CODE │ MEMBER NAME   │ SUBSYSTEM   │ OWNER   │ STATUS     │ HAS SIGN CERT   │
╞══════════════════╪════════════╪════════════════╪═══════════════╪═══════════════╪═════════════╪═════════╪════════════╪═════════════════╡
│ DEV:COM:12345    │ DEV        │ COM            │         12345 │ COMPANY       │             │ False   │ SAVED      │ True            │
├──────────────────┼────────────┼────────────────┼───────────────┼───────────────┼─────────────┼─────────┼────────────┼─────────────────┤
│ DEV:ORG:111      │ DEV        │ ORG            │           111 │ NIIS          │             │ True    │ REGISTERED │ True            │
├──────────────────┼────────────┼────────────────┼───────────────┼───────────────┼─────────────┼─────────┼────────────┼─────────────────┤
│ DEV:ORG:111:TEST │ DEV        │ ORG            │           111 │ NIIS          │ TEST        │ False   │ REGISTERED │ True            │
╘══════════════════╧════════════╧════════════════╧═══════════════╧═══════════════╧═════════════╧═════════╧════════════╧═════════════════╛
```

* ID client id
* INSTANCE client instance
* MEMBER CLASS client member class
* MEMBER CODE client member code
* MEMBER NAME client member name
* SUBSYSTEM client subsystem code (empty for members)
* OWNER true if the client is the owner of the Security Server
* STATUS client status between SAVED, REGISTRATION IN PROGRESS, REGISTERED, GLOBAL ERROR, DELETION IN PROGRESS, DELETED
* HAS SIGN CERT true if the client has a valid sign certificate

#### 4.2.7 Service management commands

Services and service descriptions are managed with ``xrdsst service`` subcommands.
Configuration parameters involved are the described in [3.2.3 Services Configuration](#323-services-configuration)

##### 4.2.7.1 Service add description

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Adding REST/OPENAPI3/WSDL service can be done with:

```bash
xrdsst service add-description
```

For REST / OPENAPI3 type services, this command will auto-generate a service with the property name `rest_service_code`. 

For WSDL type services it is not necessary to fill in the `rest_service_code` property, when adding the description the services discovered in the WSDL URL are autogenerated.

The default values of the service properties will be of 60 for the `timeout` and False for the` ssl_auth`.

We must include the services when we want to modify any of their properties (for all or for single one).

##### 4.2.7.2 Service add access rights

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Access rights for a service can be done with:

```bash
xrdsst service add-access
```

This command will add for all the services the access rights defined in the property `access` of the` service_descriptions` section
except in the case that the `access` property of the `services` section is filled, in that case, this list will overwrite 
the access rights for the individual service. 

##### 4.2.7.3 Enable service

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Enabling the service description can be done with:

```bash
xrdsst service enable-description
```

##### 4.2.7.4 Service update parameters

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Updating the service parameters can be done with:

```bash
xrdsst service update-parameters
```

This command will update the parameters of the single services added to the configuration file, or it will update the parameters
for all the services in the description if the boolean parameters are set to True.

##### 4.2.7.5 Service list descriptions

* Access rights: XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Listing service descriptions can be done with:

```bash
xrdsst service list-descriptions --client <CLIENT_ID>
```

* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST, multiple values can also be given, separated by comma, e.g., DEV:GOV:1234:TEST,DEV:GOV:1234:MANAGEMENT

```bash
╒══════╤═══════════════════╤══════╤════════════════════════════════════════════════════╤══════════╤════════════╤════════════╕
│ SS   │ CLIENT            │   ID │ URL                                                │ TYPE     │ DISABLED   │   SERVICES │
╞══════╪═══════════════════╪══════╪════════════════════════════════════════════════════╪══════════╪════════════╪════════════╡
│ ss3  │ DEV:GOV:1234:TEST │   28 │ http://10.249.34.187/managementservices.wsdl       │ WSDL     │ False      │          4 │
├──────┼───────────────────┼──────┼────────────────────────────────────────────────────┼──────────┼────────────┼────────────┤
│ ss3  │ DEV:GOV:1234:TEST │   22 │ https://raw.githubusercontent.com/OpenAPITools/... │ OPENAPI3 │ False      │          1 │
╘══════╧═══════════════════╧══════╧════════════════════════════════════════════════════╧══════════╧════════════╧════════════╛
```

* SS Security Server name
* CLIENT client full id
* ID service description id
* URL service description url
* TYPE service description type
* DISABLED boolean value to indicate if service description is disabled
* SERVICES number of services provided with the given service description

##### 4.2.7.6 Service list services

* Access rights: XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Listing services for client's service descriptions can be done with:

```bash
xrdsst service list-services --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID>
```

* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456

```bash
╒══════╤═══════════════════╤═══════════════╤════════════════════════════════════╤══════════════════╤═══════════╤═══════════════════════════════════════════════╕
│ SS   │ CLIENT            │   DESCRIPTION │ SERVICE                            │ CODE             │   TIMEOUT │ URL                                           │
╞══════╪═══════════════════╪═══════════════╪════════════════════════════════════╪══════════════════╪═══════════╪═══════════════════════════════════════════════╡
│ ss3  │ DEV:GOV:1234:TEST │            28 │ DEV:GOV:1234:TEST:authCertDeletion │ authCertDeletion │        60 │ http://INSERT_MANAGEMENT_SERVICE_ADDRESS_HERE │
├──────┼───────────────────┼───────────────┼────────────────────────────────────┼──────────────────┼───────────┼───────────────────────────────────────────────┤
│ ss3  │ DEV:GOV:1234:TEST │            28 │ DEV:GOV:1234:TEST:clientDeletion   │ clientDeletion   │        60 │ http://INSERT_MANAGEMENT_SERVICE_ADDRESS_HERE │
├──────┼───────────────────┼───────────────┼────────────────────────────────────┼──────────────────┼───────────┼───────────────────────────────────────────────┤
│ ss3  │ DEV:GOV:1234:TEST │            28 │ DEV:GOV:1234:TEST:clientReg        │ clientReg        │        60 │ http://INSERT_MANAGEMENT_SERVICE_ADDRESS_HERE │
├──────┼───────────────────┼───────────────┼────────────────────────────────────┼──────────────────┼───────────┼───────────────────────────────────────────────┤
│ ss3  │ DEV:GOV:1234:TEST │            28 │ DEV:GOV:1234:TEST:ownerChange      │ ownerChange      │        60 │ http://INSERT_MANAGEMENT_SERVICE_ADDRESS_HERE │
╘══════╧═══════════════════╧═══════════════╧════════════════════════════════════╧══════════════════╧═══════════╧═══════════════════════════════════════════════╛
```

* SS Security Server name
* CLIENT client full id
* DESCRIPTION service description id
* SERVICE service full id
* CODE service code
* TIMEOUT service timeout value
* URL service url

##### 4.2.7.7 Service delete descriptions

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Deletion of service descriptions can be done with:

```bash
xrdsst service delete-descriptions --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456

##### 4.2.7.8 Service update descriptions

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Update of service descriptions can be done with:

```bash
xrdsst service update-descriptions --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID> --code <REST_SERVICE_CODE> --url <SERVICE_DESCRIPTION_URL
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456
* <REST_SERVICE_CODE> REST service code for service description with type REST/OPENAPI3, e.g., Petstore
* <SERVICE_DESCRIPTION_URL> url of the service description, e.g., https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/modules/openapi-generator-gradle-plugin/samples/local-spec/petstore-v3.0.yaml

Parameters that can be updated for service description of type WSDL:
* <SERVICE_DESCRIPTION_URL>

Parameters that can be updated for service description of type REST/OPENAPI3:
* <REST_SERVICE_CODE>
* <SERVICE_DESCRIPTION_URL>

##### 4.2.7.9 Service refresh descriptions

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Refresh of service descriptions can be done with:

```bash
xrdsst service refresh-descriptions --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456

##### 4.2.7.10 Service disable descriptions

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Disabling of service descriptions can be done with:

```bash
xrdsst service disable-descriptions --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID> --notice <NOTICE>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456
* <NOTICE> disabling notice, e.g., "Not used"

##### 4.2.7.11 Service list access rights for services

* Access rights: XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Listing access rights for services for client's service descriptions can be done with:

```bash
xrdsst service list-access --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID>
```

* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456

```bash
╒══════╤═══════════════════╤═══════════════╤════════════════════════════╤════════════════════════════╤════════════════════════╤════════════════╤═════════════╕
│ SS   │ CLIENT            │   DESCRIPTION │ SERVICE                    │ SERVICE_CLIENT             │ NAME                   │ RIGHTS_GIVEN   │ TYPE        │
╞══════╪═══════════════════╪═══════════════╪════════════════════════════╪════════════════════════════╪════════════════════════╪════════════════╪═════════════╡
│ ss3  │ DEV:GOV:1234:TEST │            22 │ DEV:GOV:1234:TEST:Petstore │ DEV:security-server-owners │ Security server owners │ 2021/08/17     │ GLOBALGROUP │
╘══════╧═══════════════════╧═══════════════╧════════════════════════════╧════════════════════════════╧════════════════════════╧════════════════╧═════════════╛
```

* SS Security Server name
* CLIENT client full id
* DESCRIPTION service description id
* SERVICE service full id
* SERVICE_CLIENT service client id that has access to the given service
* NAME service client name that has access to the given service
* RIGHTS_GIVEN a date when access rights were given
* TYPE service client type

##### 4.2.7.12 Service delete access rights for services

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

There are no configuration parameters involved, command line arguments are used instead

Deleting access rights for services for client's service descriptions can be done with:

```bash
xrdsst service delete-access --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID> --description <SERVICE_DESCRIPTION_ID> --service <SERVICE_ID> --sclient <SERVICE_CLIENT_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <CLIENT_ID> id of the client, e.g., DEV:GOV:1234:TEST
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123
* <SERVICE_ID> id of the service, e.g., DEV:GOV:1234:TEST:Petstore
* <SERVICE_CLIENT_ID> id of the service description, e.g., DEV:security-server-owners, multiple values can also be given, separated by comma, e.g., DEV:GOV:1234:TEST,DEV:security-server-owners

##### 4.2.7.13 Service apply

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

It is possible to run sequentially all the service commands described before in [4.2.6 Service management commands](#427-service-management-commands)
with:

```bash
xrdsst service apply
```

This command will execute the commands: ``xrdsst service add-description``, ``xrdsst service enable-description``, ``xrdsst service add-access``, ``xrdsst service update-parameters``.

#### 4.2.8 Endpoint management

Endpoints are managed with ``xrdsst endpoint`` subcommands.

Configuration parameters involved are the ``endpoint`` section described in [3.2.3 Service Configuration](#323-service-configuration)

Endpoints are only available for service types REST and OPENAPI3.

##### 4.2.8.1 Endpoint add

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Adding endpoints to a service can be done with:

```bash
xrdsst endpoint add
```

Endpoints in service type OPENAPI3 are autogenerated, so, the endpoints defined in the configuration 
will be created together with the autogenerated ones.

##### 4.2.8.2 Endpoint add access rights

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Access rights for a single endpoint can be add with:

```bash
xrdsst endpoint add-access
```

##### 4.2.8.3 Endpoint list

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Listing service endpoints can be done with:

```bash
xrdsst endpoint list --ss <SECURITY_SERVER_NAME> --description <SERVICE_DESCRIPTION_ID>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <SERVICE_DESCRIPTION_ID> id of the service description, e.g., 123, multiple values can also be given, separated by comma, e.g., 123,456

```bash
╒═══════════════╤════════╤═══════════╤══════════════════╤══════════════════╤════════════════════════════════════════════════════╤══════════╕
│   ENDPOINT ID │ PATH   │ METHOD    │ SERVICE CODE     │ CLIENT           │ SERVICE DESCRIPTION                                │ TYPE     │
╞═══════════════╪════════╪═══════════╪══════════════════╪══════════════════╪════════════════════════════════════════════════════╪══════════╡
│            25 │ *      │ **        │ authCertDeletion │ DEV:ORG:111:TEST │ http://10.54.135.88/managementservices.wsdl        │ WSDL     │
├───────────────┼────────┼───────────┼──────────────────┼──────────────────┼────────────────────────────────────────────────────┼──────────┤
│            28 │ GET    │ /getPath  │ Petstore         │ DEV:ORG:111:TEST │ https://raw.githubusercontent.com/OpenAPITools/... │ OPENAPI3 │
├───────────────┼────────┼───────────┼──────────────────┼──────────────────┼────────────────────────────────────────────────────┼──────────┤ 
│            17 │ GET    │ /pets/*   │ Petstore         │ DEV:ORG:111:TEST │ https://raw.githubusercontent.com/OpenAPITools/... │ OPENAPI3 │
╘═══════════════╧════════╧═══════════╧══════════════════╧══════════════════╧════════════════════════════════════════════════════╧══════════╛
```

The table above shows the following information about the endpoint:

* ENDPOINT ID: Id of the endpoint.
* PATH: Path of the endpoint.
* METHOD: Method of the endpoint.
* SERVICE CODE: Code of the service owner of the endpoint.
* CLIENT : Client id of the subsystem owner of the endpoint.
* SERVICE DESCRIPTION : Url of the service description owner of the endpoint.
* TYPE : Type of the service description owner of the endpoint.

##### 4.2.8.4 Endpoint update

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Single endpoint can be updated with with:

```bash
xrdsst endpoint update --ss <SECURITY_SERVER_NAME> --endpoint  <ENDPOINT_ID> --method <ENDPOINT_METHOD> --path <ENDPOINT_PATH>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <ENDPOINT_ID> id of the endpoint to be updated, e.g., 1
* <ENDPOINT_METHOD> new endpoint method, possible methods are: ALL, GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS, TRACE
* <ENDPOINT_path> new endpoint path, e.g., /users 

##### 4.2.8.5 Endpoint delete

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Single endpoint can be deleted with:

```bash
xrdsst endpoint delete --ss <SECURITY_SERVER_NAME> --endpoint  <ENDPOINT_ID> 
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <ENDPOINT_ID> id of the endpoint to be delete, e.g., 1

##### 4.2.8.6 Endpoint list access

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Listing service endpoint access can be done:

```bash
xrdsst endpoint list-access --ss <SECURITY_SERVER_NAME> --endpoint  <ENDPOINT_ID> 
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <ENDPOINT_ID> id of the endpoint, e.g., 123, multiple values can also be given, separated by comma, e.g., 1,2,3

```bash
╒═══════════════╤════════════╤════════════════╤═══════════════════════════════════════════════════╕
│   ENDPOINT ID │ ENDPOINT   │ SERVICE CODE   │ ACCESS RIGHTS                                     │
╞═══════════════╪════════════╪════════════════╪═══════════════════════════════════════════════════╡
│            15 │ GET /pets  │ Petstore       │ DEV:GOV:9999:SUBGOV, DEV:ORG:0000:SUBORGANIZATION │
├───────────────┼────────────┼────────────────┼───────────────────────────────────────────────────┤
│            26 │ * **       │ ownerChange    │ DEV:security-server-owners                        │
╘═══════════════╧════════════╧════════════════╧═══════════════════════════════════════════════════╛
```

The table above shows the following information about the endpoint access:

* ENDPOINT ID: Id of the endpoint.
* ENDPOINT: Method and path of the endpoint.
* SERVICE CODE: Code of the service owner of the endpoint.
* ACCESS RIGHTS : List of service clients ids with access rights to the endpoint

##### 4.2.8.7 Endpoint delete access rights

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Endpoints access rights can be deleted with:

```bash
xrdsst endpoint delete-access --ss <SECURITY_SERVER_NAME> --endpoint  <ENDPOINT_ID> --access <ACCESS_RIGTHS>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <ENDPOINT_ID> id of the endpoint, e.g., 123, multiple values can also be given, separated by comma, e.g., 1,2,3
* ACCESS RIGHTS : Service clients ids with access rights to the endpoint, multiple values can also be given, separated by comma, e.g., DEV:GOV:9999:SUBGOV,DEV:security-server-owners  

This command will search through all the endpoints send as parameters and delete the access rights that matches with the ones sent as parameters

#### 4.2.9 Member management

Members are managed with ``xrdsst member`` subcommands.

There are no configuration parameters involved, command line arguments are used instead

##### 4.2.9.1 Member find

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Finding a member for current X-Road instance can be done with:

```bash
xrdsst member find --class <MEMBER_CLASS> --code <MEMBER_CODE>
```

* <MEMBER_CLASS> member class for the member to be searched, e.g., GOV
* <MEMBER_CODE> member code for the member to be searched, e.g., 1234

```
╒═══════════════════╤═══════════════╤════════════════╤═══════════════╕
│ SECURITY-SERVER   │ MEMBER-NAME   │ MEMBER-CLASS   │   MEMBER-CODE │
╞═══════════════════╪═══════════════╪════════════════╪═══════════════╡
│ ss3               │ ACME          │ GOV            │          1234 │
╘═══════════════════╧═══════════════╧════════════════╧═══════════════╛
```

* SECURITY-SERVER Security Server name
* MEMBER-NAME name of the member
* MEMBER-CLASS member class
* MEMBER-CODE member code

##### 4.2.9.2 Member list member classes

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Listing member classes can be done with:

```bash
xrdsst member list-classes --instance <XROAD-INSTANCE>
```

**When ``instance`` command-line parameter is not provided, current instance is assumed**

* <XROAD-INSTANCE> X-Road instance for the member classes to be searched, e.g., DEV

```bash
╒═══════════════════╤════════════╤════════════════╕
│ SECURITY-SERVER   │ INSTANCE   │ MEMBER-CLASS   │
╞═══════════════════╪════════════╪════════════════╡
│ ss3               │            │ COM            │
├───────────────────┼────────────┼────────────────┤
│ ss3               │            │ GOV            │
╘═══════════════════╧════════════╧════════════════╛
```

* SECURITY-SERVER Security Server name
* INSTANCE instance name
* MEMBER-CLASS member class

#### 4.2.10 Local groups management

Client local groups are managed with ``xrdsst local-group`` subcommands.

##### 4.2.10.1 Local groups add

Configuration parameters involved are the ``local-groups`` section described in [3.2.3 Client Configuration](#323-client-configuration)

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Adding local groups to a client can be done with:

```bash
xrdsst local-group add
```

##### 4.2.10.2 Local groups add members

Configuration parameters involved are the ``local-groups members`` section described in [3.2.3 Client Configuration](#323-client-configuration)

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SERVICE_ADMINISTRATOR

Adding members to a local group can be done with:

```bash
xrdsst local-group add-member
```

##### 4.2.10.3 Local groups list

* Access rights: XROAD_SERVER_OBSERVER or XROAD_SERVICE_ADMINISTRATOR

Listing client local groups can be done with:

```bash
xrdsst local-group list --ss <SECURITY_SERVER_NAME> --client <CLIENT_ID>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <CLIENT_ID> subsystem client id, e.g., DEV:COM:12345:COMPANY

```bash
╒══════╤════════════╤════════════════════════╤═════════════════════════════════════════════════════════╕
│   ID │ CODE       │ DESCRIPTION            │ MEMBERS                                                 │
╞══════╪════════════╪════════════════════════╪═════════════════════════════════════════════════════════╡
│  185 │ OtherGroup │ description 1          │ []                                                      │
├──────┼────────────┼────────────────────────┼─────────────────────────────────────────────────────────┤
│  125 │ TestGroup  │ Description test group │ ['DEV:GOV:9999:SUBGOV', 'DEV:ORG:0000:SUBORGANIZATION'] │
╘══════╧════════════╧════════════════════════╧═════════════════════════════════════════════════════════╛
```

The table above shows the following information about the local groups:

* ID: Local group id.
* CODE: Local group code.
* DESCRIPTION: Local group description.
* MEMBERS: List of members ids

##### 4.2.10.4 Local groups delete

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Deletion of client local groups can be done with:

```bash
xrdsst local-group delete --ss <SECURITY_SERVER_NAME> --local-group <LOCAL_GROUP_ID>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <LOCAL_GROUP_ID> Local group id (can be check with the command [4.2.10.3 Local groups list](#42103-local-groups-list)), 
  multiple values can also be given, separated by comma, e.g., 125,127

##### 4.2.10.5 Local groups member delete

* Access rights: XROAD_SERVICE_ADMINISTRATOR

Deletion of client local group members can be done with:

```bash
xrdsst local-group delete-member --ss <SECURITY_SERVER_NAME> --local-group <LOCAL_GROUP_ID> --member <MEMBERS_ID>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <LOCAL_GROUP_ID> Local group id (it can be check with the command [4.2.10.3 Local groups list](#42103-local-groups-list)), 
  multiple values can also be given, separated by comma, e.g., 123,456
* <MEMBERS_ID> Member (service client) id (local group members can be check with the 
  command [4.2.10.3 Local groups list](#42103-local-groups-list)), multiple values can also be given, separated by comma,
  e.g. DEV:COM:12345:COMPANY, DEV:ORG:123:NIIS
  
If multiple local groups are set as parameters, the command will go through all the local groups searching for the members
that matches with the ones send as parameters and it will delete them.

#### 4.2.11 Backup management

Backups are managed with ``xrdsst backup`` subcommands.

There are no configuration parameters involved, command line arguments are used instead

##### 4.2.11.1 Backup list

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Listing backups can be done with:

```bash
xrdsst backup list --ss <SECURITY_SERVER_NAME>
```

```bash
╒═══════════════════╤═════════════════════════════════╤════════════╕
│ SECURITY_SERVER   │ FILE_NAME                       │ CREATED    │
╞═══════════════════╪═════════════════════════════════╪════════════╡
│ ss3               │ conf_backup_20210817-152554.tar │ 2021/08/17 │
╘═══════════════════╧═════════════════════════════════╧════════════╛
```

* SECURITY_SERVER Security Server name
* FILE_NAME file name of the created Security Server backup
* CREATED backup creation date

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`

##### 4.2.11.2 Backup add

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Adding backups can be done with:

```bash
xrdsst backup add --ss <SECURITY_SERVER_NAME>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`

##### 4.2.11.3 Backup download

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Downloading backups can be done with:

```bash
xrdsst backup download --ss <SECURITY_SERVER_NAME> --file <BACKUP_FILENAME>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <BACKUP_FILENAME> file name of the backup to be downloaded, e.g., conf_backup_20210713-161054.tar, 
  multiple files can also be downloaded, e.g., conf_backup_20210713-161054.tar,conf_backup_20210713-154857.tar

##### 4.2.11.4 Backup delete

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Deletion of backups can be done with:

```bash
xrdsst backup delete --ss <SECURITY_SERVER_NAME> --file <BACKUP_FILENAME>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <BACKUP_FILENAME> file name of the backup to be deleted, e.g., conf_backup_20210713-161054.tar, 
  multiple files can also be deleted, e.g., conf_backup_20210713-161054.tar,conf_backup_20210713-154857.tar

##### 4.2.11.5 Backup restore

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Restoration of configuration from backups can be done with:

```bash
xrdsst backup restore --ss <SECURITY_SERVER_NAME> --file <BACKUP_FILENAME>
```

* <SECURITY_SERVER_NAME> name of the Security Server, e.g., `ss1`
* <BACKUP_FILENAME> file name of the backup to be restored from, e.g., conf_backup_20210713-161054.tar

#### 4.2.12 Diagnostics management

Diagnostic operations for Security Server can be performed with ``xrdsst diagnostics`` subcommands.

##### 4.2.12.1 Global configuration diagnostics

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Listing global-configuration diagnostics can be done with ```xrdsst diagnostics global-configuration```

```bash
╒═══════════════════╤════════════════╤═══════════════╤═════════════════════╤═════════════════════╕
│ SECURITY_SERVER   │ STATUS_CLASS   │ STATUS_CODE   │ PREV_UPDATE         │ NEXT_UPDATE         │
╞═══════════════════╪════════════════╪═══════════════╪═════════════════════╪═════════════════════╡
│ ss3               │ OK             │ SUCCESS       │ 2021/07/20 11:34:48 │ 2021/07/20 11:35:48 │
╘═══════════════════╧════════════════╧═══════════════╧═════════════════════╧═════════════════════╛
```

* SECURITY_SERVER name of the Security Server
* STATUS_CLASS global configuration status class
* STATUS_CODE global configuration status code
* PREV_UPDATE date and time of previous update of the global configuration
* NEXT_UPDATE date and time for the next update of the global configuration

##### 4.2.12.2 OCSP responders diagnostics

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Listing OCSP responders diagnostics can be done with ```xrdsst diagnostics ocsp-responders```

```bash
╒═══════════════════╤══════════════════════════════╤═══════════════════════════╤════════════════╤═══════════════╤═════════════════════╤═════════════════════╕
│ SECURITY_SERVER   │ NAME                         │ URL                       │ STATUS_CLASS   │ STATUS_CODE   │ PREV_UPDATE         │ NEXT_UPDATE         │
╞═══════════════════╪══════════════════════════════╪═══════════════════════════╪════════════════╪═══════════════╪═════════════════════╪═════════════════════╡
│ ss3               │ CN=Test CA, O=X-Road Test CA │ http://10.249.34.187:8888 │ OK             │ SUCCESS       │ 2021/07/20 11:32:52 │ 2021/07/20 11:52:52 │
╘═══════════════════╧══════════════════════════════╧═══════════════════════════╧════════════════╧═══════════════╧═════════════════════╧═════════════════════╛
```

* SECURITY_SERVER name of the Security Server
* NAME name of the certification authority
* URL url of the certification authority
* STATUS_CLASS OCSP status class
* STATUS_CODE OCSP status code
* PREV_UPDATE date and time of previous update of the OCSP
* NEXT_UPDATE date and time for the next update of the OCSP

##### 4.2.12.3 Timestamping services diagnostics

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Listing timestamping services diagnostics can be done with ```xrdsst diagnostics timestamping-services```

```bash
╒═══════════════════╤═══════════════════════════╤════════════════╤════════════════════════════════════╤═════════════════════╕
│ SECURITY_SERVER   │ URL                       │ STATUS_CLASS   │ STATUS_CODE                        │ PREV_UPDATE         │
╞═══════════════════╪═══════════════════════════╪════════════════╪════════════════════════════════════╪═════════════════════╡
│ ss3               │ http://10.249.34.187:8899 │ WAITING        │ ERROR_CODE_TIMESTAMP_UNINITIALIZED │ 2021/07/20 11:34:53 │
╘═══════════════════╧═══════════════════════════╧════════════════╧════════════════════════════════════╧═════════════════════╛
```

* SECURITY_SERVER name of the Security Server
* URL url for the timestamping services
* STATUS_CLASS timestamping services status class
* STATUS_CODE timestamping services status code
* PREV_UPDATE date and time of previous update of the timestamping services

##### 4.2.12.4 All diagnostics

* Access rights: XROAD_SYSTEM_ADMINISTRATOR

Listing all the diagnostics can be done with ```xrdsst diagnostics all```

This command will list all the information from 4.2.12.1 - 4.2.12.3

#### 4.2.13 Keys management

##### 4.2.13.1 List keys

* Access rights: XROAD_SECURITY_OFFICER

Listing certificate keys can be done with:

```bash
xrdsst key list --ss <SECURITY_SERVER_NAME> --token <TOKEN_ID>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <TOKEN_ID> token id, multiple values can also be given, separated by comma, e.g., 0,1

```bash
╒══════════════════════════════════════════╤════════════════════════════════╤════════════════════════════════╤════════════════╤═══════════════════════════════════════════════╤════════════╕
│ ID                                       │ LABEL                          │ NAME                           │ USAGE          │ POSSIBLE ACTIONS                              │      CERTS │
╞══════════════════════════════════════════╪════════════════════════════════╪════════════════════════════════╪════════════════╪═══════════════════════════════════════════════╪════════════╡
│ 61F82DF2B7E1A43DF500FC3E7C8AE4B6D2DD0C7E │ ss1-default-auth-key           │ ss1-default-auth-key           │ AUTHENTICATION │ DELETE, EDIT_FRIENDLY_NAME, GENERATE_AUTH_CSR │          1 │
├──────────────────────────────────────────┼────────────────────────────────┼────────────────────────────────┼────────────────┼───────────────────────────────────────────────┼────────────┤
│ D6EFFF21413B0A6974D087949995B4C677DFD8D1 │ ss1-default-sign-key           │ ss1-default-sign-key           │ SIGNING        │ DELETE, EDIT_FRIENDLY_NAME, GENERATE_SIGN_CSR │          1 │
├──────────────────────────────────────────┼────────────────────────────────┼────────────────────────────────┼────────────────┼───────────────────────────────────────────────┼────────────┤
│ 7D98B5BCF30F59351D9D396EF350AE3899286927 │ ss1-default-sign-key_COM_12345 │ ss1-default-sign-key_COM_12345 │ SIGNING        │ DELETE, EDIT_FRIENDLY_NAME, GENERATE_SIGN_CSR │          1 │
╘══════════════════════════════════════════╧════════════════════════════════╧════════════════════════════════╧════════════════╧═══════════════════════════════════════════════╧════════════╛
```

* ID Id of the key
* LABEL label of the key
* NAME friendly name of the key
* USAGE type of certificate that can be used with the key
* POSSIBLE ACTIONS List of possible actions that can be done to the key sepparated by comma
* CERTS number of certificates added to the key

##### 4.2.13.2 Update keys

* Access rights: XROAD_SECURITY_OFFICER

The friendly name of a key can be updated with:

```bash
xrdsst key update --ss <SECURITY_SERVER_NAME> --key <KEY_ID> --name <FRIENDLY_NAME>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <KEY_ID> key id, e.g., 61F82DF2B7E1A43DF500FC3E7C8AE4B6D2DD0C7E
* <FRIENDLY_NAME> new friendly name to be updated

##### 4.2.13.3 Delete keys

* Access rights: XROAD_SECURITY_OFFICER

Keys can be deleted with:

```bash
xrdsst key delete --ss <SECURITY_SERVER_NAME> --key <KEY_ID> 
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <KEY_ID> key id for delete, e.g., 61F82DF2B7E1A43DF500FC3E7C8AE4B6D2DD0C7E

#### 4.2.14 CSR management

##### 4.2.14.1 List CSR

* Access rights: XROAD_SECURITY_OFFICER

Listing certificate signing request can be done with:

```bash
xrdsst csr list --ss <SECURITY_SERVER_NAME> --token <TOKEN_ID>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <TOKEN_ID> token id, multiple values can also be given, separated by comma, e.g., 0,1

```bash
╒═════════╤══════════════════════════════════════════╤══════════════════════════════════════════╤═════════════╤════════════════╤════════════════════╕
│   TOKEN │ KEY ID                                   │ CSR ID                                   │ OWNER       │ USAGE          │ POSSIBLE ACTIONS   │
╞═════════╪══════════════════════════════════════════╪══════════════════════════════════════════╪═════════════╪════════════════╪════════════════════╡
│       0 │ 6C4A925F1DCF78043CD84DA31868ED20C9616883 │ D9C0A62D8F67BD2A64B9BE26CDAF3064DDE547DE │             │ AUTHENTICATION │ DELETE             │
├─────────┼──────────────────────────────────────────┼──────────────────────────────────────────┼─────────────┼────────────────┼────────────────────┤
│       0 │ F6D58F5400CC9C3D71CF9D42BDE9F51F1BF446B4 │ 6234EAA48BDEF552A1EBC88C4797E147024975ED │ DEV:ORG:111 │ SIGNING        │ DELETE             │
╘═════════╧══════════════════════════════════════════╧══════════════════════════════════════════╧═════════════╧════════════════╧════════════════════╛
```

* TOKEN id of the token
* KEY ID id of the key owner of the CSR
* CSR ID id of the CSR
* OWNER member id who owns the CSR
* USAGE type of certificate that can be used with the key
* POSSIBLE ACTIONS List of possible actions that can be done to the key sepparated by comma

##### 4.2.14.2 Delete CSR

* Access rights: XROAD_SECURITY_OFFICER

Deletion of certificate signing request can be done with:

```bash
xrdsst csr delete --ss <SECURITY_SERVER_NAME> --key <KEY_ID> --csr <CSR_ID>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <KEY_ID>  id of the key who owns the CSR
* <CSR_ID> id of the CSR to be deleted, multiple values can also be given, separated by comma, e.g., D9C0A62D8F67BD2A64B9BE26CDAF3064DDE547DE,6234EAA48BDEF552A1EBC88C4797E147024975ED

#### 4.2.15 Instances management

##### 4.2.15.1 List instances:

* Access rights: Any role

Listing X-Road instances can be done with:

```bash
xrdsst instance list
```

```bash
╒═══════════════════╤═════════════╕
│ SECURITY SERVER   │ INSTANCES   │
╞═══════════════════╪═════════════╡
│ ss1               │ DEV         │
╘═══════════════════╧═════════════╛
```

* SECURITY SERVER name of the Security Server
* INSTANCES List of instances discovered for the Security Server

#### 4.2.16 Security Server management
##### 4.2.16.1 List Security Servers

* Access rights: Any role

Listing Security Servers can be done with:

```bash
xrdsst security-server list
```

This command will display all discovered Security Servers

```bash
╒═══════════════════╤════════╤═══════════╤════════════╤════════════════╤═══════════════╕
│ ID                │ CODE   │ ADDRESS   │ INSTANCE   │ MEMBER CLASS   │   MEMBER CODE │
╞═══════════════════╪════════╪═══════════╪════════════╪════════════════╪═══════════════╡
│ DEV:COM:12345:ss2 │ ss2    │ ss2       │ DEV        │ COM            │         12345 │
├───────────────────┼────────┼───────────┼────────────┼────────────────┼───────────────┤
│ DEV:ORG:111:ss1   │ ss1    │ ss1       │ DEV        │ ORG            │           111 │
╘═══════════════════╧════════╧═══════════╧════════════╧════════════════╧═══════════════╛
```

* ID Security Server id
* CODE Security Server code
* ADDRESS Security Server address
* INSTANCE Security Server instance
* MEMBER CLASS Security Server owner class
* MEMBER CODE Security Server owner code

##### 4.2.16.2 List Security Server version

* Access rights: Any role

Listing Security Server version can be done with:

```bash
xrdsst security-server list-version
```

This command will display the version for the Security Servers stored in the configuration file

```bash
╒═══════════════════╤═══════════╕
│ SECURITY SERVER   │ VERSION   │
╞═══════════════════╪═══════════╡
│ ss1               │ 6.26.0    │
╘═══════════════════╧═══════════╛
```

* SECURITY SERVER code of the Security Server
* VERSION Security Server version number

#### 4.2.17 Internal TLS certificate management

##### 4.2.17.1 Download internal TLS certificate

* Access rights: XROAD_SYSTEM_ADMINISTRATOR or XROAD_SECURITY_OFFICER or XROAD_REGISTRATION_OFFICER or XROAD_SERVICE_ADMINISTRATOR

Internal TLS certificates can be downloaded with:

```bash
xrdsst internal-tls download
```

This command will save a zip file in the `/tmp/` folder containing the public and private keys of the internal TLS certificates.

##### 4.2.17.2 Import internal TLS certificate

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

Internal TLS certificates can be imported with:

```bash
xrdsst internal-tls import --ss <SECURITY_SERVER_NAME> --cert <PATH_TO_CERT>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <PATH_TO_CERT> path for the internal TLS certificate to be imported, e.g., "/tmp/certs/cert.pem"

##### 4.2.17.3 Generate new key internal TLS certificate 

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

New key for the internal TLS certificate can be generated with:

```bash
xrdsst internal-tls generate-key --ss <SECURITY_SERVER_NAME> 
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`

##### 4.2.17.4 Generate new csr TLS certificate

* Access rights: XROAD_SYSTEM_ADMINISTRATOR and XROAD_SECURITY_OFFICER

New CSR for the internal TLS certificate can be generated with:

```bash
xrdsst internal-tls generate-csr --ss <SECURITY_SERVER_NAME> --name <DISTINGUISHED_NAME>
```

* <SECURITY_SERVER_NAME> Security Server name, e.g., `ss1`
* <DISTINGUISHED_NAME> distinguished name for the certificate,  e.g. "CN=mysecurityserver.example.com,O=My Organization,C=FI"

## 5 Failure recovery and interpretation of errors
> "In failure, software reveals its structure" -- Kevlin Henney

It is essential to have a firm grip on both *what* is going and *where* in the
distributed system to fix upcoming problems encountered while using the toolkit.
For single configuration operations, it is important that those are performed in
non-conflicting order, e.g., it is impossible to perform most token operations
before the token has been logged in. If this order is not respected, the output
from the application will refer to the commands which successful application
is required to be completed beforehand, e.g.:

```bash
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
using single-operations for (re-)applying some part of Security Server configuration.
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

```bash
$ xrdsst -c brandnew.yaml apply
API key "d8cd2476-c8dc-420a-bcc2-c8636766661b" for Security Server ss8 created.
AUTO ['init']->'ss8'
Uploading configuration anchor for Security Server: ss8
Upload of configuration anchor from "/home/user/demo-anchor.xml" successful
Initializing Security Server: ss8
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
usually the last one reported refers to the actual error, e.g., misaligned client block at
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

```bash
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

```text
security_server[1] missing required 'name' definition.
security_server[1] missing required 'url' definition.
security_server[3] missing required 'url' definition.
```
indicates that 1st and 3rd Security Server definitions with specified errors,
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

```bash
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
Security Server have been disabled and ``xrdsst client register`` unable to proceed.
This is one of these cases where management services Security Server is somewhat 
likely to belong to the same organization, and thus the error might be
sorted out inside organization, getting the services enabled again. In any case,
the key to successfully resolving such situations is to pay careful attention
to the error messages and accompanying ASCII diagram with message flow, to not
spend time at searching for the problem in the wrong places.

### 5.5 Recovery from misconfiguration
This version of toolkit does not yet offer explicit support for backup and restore
operations of the Security Server (scheduled for next release of the toolkit). In
case something goes so wrong that way out or way back cannot be seen, it is possible
to use nightly backups that are kept at Security Server to revert to earlier state.
Overview of existing automatic backups is accessible from web administration console
of the Security Server, in the "Settings" menu. More information about functionality
can be found in [UG-SS](#Ref_SS-UG).


## 6 Load balancer setup

 It is possible to setup a Load balancer environment described in [X-Road: External Load Balancer Installation Guide](https://github.com/nordic-institute/X-Road/blob/develop/doc/Manuals/LoadBalancing/ig-xlb_x-road_external_load_balancer_installation_guide.md) 
 and configure it using the toolkit.

Under the [X-Road](https://github.com/nordic-institute/X-Road) project there are ansible 
scripts prepared to install the cluster, for doing that we must follow the instructions 
[Security server cluster setup](https://github.com/nordic-institute/X-Road/tree/develop/ansible/ss_cluster#security-server-cluster-setup).

Once the cluster is ready we can use the toolkit to configure the Load Balancer setup, for doing that, we must configure the Primary Security Server as any other single Security Server, setting in the
`SECURITY_SERVER_INTERNAL_FQDN_OR_IP` property with the FQDN belonging to the Primary.

## 7 Using the Toolkit to configure highly available services using the built-in Security Server internal load balancing

In order to configure a highly available service using the built-in Security Server load balancing, at least two security
servers need to be configured with the same subsystem/service.

An example configuration file to be used:

```yaml
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
It's possible to add other members and subsystems to a Security Server using the toolkit.
For doing that we need to add the members and subsystems in the clients section of the configuration file. 
For adding a new member we must delete the properties 'service_descriptions' and 'subsystem_code'.
For example if we have the owner member 'ORG/111/ORGANIZATION/SUB' and want to add the new member 'COM/12345/COMPANY' and the subsystem 'COM/12345/COMPANY/SUB' we should fill the
configuration file like this:

```yaml
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

```bash
xrdsst client add-client
```

- Create the SIGN key and CSRS for the new member

```bash
xrdsst token init-keys
```

- Download this CSRS with the command:

```bash
xrdsst cert download-csrs 
```

Sign it and add it to the list of certificates in the configuration:

```yaml
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

```bash
xrdsst cert import
```

- Register the new member by running the command:

```bash
xrdsst client register
```

## 9 Renew expiring certificates

It is recommended to renew the certificates in advance before they expire. You can check the expiration date through the 
UI in the tab <strong>KEYS AND CERTIFICATE</strong> => <strong>SIGN AND AUTH KEYS</strong> column <strong>Expires</strong>.
To renew the certificates we must:

1. Create new CRS keys for the new certificates using the [4.2.3.4 Token create-new-keys](#4234-token-create-new-keys) command. 
2. Download and sign the new certificates using the [4.2.5.1 Certificate download CSRS](#4251-certificate-download-csrs) command.
3. Add the signed certificates to the [certificates list](#322-security-servers-configuration) of the Security Server 
   in the configuration file.
4. Import the certificates by running the [certificate import](#4252-certificate-import) command.
5. Activate the certificates by running the [certificate activation](#4254-certificate-activation) command.
6. Register the new certificates by running the [certificate registration](#4253-certificate-registration) command.
7. Wait until the new certificates have the OCSP in Good state and the Status in Registered. We can check this
   by running the [List certificates](#4256-list-certificates) command. 
   It's recommended to wait at least one day so that the new certificates can be distributed so the access server does not crash.
7. Disable the old certificates by running the [Certificate disable](#4257-certificate-disable) command.
8. Unregister the old  certificates by running the [Certificate unregister](#4258-certificate-unregister) command.
9. Delete the old AUTH and SIGN keys and certificates by running the [4.2.13.3 Delete keys](#42133-delete-keys) command.

## 10 Change Security Server owner

To change the Security Server owner, two registered Owner members have to be available. 
1. Add a new member to the Security Server and register it. For doing that, follow the guide [8 Multitenancy](#8-multitenancy).
2. Run the command [4.2.6.6 Client change owner](#4266-client-change-owner). This command submits a request for owner
change to X-Road governing authority and it will create the AUTH key and CSRs for the AUTH certificate of the new member.
3. Download the certificate created in the previous step using the command [4.2.5.1 Certificate download CSRS](#4251-certificate-download-csrs).
4. Sign the AUTH certificate and import it using the command [4.2.5.2 Certificate import](#4252-certificate-import).
5. Activate  the AUTH certificate using the command [4.2.5.2 Certificate import](#4252-certificate-import).
6. Register the AUTH certificate with the command [4.2.5.4 Certificate activation](#4254-certificate-activation).
7. Once the owner is changed, make sure to update the properties `owner_dn_org`, `owner_member_class`, `owner_member_code` in the configuration file
(`security_server` section) with the values of the new member.

## 11 Certificate profile support

The toolkit has support for multiple profiles to choose between:
- EJBCA: Ejbca implementation
- FI: Finnish implementation
- FO: Faroe Islands implementation
- IS: Icelandic Implementation
- SKKLASS3: Estonian SkKlass3 Implementation

To select one of these profiles, we should fill the property `profile` in the configuration file (`security_server` section) with the name of the profile,
to choose between: "EJBCA", "FI", "FO" and "IS" and "SKKLASS3"

This property is optional, if not set, the default profile will be EJBCA.

