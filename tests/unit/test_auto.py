import sys
import unittest
from unittest import mock

import pytest

from tests.util.test_util import ObjectStruct, StatusTestData
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.auto import AutoController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import StatusController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest


class TestAuto(unittest.TestCase):
    ss_config = {
        'ssh_access': [{'admin_credentials': 'user:pass', 'user': 'user', 'private_key': 'key'}],
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'X-Road-apikey token=66666666-8000-4011-a000-333336633333',
              'api_key_roles': ['XROAD_SYSTEM_ADMINISTRATOR'],
              'api_key_url': 'https://localhost:4000/api/v1/api-keys'
            }]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @mock.patch.object(XRDSSTTest, 'pargs', ObjectStruct(configfile=BaseController.config_file))
    @mock.patch.object(BaseController, 'load_config', (lambda x, y=None: TestAuto.ss_config))
    @mock.patch.object(StatusController, '_default', (lambda x: StatusTestData.server_status_essentials_complete))  # Double mock!
    @mock.patch.object(ServiceController, 'enable_description')
    @mock.patch.object(ServiceController, 'add_description')
    @mock.patch.object(ClientController, 'register')
    @mock.patch.object(ClientController, 'add')
    @mock.patch.object(CertController, 'activate')
    @mock.patch.object(CertController, 'register')
    @mock.patch.object(CertController, 'import_')
    @mock.patch.object(TokenController, 'init_keys')
    @mock.patch.object(TokenController, 'login')
    @mock.patch.object(TimestampController, 'init')
    @mock.patch.object(InitServerController, '_default')
    def test_autoconfig(self,
                        init_mock, timestamp_init_mock, token_login_mock, token_key_init_mock,
                        cert_import_mock, cert_register_mock, cert_activate_mock,
                        client_add_mock, client_register_mock, service_desc_add_mock, service_desc_enable_mock):
        with XRDSSTTest() as app:
            auto_controller = AutoController()
            auto_controller.app = app
            auto_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)  # Double mock!
            auto_controller._default()

            init_mock.assert_called_once()
            timestamp_init_mock.assert_called_once()
            token_login_mock.assert_called_once()
            token_key_init_mock.assert_called_once()
            cert_import_mock.assert_called_once()
            cert_register_mock.assert_called_once()
            cert_activate_mock.assert_called_once()
            client_add_mock.assert_called_once()
            client_register_mock.assert_called_once()
            service_desc_add_mock.assert_called_once()
            service_desc_enable_mock.assert_called_once()

    @mock.patch.object(XRDSSTTest, 'pargs', ObjectStruct(configfile=BaseController.config_file))
    @mock.patch.object(BaseController, 'load_config', (lambda x, y=None: TestAuto.ss_config))
    @mock.patch.object(StatusController, '_default', (lambda x: StatusTestData.server_status_essentials_complete_token_logged_out()))  # Double mock!
    @mock.patch.object(TokenController, 'init_keys')
    @mock.patch.object(TokenController, 'login')
    @mock.patch.object(TimestampController, 'init')
    @mock.patch.object(InitServerController, '_default')
    def test_autoconfig_token_login_fails(self,
                                          init_mock, timestamp_init_mock, token_login_mock, token_initkey_mock):
        with XRDSSTTest() as app:
            auto_controller = AutoController()
            auto_controller.app = app
            auto_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete_token_logged_out())  # Double mock!
            auto_controller._default()

            init_mock.assert_called_once()
            timestamp_init_mock.assert_called_once()
            token_login_mock.assert_called_once()
            token_initkey_mock.assert_not_called()

            out, err = self.capsys.readouterr()
            assert 1 == out.count("completion was NOT detected")
            assert 1 == out.count("Next AUTO operation would have been ['token init-keys'].")

            with self.capsys.disabled():
                sys.stdout.write(out)
                sys.stderr.write(err)
