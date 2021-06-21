import copy
import os

import cement.utils.fs

from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients, ConfKeysSecServerClientServiceDesc, \
    ConfKeysSecServerClientServiceDescEndpoints
from xrdsst.core.util import convert_swagger_enum
from xrdsst.models import ConnectionType, ServiceType


def validator_msg_prefix(ss_config, operation):
    return "'" + ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "' [" + str(operation) + "]: "


# Adds operation error for unfilled key to /errors/ and returns True (False) when requirements met (not met).
def require_fill(key, ss_config, operation, errors):
    val = ss_config.get(key)
    if val is None:
        errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "'" + " missing required value.")
    return bool(val)


def require_fill_length(key, ss_config, operation, errors):
    val = ss_config.get(key)
    if val is None or len(val) == 0 or not isinstance(val, list):
        errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "'" + " missing required list value.")
    return bool(val)


# Adds operation error for (unfilled) / (not matching swagger enum) key to /errors/. Return True/False if valid/invalid.
def require_swagger_enum_fill(type_, key, ss_config, operation, errors):
    val = ss_config.get(key)

    try:
        convert_swagger_enum(type_, val)
    except SyntaxWarning as syn_err:
        errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "' " + str(syn_err))
        return False

    return True


# Adds operation error into /errors/ for filled key if its value refers to unreadable or empty file or to a directory.
# Returns True if no errors detected, False otherwise.
def require_readable_file_path(key, ss_config, operation, errors):
    if not require_fill(key, ss_config, operation, errors):
        return False

    config_file_path = ss_config[key]
    file_path = cement.utils.fs.join_exists(config_file_path)
    if not file_path[1]:
        errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "'" + " references non-existent file '" + file_path[0] + "'.")
        return False

    if os.path.isdir(file_path[0]):
        errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "'" + " references directory '" + file_path[0] + "'.")
        return False

    try:
        fh = open(file_path[0], 'rb')
        single_byte = fh.read(1)
        fh.close()
        if len(single_byte) != 1:
            errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "'" + " references empty file '" + file_path[0] + "'.")
            return False
    except PermissionError:
        errors.append(validator_msg_prefix(ss_config, operation) + "'" + key + "'" + " references unreadable file '" + file_path[0] + "'.")

    return True


def validate_config_init(ss_config, operation, errors):
    err_cnt = len(errors)

    require_fill(ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_SERVER_CODE, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_PIN, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID, ss_config, operation, errors)
    if require_fill(ConfKeysSecurityServer.CONF_KEY_ANCHOR, ss_config, operation, errors):
        require_readable_file_path(ConfKeysSecurityServer.CONF_KEY_ANCHOR, ss_config, operation, errors)

    return len(errors) <= err_cnt


def validate_config_token_login(ss_config, operation, errors):
    err_cnt = len(errors)

    require_fill(ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_PIN, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID, ss_config, operation, errors)

    return len(errors) <= err_cnt


def validate_config_timestamp_init(ss_config, operation, errors):
    # Timestamping service initialization uses only information from central server and security server
    # and has no specific configuration file section.
    return True


def validate_config_token_init_keys(ss_config, operation, errors):
    err_cnt = len(errors)

    require_fill(ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_SERVER_CODE, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_DN_C, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_DN_ORG, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID, ss_config, operation, errors)
    require_fill(ConfKeysSecurityServer.CONF_KEY_FQDN, ss_config, operation, errors)

    return len(errors) <= err_cnt


def validate_config_cert_import(ss_config, operation, errors):
    err_cnt = len(errors)

    if not require_fill(ConfKeysSecurityServer.CONF_KEY_CERTS, ss_config, operation, errors):
        # Since this is such a special case, amend the error message slightly for further clues.
        errors.append(errors.pop() + " Get CSRs ['cert download-csrs'] signed at approved CA and fill element accordingly.")
    else:
        # List conversion to dict is bit stupid here, but at the moment sufficient, if similar crops up, go multi-type with require_*.
        certs_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CERTS])
        cert_file_list_dict = {}
        for cert_ix in range(0, len(certs_config)):
            cert_file_list_dict[str(cert_ix + 1)] = certs_config[cert_ix]

        for cert_ix in range(0, len(certs_config)):
            cert_file_list_dict[ConfKeysSecurityServer.CONF_KEY_NAME] = (
                    ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                    ConfKeysSecurityServer.CONF_KEY_CERTS + "[" + str(cert_ix + 1) + "]"
            )

            require_readable_file_path(str(cert_ix + 1), cert_file_list_dict, operation, errors)

    return len(errors) <= err_cnt


