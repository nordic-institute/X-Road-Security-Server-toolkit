import os
import unittest
from unittest.mock import Mock
from unittest.mock import patch

import yaml

from definitions import ROOT_DIR
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.base import BaseController
from xrdsst.models import ConnectionType


class TestBaseController(unittest.TestCase):

    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    _ss_config = {
        'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
         'api_key': [{'url': 'https://localhost:4000/api/v1/api-keys',
                      'roles': 'XROAD_SYSTEM_ADMINISTRATOR'}],
        'security_server':
            [{'name': 'ss',
              'url': 'https://ss:4000/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS',
              'software_token_pin': '1234'}]}

    def get_ss_config(self):
        return self._ss_config

    def create_temp_conf(self, base_controller, temp_file_name):
        config_file = open(temp_file_name, "w")
        config_file.close()
        with open(temp_file_name, "w") as yml_file:
            yaml.dump(self.get_ss_config(), yml_file)
        return base_controller.load_config(temp_file_name)

    @staticmethod
    def test_load_config():
        base_controller = BaseController()
        temp_file_name = "base.yaml"
        config_file = open(temp_file_name, "w")
        config_file.close()
        with open(temp_file_name, "r") as yml_file:
            cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
        response = base_controller.load_config(temp_file_name)
        os.remove(temp_file_name)
        assert response == cfg

    def test_load_config_exception(self):
        base_controller = BaseController()
        config_file = "/etc/shadow"
        self.assertRaises(PermissionError, lambda: base_controller.load_config(config_file))

    def test_init_logging(self):
        temp_file_name = "temp.log"
        log_file = open(temp_file_name, "w")
        self._ss_config["logging"][0]["file"] = temp_file_name
        base_controller = BaseController()
        response = base_controller.init_logging(self.get_ss_config())
        log_file.close()
        os.remove(temp_file_name)
        self.assertEqual(response, None)

    def test_init_logging_file_not_found_error(self):
        temp_file_name = "temp.log"
        self._ss_config["logging"][0]["file"] = temp_file_name
        base_controller = BaseController()
        base_controller.init_logging(self.get_ss_config())
        self.assertRaises(FileNotFoundError)

    def test_init_logging_is_directory_error(self):
        self._ss_config["logging"][0]["file"] = "/var/log"
        base_controller = BaseController()
        base_controller.init_logging(self.get_ss_config())
        self.assertRaises(IsADirectoryError)

    def test_get_api_key(self):
        with patch.object(BaseController, 'create_api_key', return_value='api-key-123'):
            base_controller = BaseController()
            temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
            config = self.create_temp_conf(base_controller, temp_file_name)
            security_server = config["security_server"][0]
            security_server["api_key"] = 'X-Road-apikey token=some key'
            key = base_controller.get_api_key(config, security_server)
            assert key != 'X-Road-apikey token=api-key-123'
            security_server["api_key"] = 'X-Road-apikey token=<API_KEY>'
            key = base_controller.get_api_key(config, security_server)
            os.remove(temp_file_name)
            assert key == 'X-Road-apikey token=api-key-123'

    def test_get_api_key_ssh_key_exception(self):
        base_controller = BaseController()
        temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
        config = self.create_temp_conf(base_controller, temp_file_name)
        security_server = config["security_server"][0]
        security_server["api_key"] = 'X-Road-apikey token=<API_KEY>'
        base_controller.get_api_key(config, security_server)
        os.remove(temp_file_name)
        self.assertRaises(Exception)

    def test_get_api_key_json_exception(self):
        base_controller = BaseController()
        temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
        config = self.create_temp_conf(base_controller, temp_file_name)
        temp_key_file = open("my_key", "w")
        temp_key_file.close()
        config["api_key"][0]["key"] = "my_key"
        security_server = config["security_server"][0]
        security_server["api_key"] = 'X-Road-apikey token=<API_KEY>'
        base_controller.get_api_key(config, security_server)
        os.remove(temp_file_name)
        os.remove("my_key")
        self.assertRaises(Exception)

    def test_initialize_basic_conf_values(self):
        base_controller = BaseController()
        temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
        config = self.create_temp_conf(base_controller, temp_file_name)
        security_server = config["security_server"][0]
        configuration = Configuration()
        configuration.api_key['Authorization'] = security_server["api_key"]
        configuration.host = security_server["url"]
        configuration.verify_ssl = False
        response = base_controller.initialize_basic_config_values(security_server)
        os.remove(temp_file_name)
        assert response.api_key == configuration.api_key
        assert response.host == configuration.host
        assert response.verify_ssl == configuration.verify_ssl

    def test_configfile_argument_added(self):
        base_controller = BaseController()
        base_controller._parser = Mock()
        base_parser = base_controller._parser
        base_parser.add_argument = Mock(return_value=None)
        base_controller._pre_argument_parsing()
        base_parser.add_argument.assert_called_once()

    def test_unsuccessful_app_exit_with_nonexistant_config_spec(self):
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.pargs = Mock()
        base_controller.app.pargs.configfile = 'just/not/there/at/all'
        base_controller.app.close = Mock(return_value=None)
        base_controller.load_config(baseconfig=None)
        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_conversion_of_text_to_swagger_enum_succeeds(self):
        assert 'HTTP' == BaseController.convert_swagger_enum(ConnectionType, "HTTP")
        assert 'HTTPS' == BaseController.convert_swagger_enum(ConnectionType, "HTTPS")
        assert 'HTTPS_NO_AUTH' == BaseController.convert_swagger_enum(ConnectionType, "HTTPS_NO_AUTH")

    def test_conversion_of_text_to_swagger_enum_fails(self):
        try:
            BaseController.convert_swagger_enum(ConnectionType, "HTTPX")
            raise AssertionError("Conversion of 'HTTPX' to ConnectionType should have failed.")
        except SyntaxWarning:
            pass
