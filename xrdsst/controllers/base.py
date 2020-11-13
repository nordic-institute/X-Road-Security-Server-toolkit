import os
import logging
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

    @staticmethod
    def init_logging(config_file):
        try:
            logging.basicConfig(filename=config_file["logging"][0]["file"],
                                filemode='w',
                                level=config_file["logging"][0]["level"],
                                format='%(name)s - %(levelname)s - %(message)s')
        except FileNotFoundError as e:
            print("Configuration file \"" + config_file + "\" not found: %s\n" % e)

    @staticmethod
    def load_config():
        baseconfig = "config/base.yaml"
        # Note: this fallback below is to allow simply running xrdsst from both IDE run/debug
        # and directly from command line. There is no support for configuration file location spec yet.
        # TODO: remove fallback when configuration file spec from command-line is implemented
        if not os.path.exists(baseconfig):
            baseconfig = os.path.join("..", baseconfig)
        with open(baseconfig, "r") as yml_file:
            cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
        return cfg

    @staticmethod
    def initialize_basic_config_values(security_server):
        configuration = Configuration()
        configuration.api_key['Authorization'] = security_server["api_key"]
        configuration.host = security_server["url"]
        configuration.verify_ssl = False
        return configuration