def validate_config_cert_register(ss_config, operation, errors):
    # AUTH cert registration has no specific configuration file section / keys.
    return True


def validate_config_cert_activate(ss_config, operation, errors):
    # AUTH cert activation has no specific configuration file section / keys.
    return True


# 'download-csrs' is not an operation, but define validation with same convention as for others, used separately.
def validate_config_cert_download_csrs(ss_config, operation, errors):
    err_cnt = len(errors)

    require_fill(ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID, ss_config, operation, errors)

    return len(errors) <= err_cnt


# Validation requirements for client adding and registration are at least currently identical.
def validate_config_client_add_or_register(ss_config, operation, errors):
    if not ss_config.get(ConfKeysSecurityServer.CONF_KEY_CLIENTS):
        return True

    err_cnt = len(errors)

    if require_fill(ConfKeysSecurityServer.CONF_KEY_CLIENTS, ss_config, operation, errors):
        for i in range(0, len(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])):
            # Pass on the security server context in 'server_name.client_config_id[x]
            ss_config_client_slice = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS][i])
            ss_config_client_slice[ConfKeysSecurityServer.CONF_KEY_NAME] = (
                    ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                    # Count indexes from 1 everywhere, as in key sanity reports of load_config()
                    ConfKeysSecurityServer.CONF_KEY_CLIENTS + '[' + str(i + 1) + ']'
            )

            require_fill(
                ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CLASS,
                ss_config_client_slice, operation, errors
            )

            require_fill(
                ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CODE,
                ss_config_client_slice, operation, errors
            )

            require_fill(
                ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_NAME,
                ss_config_client_slice, operation, errors
            )

            if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS in ss_config_client_slice:
                require_fill(
                    ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE,
                    ss_config_client_slice, operation, errors
                )

            require_swagger_enum_fill(
                ConnectionType,
                ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_CONNECTION_TYPE,
                ss_config_client_slice, operation, errors
            )

    return len(errors) <= err_cnt


def validate_config_service_desc(ss_config, operation, errors):
    if not ss_config.get(ConfKeysSecurityServer.CONF_KEY_CLIENTS):
        return True

    err_cnt = len(errors)

    clients_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])

    for client_ix in range(0, len(clients_config)):
        if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS not in clients_config[client_ix]:
            continue
        # Make readable reference
        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                ConfKeysSecurityServer.CONF_KEY_CLIENTS + '[' + str(client_ix + 1) + ']'
        )
        require_fill_length(
            ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS,
            clients_config[client_ix], operation, errors)

        if clients_config[client_ix].get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS):
            service_desc_config = copy.deepcopy(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS])
            for service_desc_ix in range(0, len(service_desc_config)):
                service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                        ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS + '[' + str(service_desc_ix + 1) + ']'
                )

                require_swagger_enum_fill(ServiceType,
                                          ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE,
                                          service_desc_config[service_desc_ix], operation, errors)

                require_fill(
                    ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_URL,
                    service_desc_config[service_desc_ix], operation, errors)

                if ServiceType.WSDL != service_desc_config[service_desc_ix].get(ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE):
                    require_fill(
                        ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_REST_SERVICE_CODE,
                        service_desc_config[service_desc_ix], operation, errors)

    return len(errors) <= err_cnt


def validate_config_service_access(ss_config, operation, errors):
    if not ss_config.get(ConfKeysSecurityServer.CONF_KEY_CLIENTS):
        return True

    err_cnt = len(errors)

    clients_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])
    for client_ix in range(0, len(clients_config)):
        if not clients_config[client_ix].get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS):
            continue

        # Make readable reference
        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                ConfKeysSecurityServer.CONF_KEY_CLIENTS + '[' + str(client_ix + 1) + ']'
        )

        service_desc_config = copy.deepcopy(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS])
        for service_desc_ix in range(0, len(service_desc_config)):
            service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                    clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                    ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS + '[' + str(service_desc_ix + 1) + ']'
            )
            has_access = False
            if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS in service_desc_config[service_desc_ix]:
                has_access = True
                require_fill_length(
                    ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS,
                    service_desc_config[service_desc_ix], operation, errors)
            else:
                if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES in service_desc_config[service_desc_ix]:
                    services = service_desc_config[service_desc_ix][ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES]
                    for service_ix in range(0, len(services)):
                        if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS in services[service_ix]:
                            services[service_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                                    "%s.service.[%s]" % (service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME], str(service_ix + 1))
                            )
                            has_access = True
                            require_fill_length(
                                ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS,
                                services[service_ix], operation, errors)
            if has_access:
                require_swagger_enum_fill(ServiceType,
                                          ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE,
                                          service_desc_config[service_desc_ix], operation, errors)

                require_fill(
                    ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_URL,
                    service_desc_config[service_desc_ix], operation, errors)

                if ServiceType.REST == service_desc_config[service_desc_ix].get(ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE):
                    require_fill(
                        ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_REST_SERVICE_CODE,
                        service_desc_config[service_desc_ix], operation, errors)

    return len(errors) <= err_cnt


