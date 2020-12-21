import json
import os
import logging
import subprocess
import yaml
from cement import Controller
from cement.utils.version import get_version_banner

from definitions import ROOT_DIR
from xrdsst.core.version import get_version
from xrdsst.resources.texts import texts
from xrdsst.configuration.configuration import Configuration

BANNER = texts['app.description'] + ' ' + get_version() + '\n' + get_version_banner()


class BaseController(Controller):
    class Meta:
        label = 'base'
        stacked_on = 'base'
        description = texts['app.description']
        arguments = [
            (['-v', '--version'], {'action': 'version', 'version': BANNER})
        ]

    config_file = os.path.join(ROOT_DIR, "config/base.yaml")
    config = None
    api_key_default = "X-Road-apikey token=<API_KEY>"
    api_key_id = {}

    def _pre_argument_parsing(self):
        p = self._parser
        # Top level configuration file specification only
        if (issubclass(BaseController, self.__class__)) and issubclass(self.__class__, BaseController):
            p.add_argument('-c', '--configfile',
                           # TODO after the conventional name and location for config file gets figured out, extract to texts
                           help="Specify configuration file to use instead of default 'config/base.yaml'",
                           metavar='file',
                           default=os.path.join(ROOT_DIR, "config/base.yaml")) # TODO extract to consts after settling on naming

    def create_api_key(self, roles_list, config, security_server):
        self.log_info('Creating API key for security server: ' + security_server['name'])
        roles = []
        for role in roles_list:
            roles.append(role)
        curl_cmd = "curl -X POST -u " + config["api_key"][0]["credentials"] + " --silent " + \
                   config["api_key"][0]["url"] + " --data \'" + json.dumps(roles).replace('"', '\\"') + "\'" + \
                   " --header \'Content-Type: application/json\' -k"
        cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
              config["api_key"][0]["key"] + "\" root@" + security_server["name"] + " \"" + curl_cmd + "\""
        if os.path.isfile(config["api_key"][0]["key"]):
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
        config = conf if conf else self.config
        roles_list = config["api_key"][0]["roles"]
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

    def load_config(self, baseconfig=os.path.join(ROOT_DIR, "config/base.yaml")):
        if not baseconfig:
            baseconfig = self.app.pargs.configfile
            self.config_file = baseconfig
        if not os.path.exists(baseconfig):
            self.log_info("Cannot load config '" + baseconfig + "'")
            self.app.close(os.EX_CONFIG)
        else:
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

    @staticmethod
    def log_api_error(api_method, exception):
        logging.error("Exception calling " + api_method + ": " + str(exception))
        print("Exception calling " + api_method + ": " + str(exception))

    @staticmethod
    def log_info(message):
        logging.info(message)
        print(message)
