import copy
import json
import os
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests

from xrdsst.controllers.base import BaseController
from xrdsst.controllers.status import ServerStatus
from xrdsst.core.api_util import StatusRoles, StatusVersion, StatusGlobal, StatusServerInitialization, \
    StatusServerTimestamping, StatusToken, StatusKeys, StatusCsrs, StatusCerts
from xrdsst.core.util import default_auth_key_label, convert_swagger_enum
from xrdsst.models import ConnectionType, TokenInitStatus, User, InitializationStatus, GlobalConfDiagnostics, Token, \
    TokenStatus, TokenType, PossibleAction


class ObjectStruct:
    def __init__(self, **entries): self.__dict__.update(entries)

    def __eq__(self, other): return self.__dict__ == other.__dict__

    def __ne__(self, other): return self.__dict__ != other.__dict__


class UserTestData:
    with_all_grants = User(
        username='api-key-N',
        roles=[
            'ROLE_XROAD_REGISTRATION_OFFICER', 'ROLE_XROAD_SECURITYSERVER_OBSERVER', 'ROLE_XROAD_SECURITY_OFFICER',
            'ROLE_XROAD_SERVICE_ADMINISTRATOR', 'ROLE_XROAD_SYSTEM_ADMINISTRATOR'
        ],
        permissions=[
            'ACTIVATE_DEACTIVATE_TOKEN', 'ACTIVATE_DISABLE_AUTH_CERT', 'ACTIVATE_DISABLE_SIGN_CERT', 'ADD_CLIENT',
            'ADD_CLIENT_INTERNAL_CERT', 'ADD_LOCAL_GROUP', 'ADD_OPENAPI3', 'ADD_OPENAPI3_ENDPOINT', 'ADD_TSP',
            'ADD_WSDL', 'BACKUP_CONFIGURATION', 'CREATE_API_KEY', 'DELETE_AUTH_CERT', 'DELETE_AUTH_KEY',
            'DELETE_CLIENT', 'DELETE_CLIENT_INTERNAL_CERT', 'DELETE_ENDPOINT', 'DELETE_KEY', 'DELETE_LOCAL_GROUP',
            'DELETE_SIGN_CERT', 'DELETE_SIGN_KEY', 'DELETE_TSP', 'DELETE_WSDL', 'DIAGNOSTICS', 'DOWNLOAD_ANCHOR',
            'EDIT_ACL_SUBJECT_OPEN_SERVICES', 'EDIT_CLIENT_INTERNAL_CONNECTION_TYPE', 'EDIT_ENDPOINT_ACL',
            'EDIT_KEY_FRIENDLY_NAME', 'EDIT_LOCAL_GROUP_DESC', 'EDIT_LOCAL_GROUP_MEMBERS', 'EDIT_OPENAPI3',
            'EDIT_OPENAPI3_ENDPOINT', 'EDIT_REST', 'EDIT_SERVICE_ACL', 'EDIT_SERVICE_PARAMS',
            'EDIT_TOKEN_FRIENDLY_NAME', 'EDIT_WSDL', 'ENABLE_DISABLE_WSDL', 'EXPORT_INTERNAL_TLS_CERT',
            'GENERATE_AUTH_CERT_REQ', 'GENERATE_INTERNAL_TLS_CSR', 'GENERATE_INTERNAL_TLS_KEY_CERT', 'GENERATE_KEY',
            'GENERATE_SIGN_CERT_REQ', 'IMPORT_AUTH_CERT', 'IMPORT_INTERNAL_TLS_CERT', 'IMPORT_SIGN_CERT', 'INIT_CONFIG',
            'REFRESH_OPENAPI3', 'REFRESH_REST', 'REFRESH_WSDL', 'RESTORE_CONFIGURATION', 'REVOKE_API_KEY',
            'SEND_AUTH_CERT_DEL_REQ', 'SEND_AUTH_CERT_REG_REQ', 'SEND_CLIENT_DEL_REQ', 'SEND_CLIENT_REG_REQ',
            'SEND_OWNER_CHANGE_REQ', 'UPDATE_API_KEY', 'UPLOAD_ANCHOR', 'VIEW_ACL_SUBJECT_OPEN_SERVICES', 'VIEW_ANCHOR',
            'VIEW_API_KEYS', 'VIEW_APPROVED_CERTIFICATE_AUTHORITIES', 'VIEW_AUTH_CERT', 'VIEW_CLIENTS',
            'VIEW_CLIENT_ACL_SUBJECTS', 'VIEW_CLIENT_DETAILS', 'VIEW_CLIENT_INTERNAL_CERTS',
            'VIEW_CLIENT_INTERNAL_CERT_DETAILS', 'VIEW_CLIENT_INTERNAL_CONNECTION_TYPE', 'VIEW_CLIENT_LOCAL_GROUPS',
            'VIEW_CLIENT_SERVICES', 'VIEW_ENDPOINT', 'VIEW_ENDPOINT_ACL', 'VIEW_INTERNAL_TLS_CERT', 'VIEW_KEYS',
            'VIEW_MEMBER_CLASSES', 'VIEW_SECURITY_SERVERS', 'VIEW_SERVICE_ACL', 'VIEW_SIGN_CERT', 'VIEW_SYS_PARAMS',
            'VIEW_TSPS', 'VIEW_UNKNOWN_CERT', 'VIEW_VERSION', 'VIEW_XROAD_INSTANCES'
        ]
    )


