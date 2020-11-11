import os
import unittest
from unittest import mock
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import Init
from xrdsst.rest.rest import ApiException
import yaml


class TestInit(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ss_config = {
            'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
            'security-server':
                [{'name': 'ss3',
                  'url': 'https://ss3:4000/api/v1',
                  'api_key': 'X-Road-apikey token=api-key',
                  'configuration_anchor': '/etc/xroad/configuration-anchor.xml',
                  'owner_member_class': 'GOV',
                  'owner_member_code': '1234',
                  'security_server_code': 'SS3',
                  'software_token_pin': '1234'}]}
        self._ss_config = ss_config
        config = Configuration()
        config.api_key['Authorization'] = ss_config["security-server"][0]["api_key"]
        config.host = ss_config["security-server"][0]["url"]
        config.verify_ssl = False
        self._config = config

    def test_check_init_status(self):
        expected_response = {
            'is_anchor_imported': False,
            'is_server_code_initialized': False,
            'is_server_owner_initialized': False,
            'software_token_init_status': 'NOT_INITIALIZED'
        }
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=expected_response):
            init = Init()
            response = init.check_init_status(self._config)
            assert response == expected_response

    def test_check_init_status_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        side_effect=ApiException):
            init = Init()
            init.check_init_status(self._config)
            self.assertRaises(ApiException)

    def test_upload_anchor(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        return_value=expected_response):
            init = Init()
            response = init.upload_anchor(self._config, self._ss_config["security-server"][0])
            assert response == expected_response

    def test_upload_anchor_exception(self):
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        side_effect=ApiException):
            init = Init()
            init.upload_anchor(self._config, self._ss_config["security-server"][0])
            self.assertRaises(ApiException)

    def test_init_security_server(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        return_value=expected_response):
            init = Init()
            response = init.init_security_server(self._config, self._ss_config["security-server"][0])
            assert response == expected_response

    def test_init_security_server_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        side_effect=ApiException):
            init = Init()
            init.init_security_server(self._config, self._ss_config["security-server"][0])
            self.assertRaises(ApiException)

    def test_load_config(self):
        init = Init()
        config_file = "../../config/base.yaml"
        with open(config_file, "r") as yml_file:
            cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
        response = init.load_config(config_file)
        assert response == cfg

    def test_load_config_exception(self):
        init = Init()
        config_file = "../../config/conf.yaml"
        init.load_config(config_file)
        self.assertRaises(FileNotFoundError)

    def test_init_logging(self):
        temp_file_name = "temp.log"
        log_file = open(temp_file_name, "w")
        self._ss_config["logging"][0]["file"] = temp_file_name
        init = Init()
        response = init.init_logging(self._ss_config)
        log_file.close()
        os.remove(temp_file_name)
        self.assertEqual(response, None)

    def test_init_logging_exception(self):
        temp_file_name = "temp.log"
        self._ss_config["logging"][0]["file"] = temp_file_name
        init = Init()
        init.init_logging(self._ss_config)
        self.assertRaises(FileNotFoundError)

    def test_initialize_basic_conf_values(self):
        init = Init()
        security_server = self._ss_config["security-server"][0]
        configuration = Configuration()
        configuration.api_key['Authorization'] = security_server["api_key"]
        configuration.host = security_server["url"]
        configuration.verify_ssl = False
        response = init.initialize_basic_config_values(security_server)
        assert response.api_key == configuration.api_key
        assert response.host == configuration.host
        assert response.verify_ssl == configuration.verify_ssl
