# Returns toolkit default AUTHENTICATION key label, given security server configuration
def default_auth_key_label(security_server):
    return security_server['name'] + '-default-auth-key'


# Returns toolkit default SIGNING key label, given security server configuration
def default_sign_key_label(security_server):
    return security_server['name'] + '-default-sign-key'