import logging
import urllib3
import yaml
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version
from ..models import InitialServerConf
from ..rest.rest import ApiException
from xrdsst.configuration.configuration import Configuration
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.initialization_api import InitializationApi
from xrdsst.api.system_api import SystemApi

VERSION_BANNER = """
A toolkit for configuring security server %s
%s
""" % (get_version(), get_version_banner())


def load_config():
    with open("config/base.yaml", "r") as yml_file:
        cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
    return cfg


def initialize_basic_config_values(security_server):
    configuration = Configuration()
    configuration.api_key['Authorization'] = security_server["api_key"]
    configuration.host = security_server["url"]
    configuration.verify_ssl = False
    return configuration


class Init(Controller):
    class Meta:
        label = 'init'

        description = 'A toolkit for configuring security server'

        epilog = 'Usage: xrdsst init'

        arguments = [
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER}),
        ]

    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(help='Initialize security server', arguments=[])
    def init(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        cfg = load_config()
        logging.basicConfig(filename=cfg["logging"][0]["file"],
                            filemode='w',
                            level=cfg["logging"][0]["level"],
                            format='%(name)s - %(levelname)s - %(message)s')
        for security_server in cfg["security-server"]:
            logging.info('Starting configuration process for security server: ' + security_server['name'])
            print('Starting configuration process for security server: ' + security_server['name'])
            configuration = initialize_basic_config_values(security_server)
            configuration_check = self.check_init_status(configuration)
            if configuration_check.is_anchor_imported:
                logging.info('Configuration anchor for \"' + security_server['name'] + '\" already imported')
                print('Configuration anchor for \"' + security_server['name'] + '\" already imported')
            else:
                self.upload_anchor(configuration, security_server)
            if configuration_check.is_server_code_initialized:
                logging.info('Security server \"' + security_server['name'] + '\" already initialized')
                print('Security server \"' + security_server['name'] + '\" already initialized')
            else:
                self.init_server(configuration, security_server)

    @staticmethod
    def check_init_status(configuration):
        try:
            initialization_api = InitializationApi(ApiClient(configuration))
            response = initialization_api.get_initialization_status()
            return response
        except ApiException as e:
            print("Exception when calling InitializationApi->get_initialization_status: %s\n" % e)
            logging.error("Exception when calling InitializationApi->get_initialization_status: %s\n" % e)

    @staticmethod
    def upload_anchor(configuration, security_server):
        try:
            logging.info('Uploading configuration anchor for security server: ' + security_server['name'])
            print('Uploading configuration anchor for security server: ' + security_server['name'])
            system_api = SystemApi(ApiClient(configuration))
            anchor = open(security_server["configuration_anchor"], "r")
            system_api.upload_initial_anchor(body=anchor.read())
            logging.info(
                'Upload of configuration anchor from \"' + security_server["configuration_anchor"] + '\" successful')
            print('Upload of configuration anchor from \"' + security_server["configuration_anchor"] + '\" successful')
        except ApiException as e:
            print("Exception when calling SystemApi->upload_initial_anchor: %s\n" % e)
            logging.error("Exception when calling SystemApi->upload_initial_anchor: %s\n" % e)

    @staticmethod
    def init_server(configuration, security_server):
        try:
            logging.info('Initializing security server: ' + security_server['name'])
            print('Initializing security server: ' + security_server['name'])
            initialization_api = InitializationApi(ApiClient(configuration))
            initialization_api.init_security_server(body=InitialServerConf(
                owner_member_class=security_server["owner_member_class"],
                owner_member_code=security_server["owner_member_code"],
                security_server_code=security_server["security_server_code"],
                software_token_pin=security_server["software_token_pin"],
                ignore_warnings=True))
            logging.info('Security server \"' + security_server["name"] + '\" initialized')
            print('Security server \"' + security_server["name"] + '\" initialized')
        except ApiException as e:
            print("Exception when calling InitializationApi->init_security_server: %s\n" % e)
            logging.error("Exception when calling InitializationApi->init_security_server: %s\n" % e)
