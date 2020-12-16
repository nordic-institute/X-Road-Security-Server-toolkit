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

    # Render arguments differ for back-ends, one approach.
    def render(self, render_data):
        if self.is_output_tabulated():
            self.app.render(render_data, headers="firstrow")
        else:
            self.app.render(render_data)

    def is_output_tabulated(self):
        return self.app.output.Meta.label == 'tabulate'

    def create_api_key(self, conf, security_server):
        if conf is None:
            config = self.config
        else:
            config = conf
        roles_list = config["api-key"][0]["roles"]
        if security_server["api_key"] != self.api_key_default:
            self.log_info('API key for security server: ' + security_server['name'] +
                          ' with roles: ' + str(roles_list) + ' has already been created')
            return security_server["api_key"]
        else:
            self.log_info('Creating API key for security server: ' + security_server['name'] +
                          ' with roles: ' + str(roles_list))
            roles = '[\\"'
            count = 1
            for role in roles_list:
                if count < len(roles_list):
                    roles += role + '\\",\\"'
                else:
                    roles += role + '\\"]'
                count += 1
            url = config["api-key"][0]["url"]
            curl_cmd = "curl -X POST -u xrd:secret --silent " + url + " --data \'" + roles + "\'" + \
                       " --header \'Content-Type: application/json\' -k"
            cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
                  config["api-key"][0]["key"] + "\" root@" + security_server["name"] + " \"" + curl_cmd + \
                  "\"" + " | jq \'.key\'"
            process = subprocess.run(cmd, shell=True, check=False, capture_output=True)
            api_key = 'X-Road-apikey token=' + str(process.stdout, 'utf-8').strip().replace('"', '')
            self.log_info('API key \"' + api_key + '\" for security server ' + security_server['name'] +
                          ' created successfully')
            for ss in config["security-server"]:
                if ss["name"] == security_server['name']:
                    ss["api_key"] = api_key
            with open(self.config_file, 'w') as config_file:
                yaml.dump(config, config_file)
            return api_key

    @staticmethod
    def init_logging(configuration):
        try:
            log_file_name = configuration["logging"][0]["file"]
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
            cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
        self.config_file = baseconfig
        self.config = cfg
        return cfg

    def initialize_basic_config_values(self, security_server, config=None):
        configuration = Configuration()
        configuration.api_key['Authorization'] = self.create_api_key(config, security_server)
        configuration.host = security_server["url"]
        configuration.verify_ssl = False
        return configuration

    @staticmethod
    def log_api_error(api_method, exception):
        logging.error("Exception calling " + api_method + ": " + str(exception))
        print("Exception calling " + api_method + ": " + str(exception))

    @staticmethod
    def log_info(message):
        logging.info(message)
        print(message)
