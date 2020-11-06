from pprint import pprint

import urllib3
import yaml
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version
from sstoolkit.configuration.configuration import Configuration
from sstoolkit.api_client.api_client import ApiClient
from sstoolkit.api.clients_api import ClientsApi
from sstoolkit.api.tokens_api import TokensApi
from sstoolkit.models.token_password import TokenPassword
from ..rest.rest import ApiException

VERSION_BANNER = """
A toolkit for configuring security server %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        description = 'A toolkit for configuring security server'

        epilog = 'Usage: sstoolkit list-clients login-token'

        arguments = [
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER}),
        ]

    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(help='List security server clients', arguments=[])
    def list_clients(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        with open("config/base.yaml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        configuration = Configuration()
        configuration.api_key['Authorization'] = cfg["base"]["api_key"]
        configuration.host = cfg["base"]["url"]
        configuration.verify_ssl = False
        api_instance = ClientsApi(ApiClient(configuration))

        try:
            api_response = api_instance.find_clients()
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling ClientsApi->find_clients: %s\n" % e)

    @ex(
        help='Login token', arguments=[
            (['--token-id'], dict(help='TOKEN ID', nargs='?', default=[])),
            (['--token-pin'], dict(help='TOKEN PIN', nargs='?', default=[]))
        ]
    )
    def login_token(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        with open("config/base.yaml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        configuration = Configuration()
        configuration.api_key['Authorization'] = cfg["base"]["api_key"]
        configuration.host = cfg["base"]["url"]
        configuration.verify_ssl = False
        api_instance = TokensApi(ApiClient(configuration))
        token_id = self.app.pargs.token_id
        token_pin = self.app.pargs.token_pin

        try:
            api_response = api_instance.login_token(id=token_id, body=TokenPassword(password=token_pin))
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling TokensApi->login_token: %s\n" % e)
