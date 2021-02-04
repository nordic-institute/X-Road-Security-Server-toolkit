from datetime import datetime

from xrdsst.api import TokensApi, DiagnosticsApi, SystemApi, UserApi, InitializationApi, SecurityServersApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.core.util import default_auth_key_label, default_sign_key_label
from xrdsst.models import KeyUsageType, CertificateStatus
from xrdsst.rest.rest import ApiException


class StatusGlobal:
    class_: str = None
    code: str = None
    updated: datetime = None
    refresh: datetime = None

    def __init__(self, class_: str = None, code: str = None, updated: datetime = None, refresh: datetime = None):
        self.class_ = class_
        self.code = code
        self.updated = updated
        self.refresh = refresh

    def __repr__(self):
        return \
            f'StatusGlobal(class_="{self.class_}",' \
            f'code="{self.code}",' \
            f'updated="{self.updated}",' \
            f'refresh="{self.refresh}")'

    def to_status_str(self):
        return self.class_ + \
               ' (' + self.code.replace('ERROR_CODE_', '') + ')\n' + \
               'LAST ' + self.updated.strftime("%H%M%S %m%d") + "\n" + \
               'NEXT ' + self.refresh.strftime("%H%M%S %m%d")


class StatusVersion:
    version: str = None

    def __init__(self, version: str = None):
        self.version = version

    def __repr__(self):
        return \
            f'StatusVersion(version="{self.version}")'

    def to_status_str(self):
        return 'VER ' + self.version


class StatusRoles:
    permitted: bool = False
    roles: [str] = None

    def __init__(self, permitted: bool = False, roles: [str] = None):
        self.permitted = permitted
        self.roles = roles

    def __repr__(self):
        return \
            f'StatusRoles(permitted={self.permitted})' \
            f'StatusRoles(roles={self.roles})'

    def to_status_str(self):
        return '\n'.join(list(map(lambda s: s.replace("ROLE_XROAD_", "").replace("_", " ").lower().title(), self.roles))) if self.permitted else "NO ACCESS"


class StatusAnchor:
    has_anchor: bool = False
    hash_: str = None
    created_at: datetime = None

    def __init__(self, has_anchor: bool = False, hash_: str = None, created_at: datetime = None):
        self.has_anchor = has_anchor
        self.hash_ = hash
        self.created_at = created_at

    def __repr__(self):
        return \
            f'StatusAnchor(has_anchor={self.has_anchor},' \
            f'hash_="{self.hash_}",' \
            f'created_at={self.created_at})'


class StatusServerInitialization:
    id_: str = None
    has_anchor: bool = False
    has_server_code: bool = False
    server_code: str = None
    has_server_owner: bool = False
    server_owner: str = None
    token_init_status: str = None

    def __init__(self, id_: str = None, has_anchor: bool = False, has_server_code: bool = False, server_code: str = None,
                 has_server_owner: bool = False, server_owner: str = None, token_init_status: str = None):
        self.id_ = id_
        self.has_anchor = has_anchor
        self.has_server_code = has_server_code
        self.server_code = server_code
        self.has_server_owner = has_server_owner
        self.server_owner = server_owner
        self.token_init_status = token_init_status

    def __repr__(self):
        return \
            f'StatusServerInitialization(id_="{self.id_}",' \
            f'has_anchor={self.has_anchor},' \
            f'has_server_code={self.has_server_code},' \
            f'server_code="{self.server_code}",' \
            f'has_server_owner={self.has_server_owner},' \
            f'server_owner="{self.server_owner}",' \
            f'token_init_status={self.token_init_status})'

    def to_status_str(self):
        return \
            ('ANCHOR INITIALIZED\n' if self.has_anchor else ('' + '\n')) + \
            ('CODE INITIALIZED\n' if self.has_server_code else ('' + '\n')) + \
            ('OWNER INITIALIZED\n' if self.has_server_owner else '' + '\n') + \
            ('TOKEN' + ' ' + self.token_init_status) if self.token_init_status else '' + '\n'


