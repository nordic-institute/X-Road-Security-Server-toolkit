import unittest
from argparse import Namespace
from unittest import mock
from xrdsst.controllers.key import KeyController, KeyListMapper
from xrdsst.main import XRDSSTTest
from xrdsst.models import KeyUsageType, Token, TokenStatus, TokenType, Key
import sys
import pytest
from xrdsst.rest.rest import ApiException


class KeyTestData:
    token_response = Token(
        available=True,
        id=0,
        logged_in=True,
        name='softToken-0',
        possible_actions=None,
        read_only=False,
        saved_to_configuration=True,
        serial_number=None,
        status=TokenStatus.OK,
        token_infos=[{'key': 'Type'}, {'value': 'Software'}],
        type=TokenType.SOFTWARE,
        keys=[Key(
            id='51E66718168C93083708A074A99D3E6B5F26ECA8',
            available=True,
            label='SIGN-ssX',
            name='SIGN-ssX',
            saved_to_configuration=True,
            usage=KeyUsageType.SIGNING,
            certificate_signing_requests=[],
            certificates=[]
        )]
    )

class TestKey(unittest.TestCase):
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


    def test_key_list(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', token='0')
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=KeyTestData.token_response):
                key_controller = KeyController()
                key_controller.app = app
                key_controller.load_config = (lambda: self.ss_config)
                key_controller.list()

            for header in KeyListMapper.headers():
                assert header in key_controller.app._last_rendered[0][0]

            assert key_controller.app._last_rendered[0][1][0] == '51E66718168C93083708A074A99D3E6B5F26ECA8'
            assert key_controller.app._last_rendered[0][1][1] == 'SIGN-ssX'
            assert key_controller.app._last_rendered[0][1][2] == 'SIGN-ssX'
            assert key_controller.app._last_rendered[0][1][3] == KeyUsageType.SIGNING

    def test_key_list_token_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', token=None)
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=KeyTestData.token_response):
                key_controller = KeyController()
                key_controller.app = app
                key_controller.load_config = (lambda: self.ss_config)
                key_controller.list()

            assert key_controller.app._last_rendered is None

    def test_key_delete(self):
        with XRDSSTTest() as app:
            key_id = '51E66718168C93083708A074A99D3E6B5F26ECA8'
            ss = 'ssX'
            app._parsed_args = Namespace(ss=ss, key=key_id)
            with mock.patch('xrdsst.api.keys_api.KeysApi.get_key',
                            return_value=KeyTestData.token_response.keys[0]):
                with mock.patch('xrdsst.api.keys_api.KeysApi.delete_key',
                                return_value={}):
                    key_controller = KeyController()
                    key_controller.app = app
                    key_controller.load_config = (lambda: self.ss_config)
                    key_controller.delete()

                    out, err = self.capsys.readouterr()
                    assert out.count("Deleted key with id: %s, security server: %s" % (key_id, ss)) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_key_delete_key_not_found(self):
        class KeyNotFound:
            status = 400
            data = '{"status":400,"error":{"code":"key_not_found"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            key_id = '51E66718168C93083708A074A99D3E6B5F26ECA8'
            ss = 'ssX'
            app._parsed_args = Namespace(ss=ss, key=key_id)
            with mock.patch('xrdsst.api.keys_api.KeysApi.get_key',
                            side_effect=ApiException(http_resp=KeyNotFound())):
                with mock.patch('xrdsst.api.keys_api.KeysApi.delete_key',
                                return_value={}):
                    key_controller = KeyController()
                    key_controller.app = app
                    key_controller.load_config = (lambda: self.ss_config)
                    key_controller.delete()

                    out, err = self.capsys.readouterr()
                    assert out.count("Could not delete key with id: %s, security server: %s, key not found" % (key_id, ss)) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_key_update(self):
        with XRDSSTTest() as app:
            key_id = '51E66718168C93083708A074A99D3E6B5F26ECA8'
            ss = 'ssX'
            name = 'New name'
            app._parsed_args = Namespace(ss=ss, key=key_id, name=name)
            with mock.patch('xrdsst.api.keys_api.KeysApi.get_key',
                            return_value=KeyTestData.token_response.keys[0]):
                with mock.patch('xrdsst.api.keys_api.KeysApi.update_key',
                                return_value={}):
                    key_controller = KeyController()
                    key_controller.app = app
                    key_controller.load_config = (lambda: self.ss_config)
                    key_controller.update()

                    out, err = self.capsys.readouterr()
                    assert out.count("Updated key with id: %s, security server: %s, new name: %s" % (key_id, ss, name)) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_key_update_key_not_found(self):
        class KeyNotFound:
            status = 400
            data = '{"status":400,"error":{"code":"key_not_found"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            key_id = '51E66718168C93083708A074A99D3E6B5F26ECA8'
            ss = 'ssX'
            name = 'New name'
            app._parsed_args = Namespace(ss=ss, key=key_id, name=name)
            with mock.patch('xrdsst.api.keys_api.KeysApi.get_key',
                            side_effect=ApiException(http_resp=KeyNotFound())):
                with mock.patch('xrdsst.api.keys_api.KeysApi.update_key',
                                return_value={}):
                    key_controller = KeyController()
                    key_controller.app = app
                    key_controller.load_config = (lambda: self.ss_config)
                    key_controller.update()

                    out, err = self.capsys.readouterr()
                    assert out.count("Could not update key with id: %s, security server: %s, key not found" % (key_id, ss)) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)