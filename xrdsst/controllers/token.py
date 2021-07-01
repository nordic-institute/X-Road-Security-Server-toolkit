import copy

from cement import ex

from xrdsst.api.security_servers_api import SecurityServersApi
from xrdsst.api.certificate_authorities_api import CertificateAuthoritiesApi
from xrdsst.core.api_util import remote_get_token
from xrdsst.controllers.base import BaseController
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.core.util import default_auth_key_label, default_sign_key_label, default_member_sign_key_label
from xrdsst.models import CsrGenerate, KeyUsageType, CsrFormat, KeyLabelWithCsrGenerate
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.models.token_password import TokenPassword
from xrdsst.resources.texts import texts
from enum import Enum
from datetime import datetime


class TokenLabels(object):
    @staticmethod
    def generate_key(token_id, sign_key_label, type):
        return 'Generating software token %s key labelled " %s " and %s CSR: ' % (token_id, sign_key_label, type)

    @staticmethod
    def error():
        return 'TokensApi->add_key_and_csr'


class TokenListMapper:
    @staticmethod
    def headers():
        return ['ID', 'NAME', 'STATUS', 'LOGIN STATUS']

    @staticmethod
    def as_list(token):
        return [token.id, token.name, token.status, token.logged_in]

    @staticmethod
    def as_object(token):
        return {
            'id': token.id,
            'name': token.name,
            'status': token.status,
            'logged_in': token.logged_in
        }


class KeyTypes(Enum):
    AUTH = 1
    SIGN = 2
    ALL = 3