class StatusServerTimestamping:
    name: str = None
    url: str = None

    def __init__(self, name: str = None, url: str = None):
        self.name = name
        self.url = url

    def __repr__(self):
        return \
            f'StatusServerTimestamping(name="{self.name}",' \
            f'url="{self.url}")'

    def __eq__(self, other):
        if isinstance(other, StatusServerTimestamping):
            return \
                self.name == other.name and \
                self.url == other.url

        return False


class StatusToken:
    id: str = None
    name: str = None
    status: str = None
    logged_in: bool = False

    def __init__(self, id_: str = None, name: str = None, status: str = None, logged_in: bool = False):
        self.id = id_
        self.name = name
        self.status = status
        self.logged_in = logged_in

    def __repr__(self):
        return \
            f'StatusToken(id={self.id},' \
            f'name="{self.name}",' \
            f'status="{self.status}",' \
            f'logged_in={self.logged_in})'

    def to_status_str(self):
        if not self.id:  # No token initialized, probably anchorless security server or some severe error.
            return ''

        return \
            '  ID ' + self.id + '\n' + \
            self.name + '\n' + \
            "STATUS " + self.status + '\n' + \
            "LOGIN " + ("YES" if self.logged_in else "NO")


class StatusKeys:
    key_count: int = 0
    sign_key_count: int = 0
    auth_key_count: int = 0
    has_toolkit_sign_key: bool = False
    toolkit_sign_key_id: str = None
    has_sign_key: bool = False

    has_toolkit_auth_key: bool = False
    toolkit_auth_key_id: str = None
    has_auth_key: bool = False

    def __init__(self, key_count: int = 0, sign_key_count: int = 0, auth_key_count: int = 0,
                 has_toolkit_sign_key: bool = False, toolkit_sign_key_id: str = None, has_sign_key: bool = False,
                 has_toolkit_auth_key: bool = False, toolkit_auth_key_id: str = None, has_auth_key: bool = False):
        self.key_count = key_count
        self.sign_key_count = sign_key_count
        self.auth_key_count = auth_key_count
        self.has_toolkit_sign_key = has_toolkit_sign_key
        self.toolkit_sign_key_id = toolkit_sign_key_id
        self.has_sign_key = has_sign_key
        self.has_toolkit_auth_key = has_toolkit_auth_key
        self.toolkit_auth_key_id = toolkit_auth_key_id
        self.has_auth_key = has_auth_key

    def __repr__(self):
        return \
            f'StatusKeys(key_count={self.key_count},' \
            f'sign_key_count={self.sign_key_count},' \
            f'auth_key_count={self.auth_key_count},' \
            f'has_toolkit_sign_key={self.has_toolkit_sign_key},' \
            f'toolkit_sign_key_id="{self.toolkit_sign_key_id}",' \
            f'has_sign_key={self.has_sign_key},' \
            f'has_toolkit_auth_key={self.has_toolkit_auth_key},' \
            f'toolkit_auth_key_id="{self.toolkit_auth_key_id}",' \
            f'has_auth_key={self.has_auth_key})'

    def to_status_str(self):
        return \
            (("SIGN" + ("*" if not self.has_toolkit_sign_key else '') + ' (' + str(self.sign_key_count) + ')') if self.has_sign_key else "") + '\n' + \
            (("AUTH" + ("*" if not self.has_toolkit_auth_key else '') + ' (' + str(self.auth_key_count) + ')') if self.has_auth_key else "") + '\n' + \
            str(self.key_count) + " KEYS" if self.key_count > 0 else ''  # Might not be == (sign_key_count + auth_key_count), esp. on hardware tokens.


