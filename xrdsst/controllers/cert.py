import urllib3
from cement import ex

from xrdsst.api.token_certificates_api import TokenCertificatesApi
from xrdsst.controllers.base import BaseController
from xrdsst.models import SecurityServerAddress
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.resources.texts import texts


from xrdsst.rest.rest import ApiException


class CertController(BaseController):
    class Meta:
        label = 'cert'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['cert.controller.description']

    @ex(help="Import certificate(s)", label="import", arguments=[])
    def import_(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.import_certificates(self.load_config())

    @ex(help="Register authentication certificate(s)", arguments=[])
    def register(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.register_certificate(self.load_config())

    @ex(help="Activate registered centrally approved authentication certificate", arguments=[])
    def activate(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.activate_certificate(self.load_config())

    def import_certificates(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting configuration process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            self.remote_import_certificates(ss_configuration, security_server)

    def register_certificate(self,  configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting configuration process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            self.remote_register_certificate(ss_configuration, security_server)

    def activate_certificate(self,  configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting configuration process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            self.remote_activate_certificate(ss_configuration, security_server)


    # requires token to be logged in
    @staticmethod
    def remote_import_certificates(ss_configuration, security_server):
        import cement.utils.fs
        token_cert_api = TokenCertificatesApi(ApiClient(ss_configuration))
        for cert in security_server["certificates"]:
            location = cement.utils.fs.join_exists(cert)
            if not location[1]:
                BaseController.log_info("Certificate '" + location[0] + "' does not exist")
            else:
                certfile = location[0]
                try:
                    cert_file = open(location[0], "rb")
                    cert_data = cert_file.read()
                    cert_file.close()
                    token_cert_api.import_certificate(body=cert_data)
                except ApiException as err:
                    if err.status == 409 and err.body.count("certificate_already_exists"):
                        print("Certificate '" + certfile + "' already imported.")
                    else:
                        BaseController.log_api_error('TokenCertificatesApi->import_certificate', err)

    @staticmethod
    def remote_register_certificate(ss_configuration, security_server):
        registrable_cert = CertController.find_actionable_auth_certificate(ss_configuration, security_server, 'REGISTER')
        if not registrable_cert:
            return

        token_cert_api = TokenCertificatesApi(ApiClient(ss_configuration))
        ss_address = SecurityServerAddress(BaseController.security_server_address(security_server))
        token_cert_api.register_certificate(registrable_cert.certificate_details.hash, body=ss_address)
        BaseController.log_info("Registered certificate " + registrable_cert.certificate_details.hash + " for address '" + str(ss_address) + "'")

    @staticmethod
    def remote_activate_certificate(ss_configuration, security_server):
        activatable_cert = CertController.find_actionable_auth_certificate(ss_configuration, security_server, 'ACTIVATE')
        if not activatable_cert:
            return

        token_cert_api = TokenCertificatesApi(ApiClient(ss_configuration))
        token_cert_api.activate_certificate(activatable_cert.certificate_details.hash) # responseless PUT
        cert_actions = token_cert_api.get_possible_actions_for_certificate(activatable_cert.certificate_details.hash)
        if 'ACTIVATE' not in cert_actions:
            BaseController.log_info("Activated certificate " + activatable_cert.certificate_details.hash)
        else:
            BaseController.log_info("Could not activate certificate " + activatable_cert.certificate_details.hash)

    @staticmethod
    def find_actionable_auth_certificate(ss_configuration, security_server, cert_action):
        token = remote_get_token(ss_configuration, security_server)
        # Find the authentication certificate by conventional name
        auth_key_label = BaseController.default_auth_key_label(security_server)
        auth_keys = list(filter(lambda key: key.label == auth_key_label, token.keys))
        found_auth_key_count = len(auth_keys)
        if found_auth_key_count == 0:
            BaseController.log_info("Did not found authentication key labelled '" + auth_key_label + "'.")
            return None
        elif found_auth_key_count > 1:
            BaseController.log_info("Found multiple authentication keys labelled '" + auth_key_label + "', skipping registration.")
            return None

        # So far so good, are there actual certificates attached to key?
        auth_key = auth_keys[0]
        if not auth_key.certificates:
            BaseController.log_info("No certificates available for authentication key labelled '" + auth_key_label + "'.")
            return None

        # Find actionable certs
        actionable_certs = list(filter(lambda c: cert_action in c.possible_actions, auth_key.certificates))
        if len(actionable_certs) == 0:
            BaseController.log_info("No certificates to '" + cert_action + "' for key labelled '" + auth_key_label + "'.")
            return None
        elif len(actionable_certs) > 1:
            BaseController.log_info("Multiple certificates to '" + cert_action + "' for key labelled '" + auth_key_label + "'.")
            return None

        return actionable_certs[0]

def remote_get_token(ss_configuration, security_server):
    token_id = security_server['software_token_id']
    token_api = TokensApi(ApiClient(ss_configuration))
    token = token_api.get_token(token_id)
    return token
