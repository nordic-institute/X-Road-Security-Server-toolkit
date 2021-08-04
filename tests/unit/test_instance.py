import unittest
from unittest import mock
from xrdsst.controllers.instance import InstanceController, InstanceListMapper
from xrdsst.main import XRDSSTTest
from xrdsst.models import KeyUsageType
import pytest
from xrdsst.rest.rest import ApiException


class TestInstance(unittest.TestCase):
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

    def test_instance_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.xroad_instances_api.XroadInstancesApi.get_xroad_instances',
                            return_value=['DEV']):
                instance_controller = InstanceController()
                instance_controller.app = app
                instance_controller.load_config = (lambda: self.ss_config)
                instance_controller.list()

            for header in InstanceListMapper.headers():
                assert header in instance_controller.app._last_rendered[0][0]

            assert instance_controller.app._last_rendered[0][1][0] == 'ssX'
            assert instance_controller.app._last_rendered[0][1][1] == 'DEV'
            assert instance_controller.app._last_rendered[0][2][0] == 'ssY'
            assert instance_controller.app._last_rendered[0][2][1] == 'DEV'
