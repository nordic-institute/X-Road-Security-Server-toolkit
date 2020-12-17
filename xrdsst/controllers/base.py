import json
import os
import logging
import subprocess
import yaml
from cement import Controller
from cement.utils.version import get_version_banner
from xrdsst.core.version import get_version
from xrdsst.resources.texts import texts
from xrdsst.configuration.configuration import Configuration

BANNER = texts['app.description'] + ' ' + get_version() + '\n' + get_version_banner()


class BaseController(Controller):
    class Meta:
        label = 'base'
        description = texts['app.description']
        arguments = [
            (['-v', '--version'], {'action': 'version', 'version': BANNER})
        ]

    config_file = "config/base.yaml"
    config = None
    api_key_default = "X-Road-apikey token=<API_KEY>"
    api_key_id = {}

    def create_api_key(self, roles_list, config, security_server):
        self.log_info('Creating API key for security server: ' + security_server['name'])
        roles = '[\\"'
        count = 1
        for role in roles_list:
            if count < len(roles_list):
                roles += role + '\\",\\"'
            else:
                roles += role + '\\"]'
            count += 1
        curl_cmd = "curl -X POST -u xrd:secret --silent " + config["api-key"][0]["url"] + " --data \'" + \
                   roles + "\'" + " --header \'Content-Type: application/json\' -k"
        cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
              config["api-key"][0]["key"] + "\" root@" + security_server["name"] + " \"" + curl_cmd + "\""
        if os.path.isfile(config["api-key"][0]["key"]):
            try:
                process = subprocess.run(cmd, shell=True, check=False, capture_output=True)
                api_key_json = json.loads(str(process.stdout, 'utf-8').strip())
                self.api_key_id[security_server['name']] = api_key_json["id"]
                self.log_info('API key \"' + api_key_json["key"] + '\" for security server ' + security_server['name'] +
                              ' created successfully')
                return api_key_json["key"]
            except Exception as err:
                self.log_api_error('BaseController->create_api_key:', err)
        else:
            raise Exception("SSH private key file does not exists")

    # Render arguments differ for back-ends, one approach.
    def render(self, render_data):
        if self.is_output_tabulated():
            self.app.render(render_data, headers="firstrow")
        else:
            self.app.render(render_data)

    def is_output_tabulated(self):
        return self.app.output.Meta.label == 'tabulate'

    def get_api_key(self, conf, security_server):
        if conf is None:
            config = self.config
        else:
            config = conf
        roles_list = config["api-key"][0]["roles"]
        api_key = None
        if security_server["api_key"] != self.api_key_default:
            self.log_info('API key for security server: ' + security_server['name'] + ' has already been created')
            api_key = security_server["api_key"]
        else:
            try:
                api_key = 'X-Road-apikey token=' + self.create_api_key(roles_list, conf, security_server)
            except Exception as err:
                self.log_api_error('BaseController->get_api_key:', err)
        return api_key

    @staticmethod
    def init_logging(configuration):
        try:
            log_file_name = configuration["logging"][0]["file"]
            if not os.path.isfile(log_file_name):
                raise FileNotFoundError
            logging.basicConfig(filename=log_file_name,
                                level=configuration["logging"][0]["level"],
                                format='%(name)s - %(levelname)s - %(message)s')
        except FileNotFoundError as err:
            print("Configuration file \"" + log_file_name + "\" not found: %s\n" % err)

    def load_config(self, baseconfig="config/base.yaml"):
        # Note: this fallback below is to allow simply running xrdsst from both IDE run/debug
        # and directly from command line. There is no support for configuration
        # file location spec yet.
        # TODO: remove fallback when configuration file spec from command-line is implemented
        if not os.path.exists(baseconfig):
            baseconfig = os.path.join("..", baseconfig)
        with open(baseconfig, "r") as yml_file:
            self.config = yaml.load(yml_file, Loader=yaml.FullLoader)
        self.config_file = baseconfig
        return self.config

    def initialize_basic_config_values(self, security_server, config=None):
        configuration = Configuration()
        configuration.api_key['Authorization'] = self.get_api_key(config, security_server)
        configuration.host = security_server["url"]
        configuration.verify_ssl = False
        return configuration

    def revoke_api_key(self, security_server, config=None):
        if self.api_key_id:
            self.log_info('Revoking API key for security server ' + security_server['name'])
            curl_cmd = "curl -X DELETE -u xrd:secret --silent " + config["api-key"][0]["url"] + "/" + \
                       str(self.api_key_id[security_server['name']]) + " -k"
            cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
                config["api-key"][0]["key"] + "\" root@" + security_server["name"] + " \"" + curl_cmd + "\""
            process = subprocess.run(cmd, shell=True, check=False, capture_output=True)
            self.log_info('API key for security server ' + security_server['name'] + ' revoked successfully')

    @staticmethod
    def log_api_error(api_method, exception):
        logging.error("Exception calling " + api_method + ": " + str(exception))
        print("Exception calling " + api_method + ": " + str(exception))

    @staticmethod
    def log_info(message):
        logging.info(message)
        print(message)