class StatusCsrs:
    sign_csr_count: int = 0
    auth_csr_count: int = 0
    has_toolkit_sign_csr: bool = False
    has_sign_csr: bool = False
    has_toolkit_auth_csr: bool = False
    has_auth_csr: bool = False

    def __init__(self, sign_csr_count: int = 0, auth_csr_count: int = 0, has_toolkit_sign_csr: bool = False,
                 has_sign_csr: bool = False, has_toolkit_auth_csr: bool = False, has_auth_csr: bool = False):
        self.sign_csr_count = sign_csr_count
        self.auth_csr_count = auth_csr_count
        self.has_toolkit_sign_csr = has_toolkit_sign_csr
        self.has_sign_csr = has_sign_csr
        self.has_toolkit_auth_csr = has_toolkit_auth_csr
        self.has_auth_csr = has_auth_csr

    def __repr__(self):
        return \
            f'StatusCsrs(sign_csr_count={self.sign_csr_count},' \
            f'auth_csr_count={self.auth_csr_count},' \
            f'has_toolkit_sign_csr={self.has_toolkit_sign_csr},' \
            f'has_sign_csr={self.has_sign_csr},' \
            f'has_toolkit_auth_csr={self.has_toolkit_auth_csr},' \
            f'has_auth_csr={self.has_auth_csr})'

    def to_status_str(self):
        return \
            (("SIGN" + ("*" if not self.has_toolkit_sign_csr else '') + ' (' + str(self.sign_csr_count) + ')') if self.has_sign_csr else "") + '\n' + \
            (("AUTH" + ("*" if not self.has_toolkit_auth_csr else '') + ' (' + str(self.auth_csr_count) + ')') if self.has_auth_csr else "") + '\n' + \
            str(self.sign_csr_count + self.auth_csr_count) + " CSRS" if (self.sign_csr_count + self.auth_csr_count > 0) else ''


class StatusCerts:
    has_toolkit_sign_cert: bool = False
    toolkit_sign_cert_hash: str = None
    has_sign_cert: bool = False

    has_toolkit_auth_cert: bool = False
    toolkit_auth_cert_hash: str = None
    has_auth_cert: bool = False
    has_registered_auth_cert: bool = False

    def __init__(self, has_toolkit_sign_cert: bool = False, toolkit_sign_cert_hash: str = None,
                 has_sign_cert: bool = False, has_toolkit_auth_cert: bool = False, toolkit_auth_cert_hash: str = None,
                 has_auth_cert: bool = False, has_registered_auth_cert: bool = False):
        self.has_toolkit_sign_cert = has_toolkit_sign_cert
        self.toolkit_sign_cert_hash = toolkit_sign_cert_hash
        self.has_sign_cert = has_sign_cert
        self.has_toolkit_auth_cert = has_toolkit_auth_cert
        self.toolkit_auth_cert_hash = toolkit_auth_cert_hash
        self.has_auth_cert = has_auth_cert
        self.has_registered_auth_cert = has_registered_auth_cert

    def __repr__(self):
        return \
            f'StatusCerts(has_toolkit_sign_cert={self.has_toolkit_sign_cert},' \
            f'toolkit_sign_cert_hash="{self.toolkit_sign_cert_hash}",' \
            f'has_sign_cert={self.has_sign_cert},' \
            f'has_toolkit_auth_cert={self.has_toolkit_auth_cert},' \
            f'toolkit_auth_cert_hash="{self.toolkit_auth_cert_hash}",' \
            f'has_auth_cert={self.has_auth_cert},' \
            f'has_registered_auth_cert={self.has_registered_auth_cert})'

    def to_status_str(self):
        return \
            (("SIGN" + ("*" if not self.has_toolkit_sign_cert else '')) if self.has_sign_cert else "") + '\n' + \
            (("AUTH" + ("*" if not self.has_toolkit_sign_cert else '')) if self.has_sign_cert else "") + '\n'


def remote_get_token(ss_configuration, security_server):
    token_id = security_server['software_token_id']
    token_api = TokensApi(ApiClient(ss_configuration))
    token = token_api.get_token(token_id)
    return token


# Returns 'global status' of X-Road according to security servers knowledge
def status_global(ss_configuration):
    diagnostics_api = DiagnosticsApi(ApiClient(ss_configuration))
    glob_conf_diag = diagnostics_api.get_global_conf_diagnostics()

    glob_status = StatusGlobal(
        class_=glob_conf_diag.status_class,
        code=glob_conf_diag.status_code,
        updated=glob_conf_diag.prev_update_at,
        refresh=glob_conf_diag.next_update_at
    )
    return glob_status


