import logging
import urllib3
from cement import ex

from .base import BaseController
from ..rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.models.token_password import TokenPassword
from xrdsst.resources.texts import texts


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

    def token_list(self, config_file):
        self.init_logging(config_file)
        for security_server in config_file["security-server"]:
            configuration = self.initialize_basic_config_values(security_server)
            self.remote_token_list(configuration, security_server)

    @staticmethod # Since this is read-only operation, do not log anything, only console output
    def remote_token_list(configuration, security_server):
        try:
            token_api = TokensApi(ApiClient(configuration))
            api_response = token_api.get_tokens()
            print('(Security server): TOKEN ID: NAME, STATUS, LOGIN STATUS, TOKEN INFO')
            for server_token in api_response:
                print(
                    '(', security_server['name'], ') :',
                    server_token.id, ' :', server_token.name, ', ', server_token.status, ', ',
                    server_token.logged_in, ',' , str(server_token.token_infos)
                )
        except ApiException as e:
            print("Exception when calling TokensApi->get_tokens: %s\n" % e)

    def token_login(self, config_file):
        self.init_logging(config_file)
        for security_server in config_file["security-server"]:
            logging.info('Starting configuration process for security server: ' + security_server['name'])
            print('Starting configuration process for security server: ' + security_server['name'])
            configuration = self.initialize_basic_config_values(security_server)
            self.remote_token_login(configuration, security_server)

    @staticmethod
    def remote_token_login(configuration, security_server):
        token_id = security_server['software_token_id']
        token_pin = security_server['software_token_pin']
        try:
            logging.info('Performing software token ' + str(token_id) + ' login: ')
            print('Performing software token ' + str(token_id) + ' login: ')
            token_api = TokensApi(ApiClient(configuration))
            token_api.login_token(
                id=token_id,
                body=TokenPassword(token_pin)
            )
            logging.info('Security server \"' + security_server["name"]  + '\"  token ' + str(token_id) + ' logged in')
            print('Security server \"' + security_server["name"] + '\"  token ' +str(token_id) + ' logged in')
        except ApiException as e:
            if 409 == e.status:
                print("Token already logged in.")
            else:
                print("Exception when calling TokensApi->login_token: %s\n" % e)
                logging.error("Exception when calling TokensApi->login_token: %s\n" % e)
