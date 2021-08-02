import unittest
from argparse import Namespace
from unittest import mock
from xrdsst.controllers.csr import CsrController, CsrListMapper
from xrdsst.main import XRDSSTTest
from xrdsst.models import KeyUsageType, Token, TokenStatus, TokenType, Key, TokenCertificateSigningRequest
import sys
import pytest
from xrdsst.rest.rest import ApiException


class CsrTestData:
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
            certificate_signing_requests=[TokenCertificateSigningRequest(
                id="F5863EC8C6992789DC7B2261FAED32DBB636E194",
                owner_id="DEV:ORG:111",
                possible_actions=[]
            )],
            certificates=[]
        )]
    )


class TestCsr(unittest.TestCase):
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

    def test_csr_list(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', token='0')
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CsrTestData.token_response):
                csr_controller = CsrController()
                csr_controller.app = app
                csr_controller.load_config = (lambda: self.ss_config)
                csr_controller.list()

            for header in CsrListMapper.headers():
                assert header in csr_controller.app._last_rendered[0][0]

            assert csr_controller.app._last_rendered[0][1][0] == '0'
            assert csr_controller.app._last_rendered[0][1][1] == '51E66718168C93083708A074A99D3E6B5F26ECA8'
            assert csr_controller.app._last_rendered[0][1][2] == 'F5863EC8C6992789DC7B2261FAED32DBB636E194'
            assert csr_controller.app._last_rendered[0][1][3] == "DEV:ORG:111"

    def test_csr_delete(self):
        with XRDSSTTest() as app:
            key_id = '51E66718168C93083708A074A99D3E6B5F26ECA8'
            csr_id = 'F5863EC8C6992789DC7B2261FAED32DBB636E194'
            ss = 'ssX'
            app._parsed_args = Namespace(ss=ss, key=key_id, csr=csr_id)
            with mock.patch('xrdsst.api.keys_api.KeysApi.get_key',
                            return_value=CsrTestData.token_response.keys[0]):
                with mock.patch('xrdsst.api.keys_api.KeysApi.delete_csr',
                                return_value={}):
                    csr_controller = CsrController()
                    csr_controller.app = app
                    csr_controller.load_config = (lambda: self.ss_config)
                    csr_controller.delete()

                    out, err = self.capsys.readouterr()
                    assert out.count("Deleted CSR id: '%s', key id: '%s', security server: '%s'" % (csr_id, key_id, ss)) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)


