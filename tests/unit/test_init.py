import copy
import os
import unittest
from pathlib import Path
from unittest import mock

import pytest

from definitions import ROOT_DIR
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import InitServerController
from xrdsst.core.conf_keys import ConfKeysRoot, ConfKeysSecurityServer
from xrdsst.main import XRDSSTTest
from xrdsst.models import TokenInitStatus
from xrdsst.models.initialization_status import InitializationStatus
from xrdsst.rest.rest import ApiException


def init_api_config():
    config = Configuration()
    config.api_key['Authorization'] = 'X-Road-apikey token=api-key'
    config.host = 'https://ss:4000/api/v1'
    config.verify_ssl = False
    return config


UNINITIALIZED_STATUS = InitializationStatus(is_anchor_imported=False, is_server_code_initialized=False,
                                            is_server_owner_initialized=False,
                                            software_token_init_status=TokenInitStatus.NOT_INITIALIZED)


class TestInit(unittest.TestCase):
    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    _ss_config = {
        'admin_credentials': 'user:pass',
        'logging': {'file': str(Path.home()) + '/xrdsst_tests.log', 'level': 'INFO'},
        'ssh_access': {'user': 'user', 'private_key': 'key'},
        'security_server':
            [{'name': 'ss',
              'url': 'https://no.there.com:4000/api/v1',
              'api_key': '<API_KEY>',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS',
              'software_token_pin': '1234',
              }]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_check_init_status(self):
        initialization_status = InitializationStatus(is_anchor_imported=True,
                                                     is_server_code_initialized=True,
                                                     is_server_owner_initialized=True,
                                                     software_token_init_status=TokenInitStatus.NOT_INITIALIZED)
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        return_value=initialization_status):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            response = init.check_init_status(init_api_config())
            assert response == initialization_status

    def test_check_init_status_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                        side_effect=ApiException):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            init.check_init_status(init_api_config())
            self.assertRaises(ApiException)

    def test_upload_anchor(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        return_value=expected_response):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            response = init.upload_anchor(init_api_config(), self._ss_config["security_server"][0])
            assert response == expected_response

    def test_upload_anchor_exception(self):
        with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                        side_effect=ApiException):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            init.upload_anchor(init_api_config(), self._ss_config["security_server"][0])
            self.assertRaises(ApiException)

    def test_init_security_server(self):
        expected_response = 200
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        return_value=expected_response):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            response = init.init_security_server(init_api_config(),
                                                 self._ss_config["security_server"][0])
            assert response == expected_response

    def test_init_security_server_exception(self):
        with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                        side_effect=ApiException):
            init = InitServerController()
            init.load_config = (lambda: self._ss_config)
            init.init_security_server(init_api_config(), self._ss_config["security_server"][0])
            self.assertRaises(ApiException)

    def test_initialize_server_when_already_initialized(self):
        with XRDSSTTest() as app:
            initialization_status = InitializationStatus(is_anchor_imported=True,
                                                         is_server_code_initialized=True,
                                                         is_server_owner_initialized=True,
                                                         software_token_init_status=TokenInitStatus.INITIALIZED)
            with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                            return_value=initialization_status):
                init = InitServerController()
                init.app = app
                init.load_config = (lambda: self._ss_config)
                self.assertEqual(init.initialize_server(self._ss_config), None)

    def test_initialize_server_when_not_initialized(self):
        with XRDSSTTest() as app:
            initialization_status = UNINITIALIZED_STATUS
            with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                            return_value=initialization_status):
                with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                                return_value=200):
                    with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                                    return_value=200):
                        init = InitServerController()
                        init.app = app
                        init.load_config = (lambda: self._ss_config)
                        self.assertEqual(init.initialize_server(self._ss_config), None)

    def test_init_token_id_unconfigured(self):
        with XRDSSTTest() as app:
            initialization_status = UNINITIALIZED_STATUS
            with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                            return_value=initialization_status):
                with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                                return_value=200):
                    with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                                    return_value=200):
                        init_controller = InitServerController()
                        init_controller.app = app
                        init_controller.load_config = (lambda: self._ss_config)
                        init_controller._default()

                        out, err = self.capsys.readouterr()
                        assert out.count("SKIPPED 'ss'") == 1
                        assert out.count("'ss' [init]: 'software_token_id' missing") == 1

    def test_init_attempt_of_unreachable_server(self):  # no preconditions ordinarily, but must not be done if no connectivity
        with XRDSSTTest() as app:
            initialization_status = UNINITIALIZED_STATUS
            with mock.patch('xrdsst.controllers.init.InitializationApi.get_initialization_status',
                            return_value=initialization_status):
                with mock.patch('xrdsst.controllers.init.SystemApi.upload_initial_anchor',
                                return_value=200):
                    with mock.patch('xrdsst.controllers.init.InitializationApi.init_security_server',
                                    return_value=200):
                        init_controller = InitServerController()
                        init_controller.app = app
                        init_config = copy.deepcopy(self._ss_config)
                        init_config[ConfKeysRoot.CONF_KEY_ROOT_SERVER][0][ConfKeysSecurityServer.CONF_KEY_SOFT_TOKEN_ID] = 0
                        init_controller.load_config = (lambda: init_config)
                        init_controller._default()

                        out, err = self.capsys.readouterr()
                        assert out.count("SKIPPED 'ss': no connectivity") > 0
