import unittest
from unittest import mock
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import InitServerController
from xrdsst.models import TokenInitStatus
from xrdsst.models.initialization_status import InitializationStatus
from xrdsst.rest.rest import ApiException
from tests.unit.test_base_controller import TestBaseController


class TestInit(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_controller = TestBaseController()
        self._ss_config = base_controller.get_ss_config()
        config = Configuration()
        config.api_key['Authorization'] = self._ss_config["security_server"][0]["api_key"]
        config.host = self._ss_config["security_server"][0]["url"]
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
            init.load_config = (lambda: self._ss_config)
            response = init.check_init_status(self._config)
            assert response == initialization_status

    def test_check_init_status_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        side_effect=ApiException):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            init.check_init_status(self._config)
            self.assertRaises(ApiException)

    def test_upload_anchor(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        return_value=expected_response):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            response = init.upload_anchor(self._config, self._ss_config["security_server"][0])
            assert response == expected_response

    def test_upload_anchor_exception(self):
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        side_effect=ApiException):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            init.upload_anchor(self._config, self._ss_config["security_server"][0])
            self.assertRaises(ApiException)

    def test_init_security_server(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        return_value=expected_response):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            response = init.init_security_server(self._config,
                                                 self._ss_config["security_server"][0])
            assert response == expected_response

    def test_init_security_server_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        side_effect=ApiException):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            init.init_security_server(self._config, self._ss_config["security_server"][0])
            self.assertRaises(ApiException)

    def test_initialize_server_when_already_initialized(self):
        initialization_status = InitializationStatus(is_anchor_imported=True,
                                                     is_server_code_initialized=True,
                                                     is_server_owner_initialized=True,
                                                     software_token_init_status=TokenInitStatus.INITIALIZED)
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=initialization_status):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            self.assertEqual(init.initialize_server(self._ss_config), None)

    def test_initialize_server_when_not_initialized(self):
        initialization_status = InitializationStatus(is_anchor_imported=False,
                                                     is_server_code_initialized=False,
                                                     is_server_owner_initialized=False,
                                                     software_token_init_status=TokenInitStatus.NOT_INITIALIZED)
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=initialization_status):
            with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                            return_value=200):
                with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                                return_value=200):
                    init = InitServerController()
                    init.load_config = (lambda: self._ss_config)
                    self.assertEqual(init.initialize_server(self._ss_config), None)