class InitTestData:
    all_initialized = InitializationStatus(True, True, True, TokenInitStatus.INITIALIZED)


class DiagnosticsTestData:
    global_ok_success = GlobalConfDiagnostics(
        status_class="OK",
        status_code="SUCCESS",
        prev_update_at=datetime.now(),
        next_update_at=datetime.now() + timedelta(minutes=5)
    )


class TokenTestData:
    token_keyless = Token(
        available=True,
        id=0,
        logged_in=True,
        name='softToken-0',
        possible_actions=None,
        read_only=False,
        saved_to_configuration=True,
        serial_number=None,
        status=TokenStatus.OK,
        token_infos=[{'key': 'Type'}, {'value': 'Software'}],
        type=TokenType.SOFTWARE,
        keys=[]
    )


class StatusTestData:
    server_status_unconnected = ServerStatus(
        security_server_name='nameofss',
        connectivity_status=(False, 'Failure for test'),
    )

    server_status_uninitialized_global_failing = ServerStatus(
        security_server_name='nameofss',
        connectivity_status=(True, ''),
        roles_status=StatusRoles(permitted=True, roles=['ROLE_XROAD_SYSTEM_ADMINISTRATOR', 'ROLE_XROAD_SECURITY_OFFICER']),
        version_status=StatusVersion(version="6.25.0"),
        global_status=StatusGlobal(
            class_="FAIL",
            code="INTERNAL",
            updated=DiagnosticsTestData.global_ok_success.prev_update_at,
            refresh=DiagnosticsTestData.global_ok_success.next_update_at
        ),
        server_init_status=StatusServerInitialization()
    )

    server_status_essentials_complete = ServerStatus(
        security_server_name='nameofss',
        connectivity_status=(True, ''),
        roles_status=StatusRoles(permitted=True, roles=UserTestData.with_all_grants.roles),
        version_status=StatusVersion(version="6.25.0"),
        global_status=StatusGlobal(
            class_=DiagnosticsTestData.global_ok_success.status_class,
            code=DiagnosticsTestData.global_ok_success.status_code,
            updated=DiagnosticsTestData.global_ok_success.prev_update_at,
            refresh=DiagnosticsTestData.global_ok_success.next_update_at
        ),
        server_init_status=StatusServerInitialization(
            id_="TEST:VOG:6666:SECS",
            has_anchor=True,
            has_server_code=True,
            server_code='SECS',
            has_server_owner=True,
            server_owner='6666',
            token_init_status=TokenInitStatus.INITIALIZED
        ),
        timestamping_status=[StatusServerTimestamping(name='named-tsa', url='https://some.where.com')],
        token_status=StatusToken(
            id_=str(TokenTestData.token_keyless.id),
            name=TokenTestData.token_keyless.name,
            status=TokenTestData.token_keyless.status,
            logged_in=TokenTestData.token_keyless.logged_in
        ),
        status_keys=StatusKeys(
            key_count=2,
            sign_key_count=1,
            auth_key_count=1,
            has_toolkit_sign_key=True,
            toolkit_sign_key_id='5D3C550E99D06D8C2D6722996B22A5470EA353B6',
            has_sign_key=True,
            has_toolkit_auth_key=True,
            toolkit_auth_key_id='8798F7D899EDCC8D5777772AFA5C189B653CB470',
            has_auth_key=True
        ),
        status_csrs=StatusCsrs(
            sign_csr_count=0,
            auth_csr_count=0,
            has_toolkit_sign_csr=False,
            has_sign_csr=False,
            has_toolkit_auth_csr=False,
            has_auth_csr=False
        ),
        status_certs=StatusCerts(
            has_sign_cert=True,
            has_toolkit_sign_cert=True,
            toolkit_sign_cert_hash="662C9B4B0D48CABAB2EDC72BC5DF3CF789A066F5",
            has_auth_cert=True,
            auth_cert_actions=[PossibleAction.DISABLE, PossibleAction.UNREGISTER],
            has_toolkit_auth_cert=True,
            toolkit_auth_cert_hash="8005BAC40B5373B1A8484B72C059AC9DBA23A741",
            toolkit_auth_cert_actions=[PossibleAction.DISABLE, PossibleAction.UNREGISTER],
            has_registered_auth_cert=True
        )
    )

    @staticmethod
    def server_status_essentials_complete_token_logged_out():
        server_status = copy.deepcopy(StatusTestData.server_status_essentials_complete)
        server_status.token_status.logged_in = False
        return server_status


