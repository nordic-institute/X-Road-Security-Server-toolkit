import unittest
from unittest import mock
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import InitServerController
from xrdsst.models.initialization_status import InitializationStatus
from xrdsst.rest.rest import ApiException


class TestInit(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ss_config = {
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
        self._ss_config = ss_config
        config = Configuration()
        config.api_key['Authorization'] = ss_config["security-server"][0]["api_key"]
        config.host = ss_config["security-server"][0]["url"]
        config.verify_ssl = False
        self._config = config

    def test_check_init_status(self):
        initialization_status = InitializationStatus(is_anchor_imported=True,
                                                     is_server_code_initialized=True,
                                                     is_server_owner_initialized=True,
                                                     software_token_init_status='NOT_INITLIALIZED')
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=initialization_status):
            init = InitServerController()
            response = init.check_init_status(self._config)
            assert response == initialization_status

    def test_check_init_status_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        side_effect=ApiException):
            init = InitServerController()
            init.check_init_status(self._config)
            self.assertRaises(ApiException)

    def test_upload_anchor(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        return_value=expected_response):
            init = InitServerController()
            response = init.upload_anchor(self._config, self._ss_config["security-server"][0])
            assert response == expected_response

    def test_upload_anchor_exception(self):
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        side_effect=ApiException):
            init = InitServerController()
            init.upload_anchor(self._config, self._ss_config["security-server"][0])
            self.assertRaises(ApiException)

    def test_init_security_server(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        return_value=expected_response):
            init = InitServerController()
            response = init.init_security_server(self._config, self._ss_config["security-server"][0])
            assert response == expected_response

    def test_init_security_server_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        side_effect=ApiException):
            init = InitServerController()
            init.init_security_server(self._config, self._ss_config["security-server"][0])
            self.assertRaises(ApiException)

    def test_initialize_server_when_already_initialized(self):
        initialization_status = InitializationStatus(is_anchor_imported=True,
                                                     is_server_code_initialized=True,
                                                     is_server_owner_initialized=True,
                                                     software_token_init_status='INITLIALIZED')
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=initialization_status):
            init = InitServerController()
            response = init.initialize_server(self._ss_config)
            self.assertEqual(response, None)

    def test_initialize_server_when_not_initialized(self):
        initialization_status = InitializationStatus(is_anchor_imported=False,
                                                     is_server_code_initialized=False,
                                                     is_server_owner_initialized=False,
                                                     software_token_init_status='NOT_INITLIALIZED')
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=initialization_status):
            with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                            return_value=200):
                with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                                return_value=200):
                    init = InitServerController()
                    response = init.initialize_server(self._ss_config)
                    self.assertEqual(response, None)