# Returns security server version reported by server itself
def status_system_version(ss_configuration):
    system_api = SystemApi(ApiClient(ss_configuration))
    sys_ver = system_api.system_version()
    return StatusVersion(sys_ver.info)


# Returns roles of the user doing the API call in human readable form
def status_roles(ss_configuration):
    user_api = UserApi(ApiClient(ss_configuration))
    try:
        user = user_api.get_user()
    except ApiException as aex:
        if aex.status == 401 or aex.status == 403:
            return StatusRoles(permitted=False, roles=[])
    return StatusRoles(permitted=True, roles=user.roles)


# Returns security server anchor information, if available
def status_anchor(ss_configuration):
    initialization_api = InitializationApi(ApiClient(ss_configuration))
    system_api = SystemApi(ApiClient(ss_configuration))

    init_response = initialization_api.get_initialization_status()

    if not init_response.is_anchor_imported:
        return StatusAnchor(has_anchor=False)

    anchor = system_api.get_anchor()
    return StatusAnchor(
        has_anchor=True,
        hash_=anchor.hash,
        created_at=anchor.created_at
    )


# Returns security server basic initialization settings
def status_server_initialization(ss_configuration):
    initialization_api = InitializationApi(ApiClient(ss_configuration))
    security_servers_api = SecurityServersApi(ApiClient(ss_configuration))

    init_response = initialization_api.get_initialization_status()

    ssi = StatusServerInitialization(
        has_anchor=init_response.is_anchor_imported,
        has_server_code=init_response.is_server_code_initialized,
        has_server_owner=init_response.is_server_owner_initialized,
        token_init_status=init_response.software_token_init_status
        # Later conditional fill for: server_code, server_owner, token_init_status
    )

    if init_response.is_anchor_imported:
        ss_api_response = security_servers_api.get_security_servers(current_server=True)
        sec_server_details = ss_api_response.pop()

        ssi.server_code = sec_server_details.server_code if init_response.is_server_code_initialized else None
        ssi.server_owner = sec_server_details.member_code if init_response.is_server_owner_initialized else None
        ssi.id_ = sec_server_details.id if init_response.is_server_owner_initialized and init_response.is_server_code_initialized else None
        ssi.token_init_status = init_response.software_token_init_status

    return ssi


# Returns /configured/ (active) timestamping services for the security server
def status_timestamping(ss_configuration):
    system_api = SystemApi(ApiClient(ss_configuration))
    ts_list_response = system_api.get_configured_timestamping_services()
    return list(map(lambda tss: StatusServerTimestamping(
        name=tss.name,
        url=tss.url
    ), ts_list_response))


# Returns token status information for security server token specified in the configuration file.
def status_token(ss_configuration, security_server):
    token = remote_get_token(ss_configuration, security_server)
    return StatusToken(
        id_=token.id,
        name=token.name,
        status=token.status,
        logged_in=token.logged_in
    )


