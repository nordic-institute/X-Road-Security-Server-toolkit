import urllib3
from cement import ex

from xrdsst.api.security_servers_api import SecurityServersApi
from xrdsst.api.certificate_authorities_api import CertificateAuthoritiesApi
from xrdsst.controllers.base import BaseController
from xrdsst.models import CsrGenerate, KeyUsageType, CsrFormat, KeyLabelWithCsrGenerate
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.models.token_password import TokenPassword
from xrdsst.resources.texts import texts


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
            'id' : token.id,
            'name' : token.name,
            'status': token.status,
            'logged_in' : token.logged_in
        }


class TokenController(BaseController):
    class Meta:
        label = 'token'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['token.controller.description']

    @ex(help='List tokens', arguments=[])
    def list(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.token_list(self.load_config())

    @ex(help='Login token', arguments=[])
    def login(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.token_login(self.load_config())

    @ex(help="Initializes two token keys with corresponding AUTH and SIGN CSR generated")
    def init_keys(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.token_add_keys_with_csrs(self.load_config())

    def token_list(self, config):
        self.init_logging(config)
        for security_server in config["security-server"]:
            configuration = self.initialize_basic_config_values(security_server, config)
            self.remote_token_list(configuration)

    # Since this is read-only operation, do not log anything, only console output
    def remote_token_list(self, configuration):
        try:
            token_api = TokensApi(ApiClient(configuration))
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

    def token_login(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security-server"]:
            BaseController.log_info('Starting configuration process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            self.remote_token_login(ss_configuration, security_server)

    @staticmethod
    def remote_token_login(ss_configuration, security_server):
        token_id = security_server['software_token_id']
        token_pin = security_server['software_token_pin']
        try:
            BaseController.log_info('Performing software token ' + str(token_id) + ' login: ')
            token_api = TokensApi(ApiClient(ss_configuration))
            token_api.login_token(
                id=token_id,
                body=TokenPassword(token_pin)
            )
            BaseController.log_info('Security server \"' + security_server["name"] + '\" token ' + str(token_id) + ' logged in')
        except ApiException as err:
            if err.status == 409:
                print("Token already logged in.")
            else:
                BaseController.log_api_error('TokensApi->login_token', err)

    def token_add_keys_with_csrs(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security-server"]:
            BaseController.log_info('Starting configuration process for security server: '+ security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            self.remote_token_add_keys_with_csrs(ss_configuration, security_server)

    # requires token to be logged in
    @staticmethod
    def remote_token_add_keys_with_csrs(ss_configuration, security_server):
        def log_creations(results):
            for result in results:
                BaseController.log_info(
                    "Created " + str(result.key.usage) + " CSR '" + result.csr_id +
                    "' for key '" + result.key.id + "' as '" + result.key.label + "'"
                )

        responses = []

        token_id = security_server['software_token_id']
        ss_code = security_server['security_server_code']
        member_class = security_server['owner_member_class']
        dn_country = security_server['owner_dn_country']
        dn_common_name = security_server['owner_member_code']
        dn_org = security_server['owner_dn_org']

        auth_key_label = security_server['name'] + '-default-auth-key'
        sign_key_label = security_server['name'] + '-default-sign-key'

        try:
            ssi = remote_get_security_server_instance(ss_configuration)
            token = remote_get_token(ss_configuration, security_server)
            auth_ca = remote_get_auth_certificate_authority(ss_configuration)
            sign_ca = remote_get_sign_certificate_authority(ss_configuration)

            token_key_labels = list(map(lambda key: key.label, token.keys))
            has_auth_key = auth_key_label in token_key_labels
            has_sign_key = sign_key_label in token_key_labels

            # It is not entirely clear how we should approach the formulation of DN, we use sample conventions here,
            # but it is entirely possible that better conventions or even more configuration should be done. TODO??
            distinguished_name = {
                'C': dn_country,
                'O': dn_org,
                'CN': dn_common_name,
                'serialNumber': '/'.join([ssi.member_class, ss_code, member_class])
            }

            auth_key_req_param = KeyLabelWithCsrGenerate(
                key_label=auth_key_label,
                csr_generate_request=CsrGenerate(
                    key_usage_type=KeyUsageType.AUTHENTICATION,
                    ca_name=auth_ca.name,
                    csr_format=CsrFormat.DER,  # Test CA setup at least only works with DER
                    member_id=':'.join([ssi.instance_id, ssi.member_class, ssi.member_code]),
                    subject_field_values=distinguished_name
                )
            )

            sign_key_req_param = KeyLabelWithCsrGenerate(
                key_label=sign_key_label,
                csr_generate_request=CsrGenerate(
                    key_usage_type=KeyUsageType.SIGNING,
                    ca_name=sign_ca.name,
                    csr_format=CsrFormat.DER,  # Test CA setup at least only works with DER
                    member_id=':'.join([ssi.instance_id, ssi.member_class, ssi.member_code]),
                    subject_field_values=distinguished_name
                )
            )

            if has_sign_key and has_auth_key:
                BaseController.log_info("No key initialization needed.")
                return

            token_api = TokensApi(ApiClient(ss_configuration))
            if not has_auth_key:
                try:
                    BaseController.log_info('Generating software token ' + str(token_id) + ' key labelled ' + auth_key_label + ' and AUTH CSR: ')
                    response = token_api.add_key_and_csr(token_id, body=auth_key_req_param)
                    responses.append(response)
                except ApiException as err:
                    BaseController.log_api_error('TokensApi->add_key_and_csr', err)
                    log_creations(responses)

            if not has_sign_key:
                try:
                    BaseController.log_info('Generating software token ' + str(token_id) + " key labelled '" + sign_key_label + "' and SIGN CSR: ")
                    response = token_api.add_key_and_csr(token_id, body=sign_key_req_param)
                    responses.append(response)
                except ApiException as err:
                    BaseController.log_api_error('TokensApi->add_key_and_csr', err)
                    log_creations(responses)
        except Exception as exc:
            log_creations(responses)
            raise exc

        log_creations(responses)


def remote_get_token(ss_configuration, security_server):
    token_id = security_server['software_token_id']
    token_api = TokensApi(ApiClient(ss_configuration))
    token = token_api.get_token(token_id)
    return token


def remote_get_security_server_instance(ss_configuration):
    ss_api = SecurityServersApi(ApiClient(ss_configuration))
    ss_api_response = ss_api.get_security_servers(current_server=True)
    return ss_api_response.pop()


def remote_get_auth_certificate_authority(ss_configuration):
    ca_api = CertificateAuthoritiesApi(ApiClient(ss_configuration))
    ca_api_response = ca_api.get_approved_certificate_authorities(key_usage_type=KeyUsageType.AUTHENTICATION)
    return ca_api_response.pop()


def remote_get_sign_certificate_authority(ss_configuration):
    ca_api = CertificateAuthoritiesApi(ApiClient(ss_configuration))
    ca_api_response = ca_api.get_approved_certificate_authorities(key_usage_type=KeyUsageType.SIGNING)
    return ca_api_response.pop()
