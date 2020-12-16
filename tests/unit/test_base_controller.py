import os
import unittest
from unittest.mock import Mock

import yaml

from definitions import ROOT_DIR
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.base import BaseController
from xrdsst.main import XRDSSTTest


class TestBaseController(unittest.TestCase):
    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    _ss_config = {
        'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
        'security-server':
            [{'name': 'ss',
              'url': 'https://ss:4000/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'configuration_anchor': configuration_anchor,
              'owner_dn_country': 'FI',
              'owner_dn_org': 'UNSERE',
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS',
              'software_token_pin': '1234'}]}

    def get_ss_config(self):
        return self._ss_config

    @staticmethod
    def test_is_output_tabulated():
        with XRDSSTTest() as app:
            base_controller = BaseController()
            base_controller.app = app
            assert base_controller.is_output_tabulated()

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
        response = base_controller.init_logging(self._ss_config)
        log_file.close()
        os.remove(temp_file_name)
        self.assertEqual(response, None)

    def test_init_logging_exception(self):
        temp_file_name = "temp.log"
        self._ss_config["logging"][0]["file"] = temp_file_name
        base_controller = BaseController()
        base_controller.init_logging(self._ss_config)
        self.assertRaises(FileNotFoundError)

    def test_initialize_basic_conf_values(self):
        base_controller = BaseController()
        security_server = self._ss_config["security-server"][0]
        configuration = Configuration()
        configuration.api_key['Authorization'] = security_server["api_key"]
        configuration.host = security_server["url"]
        configuration.verify_ssl = False
        response = base_controller.initialize_basic_config_values(security_server)
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
        base_controller.load_config()
        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)
