import logging
import urllib3
from cement import ex

from .base import BaseController
from ..rest.rest import ApiException
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

    def token_list(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security-server"]:
            configuration = self.initialize_basic_config_values(security_server)
            self.remote_token_list(configuration, security_server)

    # Since this is read-only operation, do not log anything, only console output
    def remote_token_list(self, configuration, security_server):
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
        except ApiException as e:
            print("Exception when calling TokensApi->get_tokens: %s\n" % e)

    def token_login(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security-server"]:
            logging.info('Starting configuration process for security server: ' + security_server['name'])
            print('Starting configuration process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server)
            self.remote_token_login(ss_configuration, security_server)

    @staticmethod
    def remote_token_login(ss_configuration, security_server):
        token_id = security_server['software_token_id']
        token_pin = security_server['software_token_pin']
        try:
            logging.info('Performing software token ' + str(token_id) + ' login: ')
            print('Performing software token ' + str(token_id) + ' login: ')
            token_api = TokensApi(ApiClient(ss_configuration))
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
