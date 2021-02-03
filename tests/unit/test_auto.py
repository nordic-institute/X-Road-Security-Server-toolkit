import unittest
from unittest import mock

from tests.util.test_util import ObjectStruct
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.auto import AutoController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest

class TestAuto(unittest.TestCase):
    ss_config = {
        'api_key': [{'url': 'https://localhost:4000/api/v1/api-keys',
                     'key': 'private key',
                     'credentials': 'user:pass',
                     'roles': 'XROAD_SYSTEM_ADMINISTRATOR'}],
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              }]}

    @mock.patch.object(XRDSSTTest, 'pargs', ObjectStruct(configfile=BaseController.config_file))
    @mock.patch.object(BaseController, 'load_config', (lambda x, y=None: TestAuto.ss_config))
    @mock.patch.object(CertController, 'activate')
    @mock.patch.object(CertController, 'register')
    @mock.patch.object(CertController, 'import_')
    @mock.patch.object(TokenController, 'init_keys')
    @mock.patch.object(TokenController, 'login')
    @mock.patch.object(TimestampController, 'init')
    @mock.patch.object(InitServerController, '_default')
    def test_autoconfig(self, init_mock, timestamp_init_mock, token_login_mock, token_key_init_mock, cert_import_mock, cert_register_mock, cert_activate_mock):
        with XRDSSTTest() as app:
            auto_controller = AutoController()
            auto_controller.app = app
            auto_controller._default()

            init_mock.assert_called_once()
            timestamp_init_mock.assert_called_once()
            token_login_mock.assert_called_once()
            token_key_init_mock.assert_called_once()
            cert_import_mock.assert_called_once()
            cert_register_mock.assert_called_once()
            cert_activate_mock.assert_called_once()