class TokenController(BaseController):
    class Meta:
        label = 'token'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['token.controller.description']

    @ex(help='List tokens', arguments=[])
    def list(self):
        active_config = self.load_config()
        self.token_list(active_config)

    @ex(help='Login token', arguments=[])
    def login(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.token_login(active_config)

    @ex(help="Initializes two token keys with corresponding AUTH and SIGN CSR generated")
    def init_keys(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.token_add_keys_with_csrs(active_config)

    @ex(help="Initializes new keys for renew the certificates")
    def create_new_keys(self):
        active_config = self.load_config()

        self.token_add_keys_with_csrs(active_config, True)

    def token_list(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_token_list(ss_api_config)
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_token_list(self, ss_api_config):
        try:
            token_api = TokensApi(ApiClient(ss_api_config))
            token_list_response = token_api.get_tokens()
            render_data = []
            if self.is_output_tabulated():
                render_data = [TokenListMapper.headers()]
                render_data.extend(map(TokenListMapper.as_list, token_list_response))
            else:
                render_data.extend(map(TokenListMapper.as_object, token_list_response))

            self.render(render_data)
        except ApiException as err:
            print("Exception when calling TokensApi->get_tokens: %s\n" % err)

    @staticmethod
    def remote_get_tokens(ss_api_config):
        try:
            token_api = TokensApi(ApiClient(ss_api_config))
            token_list_response = token_api.get_tokens()
            return token_list_response
        except ApiException as err:
            print("Exception when calling TokensApi->get_tokens: %s\n" % err)

    def token_login(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting token login process for security server: ' + security_server['name'])
            self.remote_token_login(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    @staticmethod
    def remote_token_login(ss_api_config, security_server):
        token_id = security_server['software_token_id']
        token_pin = security_server['software_token_pin']
        try:
            BaseController.log_info('Performing software token ' + str(token_id) + ' login: ')
            token_api = TokensApi(ApiClient(ss_api_config))
            token_api.login_token(
                id=token_id,
                body=TokenPassword(token_pin)
            )
            BaseController.log_info("Security server '" + security_server['name'] + "' token " + str(token_id) + " logged in.")
        except ApiException as err:
            if err.status == 409:
                BaseController.log_info("Token " + str(token_id) + " already logged in for '" + security_server['name'] + "'.")
            else:
                BaseController.log_api_error('TokensApi->login_token', err)

    def token_add_keys_with_csrs(self, config, is_new_key=False):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting token key creation process for security server: ' + security_server['name'])

            auth_key_label = default_auth_key_label(security_server)
            sign_key_label = default_sign_key_label(security_server)

            if is_new_key:
                date = datetime.today().strftime('%Y_%m_%d')
                auth_key_label = "%s_%s" % (auth_key_label, date)
                sign_key_label = "%s_%s" % (sign_key_label, date)

            member_class = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS]
            member_code = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE]
            member_name = security_server[ConfKeysSecurityServer.CONF_KEY_DN_ORG]

            self.remote_token_add_all_keys_with_csrs(ss_api_config, security_server, member_class, member_code, member_name, auth_key_label, sign_key_label)
            self.remote_token_add_sign_keys_with_csrs(ss_api_config, security_server, is_new_key, auth_key_label, sign_key_label)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    # requires token to be logged in
    @staticmethod
    def remote_token_add_all_keys_with_csrs(ss_api_config, security_server, member_class, member_code, member_name, auth_key_label=None, sign_key_label=None):
        def log_creations(results):
            for result in results:
                BaseController.log_info(
                    "Created " + str(result.key.usage) + " CSR '" + result.csr_id +
                    "' for key '" + result.key.id + "' as '" + result.key.label + "'"
                )

        responses = []

        ssi = remote_get_security_server_instance(ss_api_config)
        token = remote_get_token(ss_api_config, security_server)
        auth_ca = remote_get_auth_certificate_authority(ss_api_config)
        sign_ca = remote_get_sign_certificate_authority(ss_api_config)

        token_id = security_server[ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID]
        ss_code = security_server[ConfKeysSecurityServer.CONF_KEY_SERVER_CODE]
        dn_country = security_server[ConfKeysSecurityServer.CONF_KEY_DN_C]
        dn_common_name = member_code
        dn_org = member_name
        fqdn = security_server[ConfKeysSecurityServer.CONF_KEY_FQDN]

        try:
            token_key_labels = list(map(lambda key: key.label, token.keys))
            has_auth_key = auth_key_label in token_key_labels
            has_sign_key = sign_key_label in token_key_labels

            sign_cert_subject = {
                'C': dn_country,
                'O': dn_org,
                'CN': dn_common_name,
                'serialNumber': '/'.join([ssi.member_class, ss_code, member_class])
            }

            auth_cert_subject = copy.deepcopy(sign_cert_subject)
            auth_cert_subject['CN'] = fqdn

            if has_sign_key and has_auth_key:
                BaseController.log_info("No key initialization needed.")
                return

            token_api = TokensApi(ApiClient(ss_api_config))
            auth_key_req_param = KeyLabelWithCsrGenerate(
                key_label=auth_key_label,
                csr_generate_request=CsrGenerate(
                    key_usage_type=KeyUsageType.AUTHENTICATION,
                    ca_name=auth_ca.name,
                    csr_format=CsrFormat.DER,  # Test CA setup at least only works with DER
                    member_id=':'.join([ssi.instance_id, ssi.member_class, ssi.member_code]),
                    subject_field_values=auth_cert_subject
                )
            )

            if not has_auth_key:
                try:
                    BaseController.log_info(TokenLabels.generate_key(token_id, sign_key_label, 'AUTH'))
                    response = token_api.add_key_and_csr(token_id, body=auth_key_req_param)
                    responses.append(response)
                except ApiException as err:
                    BaseController.log_api_error(TokenLabels.error(), err)
                    log_creations(responses)

            sign_key_req_param = KeyLabelWithCsrGenerate(
                key_label=sign_key_label,
                csr_generate_request=CsrGenerate(
                    key_usage_type=KeyUsageType.SIGNING,
                    ca_name=sign_ca.name,
                    csr_format=CsrFormat.DER,  # Test CA setup at least only works with DER
                    member_id=':'.join([ssi.instance_id, ssi.member_class, ssi.member_code]),
                    subject_field_values=sign_cert_subject
                )
            )
            if not has_sign_key:
                try:
                    BaseController.log_info(TokenLabels.generate_key(token_id, sign_key_label, 'SIGN'))
                    response = token_api.add_key_and_csr(token_id, body=sign_key_req_param)
                    responses.append(response)
                except ApiException as err:
                    BaseController.log_api_error(TokenLabels.error(), err)
                    log_creations(responses)
        except Exception as exc:
            log_creations(responses)
            raise exc

        log_creations(responses)

    # requires token to be logged in
    @staticmethod
    def remote_token_add_sign_keys_with_csrs(ss_api_config, security_server, is_new_key, auth_key_label=None, sign_key_label=None):
        def log_creations(results):
            for result in results:
                BaseController.log_info(
                    "Created " + str(result.key.usage) + " CSR '" + result.csr_id +
                    "' for key '" + result.key.id + "' as '" + result.key.label + "'"
                )

        if "clients" not in security_server:
            return

        for client in security_server["clients"]:
            if client["member_class"] != security_server["owner_member_class"] or client["member_code"] != security_server["owner_member_code"]:
                member_class = client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CLASS]
                member_code = client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CODE]
                member_name = client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_NAME]
                sign_key_label = default_member_sign_key_label(security_server, client)
                if is_new_key:
                    date = datetime.today().strftime('%Y_%m_%d')
                    sign_key_label = "%s_%s" % (sign_key_label, date)

        responses = []

        ssi = remote_get_security_server_instance(ss_api_config)
        token = remote_get_token(ss_api_config, security_server)
        sign_ca = remote_get_sign_certificate_authority(ss_api_config)
        token_id = security_server[ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID]
        ss_code = security_server[ConfKeysSecurityServer.CONF_KEY_SERVER_CODE]
        dn_country = security_server[ConfKeysSecurityServer.CONF_KEY_DN_C]
        dn_common_name = member_code
        dn_org = member_name
        fqdn = security_server[ConfKeysSecurityServer.CONF_KEY_FQDN]

        try:
            token_key_labels = list(map(lambda key: key.label, token.keys))
            has_auth_key = auth_key_label in token_key_labels
            has_sign_key = sign_key_label in token_key_labels

            sign_cert_subject = {
                'C': dn_country,
                'O': dn_org,
                'CN': dn_common_name,
                'serialNumber': '/'.join([ssi.member_class, ss_code, member_class])
            }

            auth_cert_subject = copy.deepcopy(sign_cert_subject)
            auth_cert_subject['CN'] = fqdn

            if has_sign_key and has_auth_key:
                BaseController.log_info("No key initialization needed.")
                return

            token_api = TokensApi(ApiClient(ss_api_config))
            sign_key_req_param = KeyLabelWithCsrGenerate(
                key_label=sign_key_label,
                csr_generate_request=CsrGenerate(
                    key_usage_type=KeyUsageType.SIGNING,
                    ca_name=sign_ca.name,
                    csr_format=CsrFormat.DER,  # Test CA setup at least only works with DER
                    member_id=':'.join([ssi.instance_id, ssi.member_class, ssi.member_code]),
                    subject_field_values=sign_cert_subject
                )
            )
            if not has_sign_key:
                try:
                    BaseController.log_info(TokenLabels.generate_key(token_id, sign_key_label, 'SIGN'))
                    response = token_api.add_key_and_csr(token_id, body=sign_key_req_param)
                    responses.append(response)
                except ApiException as err:
                    BaseController.log_api_error(TokenLabels.error(), err)
                    log_creations(responses)
        except Exception as exc:
            log_creations(responses)
            raise exc

        log_creations(responses)


def remote_get_security_server_instance(ss_api_config):
    ss_api = SecurityServersApi(ApiClient(ss_api_config))
    ss_api_response = ss_api.get_security_servers(current_server=True)
    return ss_api_response.pop()


def remote_get_auth_certificate_authority(ss_api_config):
    ca_api = CertificateAuthoritiesApi(ApiClient(ss_api_config))
    ca_api_response = ca_api.get_approved_certificate_authorities(key_usage_type=KeyUsageType.AUTHENTICATION)
    return ca_api_response.pop()


def remote_get_sign_certificate_authority(ss_api_config):
    ca_api = CertificateAuthoritiesApi(ApiClient(ss_api_config))
    ca_api_response = ca_api.get_approved_certificate_authorities(key_usage_type=KeyUsageType.SIGNING)
    return ca_api_response.pop()
