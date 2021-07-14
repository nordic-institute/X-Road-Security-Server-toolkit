# Return list of configuration keys that are NOT among known ConfKeys*, in hierarchical representation
def validate_conf_keys(xrdsst_conf):
    # Return only configuration keys from ConfKey list class (CONF_KEY_)
    def _keys_only(conf_key_X):
        return {getattr(conf_key_X, x) for x in vars(conf_key_X) if x.startswith('CONF_KEY')}

    # Return only used keys that are NOT among known ConfKeys
    def _invalid(used_keys, conf_key_X):
        return used_keys.difference(_keys_only(conf_key_X))

    def _validate_conf_keys(xrdsst_conf_fragment, conf_key_X):
        result = []
        if isinstance(xrdsst_conf_fragment, dict):
            fragment_keys = set(xrdsst_conf_fragment.keys())
            invalid_fragment_keys = _invalid(fragment_keys, conf_key_X)
            result.extend(map(lambda key: ('.' + key, key, _keys_only(conf_key_X)), invalid_fragment_keys))

            for desc_key in {x for x in conf_key_X.descendant_conf_keys() if xrdsst_conf_fragment.get(x[0])}:
                result.extend(map(
                    lambda key: ('.' + desc_key[0] + str(key[0]), key[1], key[2]),
                    _validate_conf_keys(xrdsst_conf_fragment[desc_key[0]], desc_key[1])
                ))
        elif isinstance(xrdsst_conf_fragment, list):
            for i in range(0, len(xrdsst_conf_fragment)):
                result.extend(map(
                    lambda key: ('[' + str(i + 1) + ']' + str(key[0]), key[1], key[2]),
                    _validate_conf_keys(xrdsst_conf_fragment[i], conf_key_X)
                ))

        return result

    return _validate_conf_keys(xrdsst_conf, ConfKeysRoot)


# Known keys for xrdsst configuration file root.
class ConfKeysRoot:
    CONF_KEY_ROOT_SERVER = 'security_server'
    CONF_KEY_ROOT_ADMIN_CREDENTIALS = 'admin_credentials'
    CONF_KEY_ROOT_SSH_ACCESS = 'ssh_access'
    CONF_KEY_ROOT_LOGGING = 'logging'

    # Return the tuples ('child key', child conf keys class) for keys with descendants of their own
    @staticmethod
    def descendant_conf_keys():
        return [
            (ConfKeysRoot.CONF_KEY_ROOT_SERVER, ConfKeysSecurityServer),
            (ConfKeysRoot.CONF_KEY_ROOT_SSH_ACCESS, ConfKeysSSHAccess),
            (ConfKeysRoot.CONF_KEY_ROOT_LOGGING, ConfKeysLogging)
        ]


# Known keys for xrdsst configuration file logging section.
class ConfKeysLogging:
    CONF_KEY_LOGGING_FILE = 'file'
    CONF_KEY_LOGGING_LEVEL = 'level'

    @staticmethod
    def descendant_conf_keys():
        return []

class ConfKeysSSHAccess:
    CONF_KEY_USER = 'user'
    CONF_KEY_PRIVATE_KEY = 'private_key'

    @staticmethod
    def descendant_conf_keys():
        return []

# Known keys for xrdsst configuration file security server configuration section.
class ConfKeysSecurityServer:
    CONF_KEY_ANCHOR = 'configuration_anchor'
    CONF_KEY_API_KEY = 'api_key'
    CONF_KEY_API_KEY_URL = 'api_key_url'
    CONF_KEY_ADMIN_CREDENTIALS = 'admin_credentials'
    CONF_KEY_CERTS = 'certificates'
    CONF_KEY_CLIENTS = 'clients'
    CONF_KEY_DN_C = 'owner_dn_country'
    CONF_KEY_DN_ORG = 'owner_dn_org'
    CONF_KEY_NAME = 'name'
    CONF_KEY_MEMBER_CLASS = 'owner_member_class'
    CONF_KEY_MEMBER_CODE = 'owner_member_code'
    CONF_KEY_SERVER_CODE = 'security_server_code'
    CONF_KEY_SOFT_TOKEN_ID = 'software_token_id'
    CONF_KEY_SOFT_TOKEN_PIN = 'software_token_pin'
    CONF_KEY_URL = 'url'
    CONF_KEY_FQDN = 'fqdn'
    CONF_KEY_SSH_USER = 'ssh_user'
    CONF_KEY_SSH_PRIVATE_KEY = 'ssh_private_key'
    CONF_KEY_TLS_CERTS = 'tls_certificates'

    @staticmethod
    def descendant_conf_keys():
        return [
            (ConfKeysSecurityServer.CONF_KEY_CLIENTS, ConfKeysSecServerClients)
        ]


# Known keys for xrdsst configuration file security server client configuration section.
class ConfKeysSecServerClients:
    CONF_KEY_SS_CLIENT_MEMBER_CLASS = 'member_class'
    CONF_KEY_SS_CLIENT_MEMBER_CODE = 'member_code'
    CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE = 'subsystem_code'
    CONF_KEY_SS_CLIENT_CONNECTION_TYPE = 'connection_type'
    CONF_KEY_SS_CLIENT_SERVICE_DESCS = 'service_descriptions'
    CONF_KEY_SS_CLIENT_MEMBER_NAME = 'member_name'
    CONF_KEY_SS_CLIENT_TLS_CERTIFICATES = 'tls_certificates'
    CONF_KEY_LOCAL_GROUPS = 'local_groups'

    @staticmethod
    def descendant_conf_keys():
        return [
            (ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SERVICE_DESCS, ConfKeysSecServerClientServiceDesc)
        ]


# Known keys for xrdsst configuration file security server client service descriptions configuration section.
class ConfKeysSecServerClientServiceDesc:
    CONF_KEY_SS_CLIENT_SERVICE_DESC_URL = 'url'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_REST_SERVICE_CODE = 'rest_service_code'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_TYPE = 'type'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS = 'access'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_URL_ALL = 'url_all'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_TIMEOUT_ALL = 'timeout_all'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SSL_AUTH_ALL = 'ssl_auth_all'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES = 'services'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS = 'endpoints'

    @staticmethod
    def descendant_conf_keys():
        return [
            (ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES, ConfKeysSecServerClientServiceDescService),
            (ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINTS, ConfKeysSecServerClientServiceDescEndpoints)
        ]


# Known keys for xrdsst configuration file security server client service descriptions services configuration section.
class ConfKeysSecServerClientServiceDescService:
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICE_SERVICE_CODE = 'service_code'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICE_CLIENT_ACCESS = 'access'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICE_TIMEOUT = 'timeout'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICE_SSL_AUTH = 'ssl_auth'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICE_URL = 'url'

    @staticmethod
    def descendant_conf_keys():
        return []


class ConfKeysSecServerClientServiceDescEndpoints:
    CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_METHOD = 'method'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_PATH = 'path'
    CONF_KEY_SS_CLIENT_SERVICE_DESC_ENDPOINT_ACCESS = 'access'
    @staticmethod
    def descendant_conf_keys():
        return []

class ConfKeysSecServerClientLocalGroups:
    CONF_KEY_SS_CLIENT_LOCAL_GROUP_CODE = 'code'
    CONF_KEY_SS_CLIENT_LOCAL_GROUP_DESCRIPTION = 'description'
    CONF_KEY_SS_CLIENT_LOCAL_GROUP_MEMBERS = 'members'
    @staticmethod
    def descendant_conf_keys():
        return []