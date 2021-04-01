import copy
import os
import sys
import unittest
from unittest import mock

import pytest

from datetime import datetime, timedelta
from definitions import ROOT_DIR
from tests.util.test_util import ObjectStruct, DiagnosticsTestData, InitTestData
from xrdsst.api import UserApi, SystemApi, DiagnosticsApi, InitializationApi, SecurityServersApi, TokensApi
from xrdsst.controllers.status import StatusController
from xrdsst.main import XRDSSTTest
from xrdsst.models import Version, User, GlobalConfDiagnostics, InitializationStatus, TokenStatus, SecurityServer, \
    TimestampingService, Token, PossibleAction, TokenType
from xrdsst.rest.rest import ApiException


def sysadm_secoff(opt_p):
    return User(username='api-key-N', permissions=[], roles=['ROLE_XROAD_SYSTEM_ADMINISTRATOR', 'ROLE_XROAD_SECURITY_OFFICER'])


class TestStatus(unittest.TestCase):
    authcert_existing = os.path.join(ROOT_DIR, "tests/resources/authcert.pem")
    ss_config = {
        'admin_credentials': 'user:pass',
        'logging': {'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'},
        'ssh_access': {'user': 'user', 'private_key': 'key'},
        'security_server':
            [{'name': 'longServerName',
              'url': 'https://unrealz5BAlxpy9yo0XpplIQbPC.com:443',
              'certificates': [
                  '/some/where/authcert',
                  '/some/where/signcert',
              ],
              'api_key': 'X-Road-apikey token=86668888-8000-4000-a000-277727227272',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_dn_country': 'FI',
              'owner_dn_org': 'UNSERE',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122'}]}

    def serverless_config(self):
        config = copy.deepcopy(self.ss_config)
        config.pop('security_server')
        return config

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_status_no_security_servers(self):
        with XRDSSTTest() as app:
            status_controller = StatusController()
            status_controller.app = app
            status_controller.load_config = (lambda: self.serverless_config())
            status_controller._default()

            out, err = self.capsys.readouterr()
            assert out.count("No security servers defined") > 0
            for header in ['GLOBAL', 'SERVER', 'ROLES', 'INIT', 'TSAS', 'TOKEN', 'KEYS', 'CSRS', 'CERTS']:
                assert header in status_controller.app._last_rendered[0][0]

            with self.capsys.disabled():
                sys.stdout.write(out)
                sys.stderr.write(err)

    @mock.patch('xrdsst.core.api_util.is_ss_connectable', lambda x: (True, 'good connectivity (test injected)'))
    @mock.patch.object(UserApi, 'get_user', side_effect=ApiException(http_resp=ObjectStruct(status=401, reason=None, data='{"status":401}', getheaders=(lambda: None))))
    def test_status_api_key_not_accepted(self, userapi_mock):
        with XRDSSTTest() as app:
            status_controller = StatusController()
            status_controller.app = app
            status_controller.load_config = (lambda: self.ss_config)
            status_controller._default()

            out, err = self.capsys.readouterr()
            assert status_controller.app._last_rendered[0][1].count('longServerName') == 1  # Still must report server name in config
            assert status_controller.app._last_rendered[0][1].count('NO ACCESS') > 0  # ... and inform of access error

            with self.capsys.disabled():
                sys.stdout.write(out)
                sys.stderr.write(err)

    @mock.patch('xrdsst.core.api_util.is_ss_connectable', lambda x: (True, 'good connectivity (test injected)'))
    @mock.patch.object(UserApi, 'get_user', sysadm_secoff)
    @mock.patch.object(SystemApi, 'system_version', (lambda x: Version(info="6.25.0")))
    @mock.patch.object(DiagnosticsApi, 'get_global_conf_diagnostics', (lambda x:
        GlobalConfDiagnostics(status_class="FAIL", status_code="INTERNAL", prev_update_at=datetime.now(), next_update_at=datetime.now() + timedelta(minutes=5))
    ))
    @mock.patch.object(InitializationApi, 'get_initialization_status', (lambda x: InitializationStatus(False, False, False, TokenStatus.NOT_INITIALIZED)))
    def test_status_uninitialized_server(self):
        with XRDSSTTest() as app:
            status_controller = StatusController()
            status_controller.app = app
            status_controller.load_config = (lambda: self.ss_config)
            status_controller._default()

            # Global status
            assert status_controller.app._last_rendered[0][1][0].count('FAIL') == 1
            assert status_controller.app._last_rendered[0][1][0].count('INTERNAL') == 1
            assert status_controller.app._last_rendered[0][1][0].count('LAST') == 1
            assert status_controller.app._last_rendered[0][1][0].count('NEXT') == 1

            # Security server and its version
            assert status_controller.app._last_rendered[0][1][1].count('longServerName') == 1
            assert status_controller.app._last_rendered[0][1][1].count('6.25.0') == 1

            # Roles granted to API user
            assert status_controller.app._last_rendered[0][1][2].upper().count('ADMINISTRATOR') == 1
            assert status_controller.app._last_rendered[0][1][2].upper().count('OFFICER') == 1

            # Token status
            assert status_controller.app._last_rendered[0][1][3].upper().count('TOKEN NOT_INITIALIZED') == 1

            # Other columns not available
            for col in range(4, 9):
                assert '' == status_controller.app._last_rendered[0][1][col].strip()

    @mock.patch('xrdsst.core.api_util.is_ss_connectable', lambda x: (True, 'good connectivity (test injected)'))
    @mock.patch.object(UserApi, 'get_user', sysadm_secoff)
    @mock.patch.object(SystemApi, 'system_version', (lambda x: Version(info="6.25.0")))
    @mock.patch.object(DiagnosticsApi, 'get_global_conf_diagnostics', (lambda x: DiagnosticsTestData.global_ok_success))
    @mock.patch.object(InitializationApi, 'get_initialization_status', (lambda x: InitTestData.all_initialized))
    @mock.patch.object(SecurityServersApi, 'get_security_servers', (lambda x, **kwargs: [
        SecurityServer(id="TEST:GOV:8672:SSLONG", instance_id="TEST", member_class="GOV", server_address="4.2.2.1", server_code="SSLONG")
    ]))
    @mock.patch.object(SystemApi, 'get_configured_timestamping_services', (lambda x: [
        TimestampingService(name="one tsa", url="https://one.tsa"),
        TimestampingService(name="two tsa", url="https://two.tsa"),
    ]))
    @mock.patch.object(TokensApi, 'get_token', (lambda x, y: Token(
        available=True, id="0", keys=[], logged_in=False, name="softToken-0",
        possible_actions=[PossibleAction.LOGIN, PossibleAction.EDIT_FRIENDLY_NAME],
        read_only=False, saved_to_configuration=True, status=TokenStatus.OK, type=TokenType.SOFTWARE))
    )
    def test_status_initialized_server(self):
        with XRDSSTTest() as app:
            status_controller = StatusController()
            status_controller.app = app
            status_controller.load_config = (lambda: self.ss_config)
            status_controller._default()

            out, err = self.capsys.readouterr()

            # Global status
            assert status_controller.app._last_rendered[0][1][0].count('OK') == 1
            assert status_controller.app._last_rendered[0][1][0].count('SUCCESS') == 1
            assert status_controller.app._last_rendered[0][1][0].count('LAST') == 1
            assert status_controller.app._last_rendered[0][1][0].count('NEXT') == 1

            # Security server and its version
            assert status_controller.app._last_rendered[0][1][1].count('longServerName') == 1
            assert status_controller.app._last_rendered[0][1][1].count('6.25.0') == 1

            # Roles granted to API user
            assert status_controller.app._last_rendered[0][1][2].upper().count('ADMINISTRATOR') == 1
            assert status_controller.app._last_rendered[0][1][2].upper().count('OFFICER') == 1

            # Initialization statuses
            assert status_controller.app._last_rendered[0][1][3].count('ANCHOR INITIALIZED') == 1
            assert status_controller.app._last_rendered[0][1][3].count('CODE INITIALIZED') == 1
            assert status_controller.app._last_rendered[0][1][3].count('OWNER INITIALIZED') == 1
            assert status_controller.app._last_rendered[0][1][3].count('TOKEN INITIALIZED') == 1

            # TSA list
            assert status_controller.app._last_rendered[0][1][4].count('one tsa') == 1
            assert status_controller.app._last_rendered[0][1][4].count('two tsa') == 1

            # Token data
            assert status_controller.app._last_rendered[0][1][5].count('ID 0') == 1
            assert status_controller.app._last_rendered[0][1][5].count('softToken-0') == 1
            assert status_controller.app._last_rendered[0][1][5].count('STATUS OK') == 1
            assert status_controller.app._last_rendered[0][1][5].count('LOGIN NO') == 1

            # Other columns not filled with given data
            for col in range(6, 9):
                assert '' == status_controller.app._last_rendered[0][1][col].strip()

            with self.capsys.disabled():
                sys.stdout.write(out)
                sys.stderr.write(err)