# Requires all server status in first list to be uninitialized and all in second list to be
# communication-capable on X-Road (certs present, auth cert registered)
def assert_server_statuses_transitioned(sl1: [ServerStatus], sl2: [ServerStatus]):
    assert len(sl1) == len(sl2)

    # Ignore the global status, roles, for same reasons as in server_statuses_equal()
    # Rely on booleans only, multi-server configs cannot have more
    for i in range(0, len(sl1)):
        assert sl1[i].security_server_name == sl2[i].security_server_name # Config match sanity check

        assert sl1[i].server_init_status.has_anchor is not True
        assert sl2[i].server_init_status.has_anchor is True

        assert sl1[i].server_init_status.has_server_code is not True
        assert sl2[i].server_init_status.has_server_code is True

        assert sl1[i].server_init_status.has_server_owner is not True
        assert sl2[i].server_init_status.has_server_owner is True

        assert TokenInitStatus.NOT_INITIALIZED == sl1[i].server_init_status.token_init_status
        assert TokenInitStatus.INITIALIZED == sl2[i].server_init_status.token_init_status

        assert sl1[i].token_status.logged_in is not True
        assert sl2[i].token_status.logged_in is True

        assert not sl1[i].timestamping_status
        assert len(sl2[i].timestamping_status) > 0

        assert sl1[i].status_keys.has_auth_key is not True
        assert sl2[i].status_keys.has_auth_key is True
        assert sl1[i].status_keys.has_toolkit_auth_key is not True
        assert sl2[i].status_keys.has_toolkit_auth_key is True

        # No assumptions about CSRS.

        assert sl1[i].status_certs.has_toolkit_sign_cert is not True
        assert sl2[i].status_certs.has_toolkit_sign_cert is True
        assert sl1[i].status_certs.has_sign_cert is not True
        assert sl2[i].status_certs.has_sign_cert is True

        assert sl1[i].status_certs.has_toolkit_auth_cert is not True
        assert sl2[i].status_certs.has_toolkit_auth_cert is True
        assert sl1[i].status_certs.has_auth_cert is not True
        assert sl2[i].status_certs.has_auth_cert is True

        assert sl1[i].status_certs.has_registered_auth_cert is not True
        assert sl2[i].status_certs.has_registered_auth_cert is True


# Waits until boolean function returns True within number of retried delays or raises error
def waitfor(boolf, delay, retries):
    count = 0
    while count < retries and not boolf():
        time.sleep(delay)
        count += 1

    if count >= retries:
        raise Exception("Exceeded retry count " + str(retries) + " with delay " + str(delay) + "s.")


# Returns TEST CA signed certificate in PEM format.
def perform_test_ca_sign(test_ca_sign_url, certfile_loc, _type):
    certfile = open(certfile_loc, "rb")  # opening for [r]eading as [b]inary
    cert_data = certfile.read()
    certfile.close()

    response = requests.post(
        test_ca_sign_url,
        {'type': _type},
        files={
            'certreq': (os.path.basename(certfile_loc), cert_data, 'application/x-x509-ca-cert')
        }
    )

    # Test CA returns plain PEMs only
    return response.content.decode("ascii")


