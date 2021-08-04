import unittest
from unittest import mock
from xrdsst.controllers.security_server import SecurityServerListMapper, SecurityServerController, SecurityServerVersionMapper
from xrdsst.main import XRDSSTTest
from xrdsst.models import SecurityServer, Version
import pytest
from xrdsst.rest.rest import ApiException

class TestSecurityServerData:
    security_servers_response = [
        SecurityServer(
            instance_id="DEV",
            server_code="ssX",
            id="DEV:GOV:9876:ssX",
            server_address="ssX",
            member_code="9876",
            member_class="GOV"
        ),
        SecurityServer(
            instance_id="DEV",
            server_code="ssY",
            id="DEV:COM:12345:ssY",
            server_address="ssY",
            member_code="12345",
            member_class="COM"
        )
    ]

    version = Version(info="6.26.0")


class TestSecurityServer(unittest.TestCase):
    ss_config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'logging': {'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'},
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'TOOLKIT_SS1_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_member_class': 'GOV',
              'owner_member_code': '9876',
              'owner_dn_org': 'NIIS',
              'clients': []},
             {'name': 'ssY',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'TOOLKIT_SS2_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_member_class': 'GOV',
              'owner_member_code': '9876',
              'owner_dn_org': 'NIIS',
              'clients': []}
             ]
    }

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_security_server_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.security_servers_api.SecurityServersApi.get_security_servers',
                            return_value=TestSecurityServerData.security_servers_response):
                security_server_controller = SecurityServerController()
                security_server_controller.app = app
                security_server_controller.load_config = (lambda: self.ss_config)
                security_server_controller.list()

            for header in SecurityServerListMapper.headers():
                assert header in security_server_controller.app._last_rendered[0][0]

            assert len(security_server_controller.app._last_rendered[0]) == 3

            assert security_server_controller.app._last_rendered[0][1][0] == "DEV:GOV:9876:ssX"
            assert security_server_controller.app._last_rendered[0][1][1] == 'ssX'
            assert security_server_controller.app._last_rendered[0][1][2] == 'ssX'
            assert security_server_controller.app._last_rendered[0][1][3] == 'DEV'
            assert security_server_controller.app._last_rendered[0][1][4] == 'GOV'
            assert security_server_controller.app._last_rendered[0][1][5] == '9876'

    def test_security_server_list_error(self):
        class ErrorResponse:
            status = 404
            data = '{"status":404}'
            reason = None

            def getheaders(self): return None
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.security_servers_api.SecurityServersApi.get_security_servers',
                            side_effect=ApiException(http_resp=ErrorResponse())):
                security_server_controller = SecurityServerController()
                security_server_controller.app = app
                security_server_controller.load_config = (lambda: self.ss_config)
                security_server_controller.list()

            assert security_server_controller.app._last_rendered is None

    def test_security_version_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.system_version',
                            return_value=TestSecurityServerData.version):
                security_server_controller = SecurityServerController()
                security_server_controller.app = app
                security_server_controller.load_config = (lambda: self.ss_config)
                security_server_controller.version()

            for header in SecurityServerVersionMapper.headers():
                assert header in security_server_controller.app._last_rendered[0][0]

            assert len(security_server_controller.app._last_rendered[0]) == 3

            assert security_server_controller.app._last_rendered[0][1][0] == "ssX"
            assert security_server_controller.app._last_rendered[0][1][1] == "6.26.0"
            assert security_server_controller.app._last_rendered[0][2][0] == 'ssY'
            assert security_server_controller.app._last_rendered[0][2][1] == "6.26.0"

    def test_security_version_list_error(self):
        class ErrorResponse:
            status = 404
            data = '{"status":404}'
            reason = None

            def getheaders(self): return None
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.system_version',
                            side_effect=ApiException(http_resp=ErrorResponse())):
                security_server_controller = SecurityServerController()
                security_server_controller.app = app
                security_server_controller.load_config = (lambda: self.ss_config)
                security_server_controller.version()

            assert security_server_controller.app._last_rendered is None