def validate_config_service_desc_service(ss_config, operation, errors):
    if not ss_config.get(ConfKeysSecurityServer.CONF_KEY_CLIENTS):
        return True

    err_cnt = len(errors)

    clients_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])
    for client_ix in range(0, len(clients_config)):
        if not clients_config[client_ix].get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS):
            continue

        # Make readable reference
        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                ConfKeysSecurityServer.CONF_KEY_CLIENTS + '[' + str(client_ix + 1) + ']'
        )

        service_desc_config = copy.deepcopy(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS])
        for service_desc_ix in range(0, len(service_desc_config)):
            service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                    clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                    ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS + '[' + str(service_desc_ix + 1) + ']'
            )

            require_swagger_enum_fill(ServiceType,
                                      ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE,
                                      service_desc_config[service_desc_ix], operation, errors)

            require_fill(
                ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_URL,
                service_desc_config[service_desc_ix], operation, errors)

            require_fill(
                ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_URL_ALL,
                service_desc_config[service_desc_ix], operation, errors)

            require_fill(
                ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SSL_AUTH_ALL,
                service_desc_config[service_desc_ix], operation, errors)

            require_fill(
                ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TIMEOUT_ALL,
                service_desc_config[service_desc_ix], operation, errors)

            if ServiceType.REST == service_desc_config[service_desc_ix].get(ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE):
                require_fill(
                    ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_REST_SERVICE_CODE,
                    service_desc_config[service_desc_ix], operation, errors)

    return len(errors) <= err_cnt


def validate_config_service_desc_service_endpoints(ss_config, operation, errors):
    if not ss_config.get(ConfKeysSecurityServer.CONF_KEY_CLIENTS):
        return True

    err_cnt = len(errors)

    clients_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])
    for client_ix in range(0, len(clients_config)):
        if not clients_config[client_ix].get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS):
            continue

        # Make readable reference
        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                ConfKeysSecurityServer.CONF_KEY_CLIENTS + '[' + str(client_ix + 1) + ']'
        )

        service_desc_config = copy.deepcopy(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS])
        for service_desc_ix in range(0, len(service_desc_config)):
            if service_desc_config[service_desc_ix]["type"] != ServiceType().WSDL:
                service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                        ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS + '[' + str(service_desc_ix + 1) + ']'
                )
                if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS in service_desc_config[service_desc_ix]:
                    require_fill_length(
                        ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS,
                        service_desc_config[service_desc_ix], operation, errors)

                    if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS in service_desc_config[service_desc_ix]:
                        endpoints_config = copy.deepcopy(
                            service_desc_config[service_desc_ix][ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS])
                        if endpoints_config:
                            for endpoint_ix in range(0, len(endpoints_config)):
                                endpoints_config[endpoint_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                                        service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                                        ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS + '[' + str(endpoint_ix + 1) + ']'
                                )

                                require_fill(
                                    ConfKeysSecServerClientServiceDescEndpoints.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_METHOD,
                                    endpoints_config[endpoint_ix], operation, errors)

                                require_fill(
                                    ConfKeysSecServerClientServiceDescEndpoints.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_PATH,
                                    endpoints_config[endpoint_ix], operation, errors)

    return len(errors) <= err_cnt


