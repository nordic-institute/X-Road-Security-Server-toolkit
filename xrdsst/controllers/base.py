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
        stacked_on = 'base'
        description = texts['app.description']
        arguments = [
            (['-v', '--version'], {'action': 'version', 'version': BANNER})
        ]

    def _pre_argument_parsing(self):
        p = self._parser
        # Top level configuration file specification only
        if (issubclass(BaseController, self.__class__)) and issubclass(self.__class__, BaseController):
            p.add_argument('-c', '--configfile',
                           # TODO after the conventional name and location for config file gets figured out, extract to texts
                           help="Specify configuration file to use instead of default 'config/base.yaml'",
                           metavar='file',
                           default='config/base.yaml') # TODO extract to consts after settling on naming

    # Render arguments differ for back-ends, one approach.
    def render(self, render_data):
        if self.is_output_tabulated():
            self.app.render(render_data, headers="firstrow")
        else:
            self.app.render(render_data)

    def is_output_tabulated(self):
        return self.app.output.Meta.label == 'tabulate'

    @staticmethod
    def init_logging(configuration):
        try:
            log_file_name = configuration["logging"][0]["file"]
            logging.basicConfig(filename=log_file_name,
                                level=configuration["logging"][0]["level"],
                                format='%(name)s - %(levelname)s - %(message)s')
        except FileNotFoundError as err:
            print("Configuration file \"" + log_file_name + "\" not found: %s\n" % err)

    def load_config(self, baseconfig=None):
        if not baseconfig:
            baseconfig = self.app.pargs.configfile
        if not os.path.exists(baseconfig):
            self.log_info("Cannot load config '" + baseconfig + "'")
            self.app.close(os.EX_CONFIG)
        else:
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

    @staticmethod
    def log_api_error(api_method, exception):
        logging.error("Exception calling " + api_method + ": " + str(exception))
        print("Exception calling " + api_method + ": " + str(exception))

    @staticmethod
    def log_info(message):
        logging.info(message)
        print(message)
