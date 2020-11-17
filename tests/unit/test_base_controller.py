import os
import unittest
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import BaseController
import yaml


class TestBaseController(unittest.TestCase):
    _ss_config = {
        'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
        'security-server':
            [{'name': 'ss3',
              'url': 'https://ss3:4000/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'configuration_anchor': '/tmp/configuration-anchor.xml',
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS3',
              'software_token_pin': '1234'}]}

    def test_load_config(self):
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
        config_file = "conf.yaml"
        self.assertRaises(FileNotFoundError, lambda: base_controller.load_config(config_file))

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