# Returns triple of (key, csr, cert) statuses for security server token specified in the configuration file.
def status_token_keys_and_certs(ss_configuration, security_server):
    # From among multiple certificates, returns first that is closest to being in REGISTERED
    def best_cert(certs):
        return next(
            (crt for crt in certs if CertificateStatus.REGISTERED == crt.status),
            next(
                (crt for crt in certs if CertificateStatus.REGISTRATION_IN_PROGRESS == crt.status),
                next(
                    (crt for crt in certs if CertificateStatus.SAVED == crt.status),
                    next(
                        (crt for crt in certs if CertificateStatus.DELETION_IN_PROGRESS != crt.status),
                        certs[0]
                    )
                )
            )
        )

    token = remote_get_token(ss_configuration, security_server)
    token_key_count = len(token.keys)

    toolkit_auth_key_label = default_auth_key_label(security_server)
    auth_keys = list(filter(lambda key: key.usage == KeyUsageType.AUTHENTICATION, token.keys))
    toolkit_auth_keys = list(filter(lambda key: key.label == toolkit_auth_key_label, auth_keys))
    has_toolkit_auth_key = toolkit_auth_keys and len(toolkit_auth_keys) == 1

    toolkit_sign_key_label = default_sign_key_label(security_server)
    sign_keys = list(filter(lambda key: key.usage == KeyUsageType.SIGNING, token.keys))
    toolkit_sign_keys = list(filter(lambda key: key.label == toolkit_sign_key_label, sign_keys))
    has_toolkit_sign_key = len(toolkit_sign_keys) == 1

    # KEYS

    status_keys = StatusKeys(
        key_count=token_key_count,
        sign_key_count=len(sign_keys),
        auth_key_count=len(auth_keys),
        has_toolkit_sign_key=has_toolkit_sign_key,
        toolkit_sign_key_id=toolkit_sign_keys[0].id if has_toolkit_sign_key else None,
        has_sign_key=len(sign_keys) > 0,

        has_toolkit_auth_key=has_toolkit_auth_key,
        toolkit_auth_key_id=toolkit_auth_keys[0].id if has_toolkit_auth_key else None,
        has_auth_key=len(auth_keys) > 0
    )

    # CSRS

    auth_keys_with_csrs = list(filter(lambda key: len(key.certificate_signing_requests) > 0, auth_keys))
    toolkit_auth_keys_with_csrs = list(filter(lambda key: len(key.certificate_signing_requests) > 0, toolkit_auth_keys))
    sign_keys_with_csrs = list(filter(lambda key: len(key.certificate_signing_requests) > 0, sign_keys))
    toolkit_sign_keys_with_csrs = list(filter(lambda key: len(key.certificate_signing_requests) > 0, toolkit_sign_keys))

    status_csrs = StatusCsrs(
        sign_csr_count=len(sum(map(lambda key: key.certificate_signing_requests, sign_keys_with_csrs), [])),
        auth_csr_count=len(sum(map(lambda key: key.certificate_signing_requests, auth_keys_with_csrs), [])),
        has_toolkit_sign_csr=len(toolkit_sign_keys_with_csrs) > 0,
        has_sign_csr=len(sign_keys_with_csrs) > 0,
        has_toolkit_auth_csr=len(toolkit_auth_keys_with_csrs) > 0,
        has_auth_csr=len(auth_keys_with_csrs) > 0
    )

    # Tried so hard, came so far, CERTIFICATES!

    certs_of_auth_keys = sum(map(lambda key: key.certificates, auth_keys), [])
    certs_of_sign_keys = sum(map(lambda key: key.certificates, sign_keys), [])

    registered_auth_key_certs = list(
        filter(lambda cert: CertificateStatus.REGISTERED == cert.status, certs_of_auth_keys))

    has_toolkit_sign_cert: bool = (has_toolkit_sign_key and len(toolkit_sign_keys[0].certificates) > 0)
    toolkit_sign_cert = best_cert(toolkit_sign_keys[0].certificates) if has_toolkit_sign_cert else None

    has_toolkit_auth_cert: bool = (has_toolkit_auth_key and len(toolkit_auth_keys[0].certificates) > 0)
    toolkit_auth_cert = best_cert(toolkit_auth_keys[0].certificates) if has_toolkit_auth_cert else None

    status_certs = StatusCerts(
        has_sign_cert=len(certs_of_sign_keys) > 0,
        has_toolkit_sign_cert=has_toolkit_sign_cert,
        toolkit_sign_cert_hash=toolkit_sign_cert.certificate_details.hash if toolkit_sign_cert else None,

        has_auth_cert=len(certs_of_auth_keys) > 0,
        has_toolkit_auth_cert=has_toolkit_auth_cert,
        toolkit_auth_cert_hash=toolkit_auth_cert.certificate_details.hash if toolkit_auth_cert else None,
        has_registered_auth_cert=len(registered_auth_key_certs) > 0
    )

    return status_keys, status_csrs, status_certs