# Performs GET to given API url, making use of given api-key for Authorization header, returns response as JSON dict.
def api_GET(api_url, api_path, api_key):
    full_url = api_url + "/" + api_path
    response = requests.get(
        full_url,
        headers={'Authorization': BaseController.authorization_header(api_key), 'accept': 'application/json'},
        verify=False)

    if response.status_code != 200:
        raise Exception("Failed /" + full_url + " retrieval, status " + str(response.status_code) + ": " + str(response.reason))

    return json.loads(str(response.content, 'utf-8').strip())


# Returns service description for given client
def get_service_description(config, client_id, ssn):
    api_key = os.getenv(config["security_server"][ssn]["api_key"], "")
    return api_GET(
            config["security_server"][ssn]["url"],
            "clients/" + client_id + "/service-descriptions",
            api_key
        )[0]

# Returns service clients for given service
def get_service_clients(config, service_id, ssn):
    api_key = os.getenv(config["security_server"][ssn]["api_key"], "")
    return api_GET(
            config["security_server"][ssn]["url"],
            "services/" + service_id + "/service-clients",
            api_key
        )

# Returns service clients for giving endpoints
def get_endpoint_service_clients(config, endpoint_id):
    api_key = os.getenv(config["security_server"][0]["api_key"], "")
    return api_GET(
            config["security_server"][0]["url"],
            "endpoints/" + endpoint_id + "/service-clients",
            api_key
        )

# Returns client
def get_client(config, ssn):
    conn_type = convert_swagger_enum(ConnectionType, config['security_server'][ssn]['clients'][0]['connection_type'])
    member_class = config['security_server'][ssn]['clients'][0]['member_class']
    member_code = config['security_server'][ssn]['clients'][0]['member_code']
    subsystem_code = config['security_server'][ssn]['clients'][0]['subsystem_code']
    api_key = os.getenv(config["security_server"][ssn]["api_key"], "")
    client = requests.get(
        config["security_server"][ssn]["url"] + "/clients",
        {'member_class': member_class,
         'member_code': member_code,
         'subsystem_code': subsystem_code,
         'connection_type': conn_type},
        headers={'Authorization': BaseController.authorization_header(api_key), 'accept': 'application/json'},
        verify=False)
    client_json = json.loads(str(client.content, 'utf-8').strip())
    return client_json[0] if len(client_json) > 0 else client_json


# Deduce possible TEST CA URL from configuration anchor
def find_test_ca_sign_url(conf_anchor_file_loc):
    prefix = "/testca"
    port = 8888
    suffix = "/sign"
    with open(conf_anchor_file_loc, 'r') as anchor_file:
        xml_fragment = list(filter(lambda s: s.count('downloadURL>') == 2, anchor_file.readlines())).pop()
        internal_conf_url = xml_fragment.replace("<downloadURL>", "").replace("</downloadURL>", "").strip()
        parsed_url = urlparse(internal_conf_url)
        host = parsed_url.netloc.split(':')[0]
        protocol = parsed_url.scheme
        return protocol + "://" + host + ":" + str(port) + prefix + suffix


# Check for auth cert registration update receival
def auth_cert_registration_global_configuration_update_received(config, ssn):
    def registered_auth_key(key):
        return default_auth_key_label(config["security_server"][ssn]) == key['label'] and \
               'REGISTERED' == key['certificates'][0]['status']

    api_key = os.getenv(config["security_server"][ssn]["api_key"], "")
    result = requests.get(
        config["security_server"][ssn]["url"] + "/tokens/" + str(config["security_server"][ssn]['software_token_id']),
        None,
        headers={
            'Authorization': BaseController.authorization_header(api_key),
            'accept': 'application/json'
        },
        verify=False
    )

    if result.status_code != 200:
        raise Exception("Failed registration status check, status " + str(result.status_code) + ": " + str(result.reason))

    response = json.loads(result.content)
    registered_auth_keys = list(filter(registered_auth_key, response['keys']))
    return bool(registered_auth_keys)
