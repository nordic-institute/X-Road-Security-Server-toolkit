# X-Road Security Server Toolkit configuration guide

**Technical Specification**

Version: 1.0 
Doc. ID: XRDSST-CONF

| Date       | Version     | Description                                                                  | Author             |
|------------|-------------|------------------------------------------------------------------------------|--------------------|
| 10.11.2020 | 1.0         | Initial draft                                                                | Bert Viikmäe       |


## Table of Contents

<!-- vim-markdown-toc GFM -->
* [License](#license)
* [1 Introduction](#1-introduction)
* [2 Configuration of X-Road Security Server](#2-configuration-of-x-road-security-server)
    * [2.1 General](#21-general)
    * [2.2 Format of configuration file](#22-format-of-configuration-file)
* [3 Running the X-Road Security Server Toolkit](#3-running-the-x-road-security-server-toolkit)
    * [3.1 The automatic configuration of a single security server](#31-the-automatic-configuration-of-a-single-security-server)


<!-- vim-markdown-toc -->

## License

This document is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

## 1 Introduction

This specification describes automatic configuration of X-Road security servers using X-Road Security Server Toolkit

## 2 Configuration of X-Road Security Server

### 2.1 General

The automatic configuration of X-Road security servers using the X-Road Security Server Toolkit relies on configuration files, where exact configuration values have to be specified

### 2.2 Format of configuration file

security-server:
  - name: <SECURITY_SERVER_NAME>
    url: https://<SECURITY_SERVER_FQDN_OR_IP>:4000/api/v1
    api_key: X-Road-apikey token=<API_KEY>
    configuration_anchor: /path/to/configuration-anchor.xml
    owner_member_class: <MEMBER_CLASS>
    owner_member_code: <MEMBER_CODE>
    security_server_code: <SERVER_CODE>
    software_token_pin: <SOFT_TOKEN_PIN>
    
<SECURITY_SERVER_NAME> should be substituted with the installed security server name, e.g. ss1
<SECURITY_SERVER_FQDN_OR_IP> should be substituted with the IP address or host name of the installed security server, e.g. ss1
<API_KEY> should be substituted with the api-key of the installed security server
/path/to/configuration-anchor.xml should be substituted with the correct path to the configuration anchor file, e.g. "/etc/xroad/configuration-anchor.xml"
<MEMBER_CLASS> should be substituted with the member class obtained from the Central Server, e.g. GOV
<MEMBER_CODE> should be substituted with the member code obtained from the Central Server, e.g. 1234
<SERVER_CODE> should be substituted with the server code of the installed security server, e.g. SS1
<SOFT_TOKEN_PIN> should be substituted with a desired numeric pin code

## 3 Running the X-Road Security Server Toolkit

The X-Road Security Server Toolkit is run from the command line by typing:

    xrdsst init

### 3.1 The automatic configuration of a single security server

In the first stage of the automatic process, the security server(s) will be initialized according to the configuration data specified
in the configuration file (base.yaml). First, a configuration anchor is uploaded and then the initialization of the security server
is performed with respective <MEMBER_CLASS>, <MEMBER_CODE>, <SERVER_CODE> and <SOFT_TOKEN_PIN> values.



