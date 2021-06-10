import os
import unittest
from pathlib import Path
from unittest import mock

from xrdsst.controllers.user import UserController
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.main import XRDSSTTest


class TestUser(unittest.TestCase):
    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    _ss_config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'logging': {'file': str(Path.home()) + '/xrdsst_tests.log', 'level': 'INFO'},
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'name': 'ss',
              'url': 'https://no.there.com:4000/api/v1',
              'api_key': 'TOOLKIT_SS1_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS',
              'software_token_pin': '1234',
              },
             {'name': 'ss2',
              'url': 'https://no.there.com:4000/api/v1',
              'api_key': 'TOOLKIT_SS2_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS2',
              'software_token_pin': '1234',
              }
             ]}

    def test_create_admin_user(self):
        os.environ["TOOLKIT_ADMIN_CREDENTIALS"] = 'xrd:secret'
        os.environ["TOOLKIT_SSH_USER"] = 'key'
        os.environ["TOOLKIT_SSH_PRIVATE_KEY"] = 'key'
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.user.UserController.add_user_with_groups', return_value=True):
                user_controller = UserController()
                user_controller.app = app
                user_controller.load_config = (lambda: self._ss_config)
                response = user_controller.create_user(self._ss_config)
                assert response == [True, True]

    def test_create_admin_user_fail_when_credentials_missing(self):
        self._ss_config["admin_credentials"] = ''
        with XRDSSTTest() as app:
            user_controller = UserController()
            user_controller.app = app
            user_controller.load_config = (lambda: self._ss_config)
            response = user_controller.create_user(self._ss_config)
            assert response is None
        self._ss_config["admin_credentials"] = 'TOOLKIT_ADMIN_CREDENTIALS'

    def test_create_admin_user_fail_when_ssh_user_missing(self):
        self._ss_config["ssh_access"] = {'user': '', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'}
        with XRDSSTTest() as app:
            user_controller = UserController()
            user_controller.app = app
            user_controller.load_config = (lambda: self._ss_config)
            response = user_controller.create_user(self._ss_config)
            assert response is None
        self._ss_config["ssh_access"] = {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'}

    def test_create_admin_user_fail_when_ssh_key_missing(self):
        self._ss_config["ssh_access"] = {'user': 'TOOLKIT_SSH_USER', 'private_key': ''}
        with XRDSSTTest() as app:
            user_controller = UserController()
            user_controller.app = app
            user_controller.load_config = (lambda: self._ss_config)
            response = user_controller.create_user(self._ss_config)
            assert response is None
        self._ss_config["ssh_access"] = {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'}