def validate_config_service_desc_service_endpoints_access(ss_config, operation, errors):
    if not ss_config.get(ConfKeysSecurityServer.CONF_KEY_CLIENTS):
        return True

    err_cnt = len(errors)

    clients_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])
    for client_ix in range(0, len(clients_config)):
        if not clients_config[client_ix].get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS):
            continue

        # Make readable reference
        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                ConfKeysSecurityServer.CONF_KEY_CLIENTS + '[' + str(client_ix + 1) + ']'
        )

        service_desc_config = copy.deepcopy(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS])
        for service_desc_ix in range(0, len(service_desc_config)):
            if service_desc_config[service_desc_ix]["type"] != ServiceType().WSDL:
                service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                        clients_config[client_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                        ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS + '[' + str(service_desc_ix + 1) + ']'
                )

                if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS in service_desc_config[service_desc_ix]:
                    require_fill_length(
                        ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS,
                        service_desc_config[service_desc_ix], operation, errors)

                    if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS in service_desc_config[service_desc_ix]:
                        endpoints_config = copy.deepcopy(
                            service_desc_config[service_desc_ix][ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS])
                        if endpoints_config:
                            for endpoint_ix in range(0, len(endpoints_config)):
                                endpoints_config[endpoint_ix][ConfKeysSecurityServer.CONF_KEY_NAME] = (
                                        service_desc_config[service_desc_ix][ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                                        ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS + '[' + str(endpoint_ix + 1) + ']'
                                )

                                require_fill(
                                    ConfKeysSecServerClientServiceDescEndpoints.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_METHOD,
                                    endpoints_config[endpoint_ix], operation, errors)

                                require_fill(
                                    ConfKeysSecServerClientServiceDescEndpoints.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_PATH,
                                    endpoints_config[endpoint_ix], operation, errors)

                                if ConfKeysSecServerClientServiceDescEndpoints.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_ACCESS in endpoints_config[endpoint_ix]:
                                    require_fill_length(
                                        ConfKeysSecServerClientServiceDescEndpoints.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_ACCESS,
                                        endpoints_config[endpoint_ix], operation, errors)

    return len(errors) <= err_cnt


def validate_config_tls_cert_import(ss_config, operation, errors):
    err_cnt = len(errors)
    tls_certs = 0

    if ConfKeysSecurityServer.CONF_KEY_TLS_CERTS in ss_config and ss_config[
        ConfKeysSecurityServer.CONF_KEY_TLS_CERTS] is not None:

        tls_certs_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_TLS_CERTS])
        cert_file_list_dict = {}
        for cert_ix in range(0, len(tls_certs_config)):
            cert_file_list_dict[str(cert_ix + 1)] = tls_certs_config[cert_ix]

        for tls_cert_ix in range(0, len(ss_config[ConfKeysSecurityServer.CONF_KEY_TLS_CERTS])):
            cert_file_list_dict[ConfKeysSecurityServer.CONF_KEY_NAME] = (
                    ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                    ConfKeysSecurityServer.CONF_KEY_TLS_CERTS + "[" + str(tls_cert_ix + 1) + "]"
            )
            require_readable_file_path(str(tls_cert_ix + 1), cert_file_list_dict, operation, errors)
            tls_certs = tls_certs + 1

    if ConfKeysSecurityServer.CONF_KEY_CLIENTS in ss_config:
        clients_config = copy.deepcopy(ss_config[ConfKeysSecurityServer.CONF_KEY_CLIENTS])
        for client_ix in range(0, len(clients_config)):
            if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES in clients_config[client_ix] and \
                    clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES] is not None:

                tls_certs_config = copy.deepcopy(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES])
                cert_file_list_dict = {}
                for cert_ix in range(0, len(tls_certs_config)):
                    cert_file_list_dict[str(cert_ix + 1)] = tls_certs_config[cert_ix]

                for tls_cert_ix in range(0, len(clients_config[client_ix][ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES])):
                    cert_file_list_dict[ConfKeysSecurityServer.CONF_KEY_NAME] = (
                            ss_config[ConfKeysSecurityServer.CONF_KEY_NAME] + "." +
                            ConfKeysSecurityServer.CONF_KEY_CLIENTS + "[" + str(client_ix + 1) + "]" + "." +
                            ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES + "[" + str(tls_cert_ix + 1) + "]"
                    )
                    require_readable_file_path(str(tls_cert_ix + 1), cert_file_list_dict, operation, errors)
                    tls_certs = tls_certs + 1

    if tls_certs == 0:
        errors.append(
            errors.pop() if errors else '' + " Internal TLS certificates, missing required value. ")

    return len(errors) <= err_cnt

def validate_config_certificate_operations(ss_config, operation, errors):
    err_cnt = len(errors)

    if ConfKeysSecurityServer.CONF_KEY_CERTS_MANAGEMENT in ss_config:
        require_fill_length(
            ConfKeysSecurityServer.CONF_KEY_CERTS_MANAGEMENT,
            ss_config, operation, errors)
    return len(errors) <= err_cnt

