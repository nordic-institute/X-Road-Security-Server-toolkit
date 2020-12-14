import os
import unittest
from datetime import datetime
from unittest import mock

from dateutil.tz import tzutc

import urllib3

from definitions import ROOT_DIR
from xrdsst.main import XRDSSTTest
from xrdsst.models import Token, TokenStatus, TokenType, Key, KeyUsageType, TokenCertificate, \
    CertificateOcspStatus, CertificateStatus, CertificateDetails, KeyUsage, CertificateAuthority, \
    CertificateAuthorityOcspResponse, SecurityServer, KeyWithCertificateSigningRequestId, \
    TokenCertificateSigningRequest

from xrdsst.controllers.token import TokenController


class TokenTestData:
    # JSON of the response unusable due to assertions in generated Client API,
    # define response in Python
    token_login_response = Token(
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
            certificates=[
                TokenCertificate(
                    active=True,
                    ocsp_status=CertificateOcspStatus.OCSP_RESPONSE_GOOD,
                    owner_id='DEV:GOV:1928',
                    saved_to_configuration=True,
                    status=CertificateStatus.REGISTERED,
                    certificate_details=CertificateDetails(
                        hash='F65685ADDAA5BDB1BA2BF58FCCC4386A1EAD0F6D',
                        issuer_common_name='Test CA',
                        issuer_distinguished_name='CN=Test CA, O=X-Road Test CA',
                        subject_common_name='',
                        subject_distinguished_name='',
                        key_usages=[KeyUsage.NON_REPUDIATION],
                        not_after=datetime(2040, 10, 31, 22, 24, 45, tzinfo=tzutc()),
                        not_before=datetime(2020, 11, 5, 22, 24, 45, tzinfo=tzutc()),
                        public_key_algorithm='RSA',
                        rsa_public_key_exponent=65537,
                        rsa_public_key_modulus=214432,  # Not even a prime, but fine ATM
                        signature='30eb0bde826774031726',
                        signature_algorithm='SHA256withRSA',
                        serial=5,
                        version=3
                    )
                )
            ]
        )]
    )

    # As long as there is single token, the information is the same as returned on token login
    token_list_response = [
        token_login_response
    ]

    security_servers_current_server_response = [
        SecurityServer(
            id="DEV:GOV:7392:UNS-SSX",
            instance_id="DEV",
            member_class="GOV",
            member_code="7392",
            server_code="UNS-SSX",
            server_address="ssX"
        )
    ]

    ca_list_response = [
        CertificateAuthority(
            name="Some CA",
            subject_distinguished_name="CN=Some CA, O=Some X-Road CA",
            issuer_distinguished_name="CN=Some Other CA, O=Some Other X-Road CA",
            ocsp_response=CertificateAuthorityOcspResponse.OCSP_RESPONSE_UNKNOWN,
            not_after=datetime(2180, 1, 14, 0, 0, 0),
            top_ca=True,
            path="CN=Some Other CA, O=Some Other X-Road CA",
            authentication_only=False
        )
    ]

    add_key_with_csr_response = KeyWithCertificateSigningRequestId(
        csr_id="16F2B5A9D76B790EE3DD7544152E333FC57F57FF",
        key=Key(
            available=True,
            certificate_signing_requests=[
                TokenCertificateSigningRequest(
                    id="16F2B5A9D76B790EE3DD7544152E333FC57F57FF",
                    owner_id=None,
                    possible_actions=[]
                )
            ],
            certificates=[],
            id="D1969303DB4B2CB5A5E0596CF6E4EA9E77D4C405",
            label="ss1-default-auth-key",
            name="ss1-default-auth-key",
            possible_actions=None,
            saved_to_configuration=True,
            usage=KeyUsageType.AUTHENTICATION
        )
    )


class TestToken(unittest.TestCase):
    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    ss_config = {
        'logging': [{'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'}],
        'api-key': [{'url': 'https://localhost:4000/api/v1/api-keys',
                     'key': 'private key',
                     'roles': 'XROAD_SYSTEM_ADMINISTRATOR'}],
        'security-server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'configuration_anchor': configuration_anchor,
              'owner_dn_country': 'FI',
              'owner_dn_org': 'UNSERE',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122'}]}

    def test_token_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_tokens',
                            return_value=TokenTestData.token_list_response):
                token_controller = TokenController()
                token_controller.app = app
                token_controller.load_config = (lambda: self.ss_config)
                token_controller.list()

    def test_token_login(self):
        with mock.patch('xrdsst.api.tokens_api.TokensApi.login_token',
                        return_value=TokenTestData.token_login_response):
            token_controller = TokenController()
            token_controller.load_config = (lambda: self.ss_config)
            token_controller.login()

    def test_token_init_keys(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.certificate_authorities_api.CertificateAuthoritiesApi.get_approved_certificate_authorities') as mock_get_cas:
                mock_get_cas.return_value.__enter__.return_value = TokenTestData.ca_list_response
                with mock.patch(
                        'xrdsst.api.security_servers_api.SecurityServersApi.get_security_servers',
                        return_value=TokenTestData.security_servers_current_server_response):
                    with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                                    return_value=TokenTestData.token_login_response):
                        with mock.patch('xrdsst.api.tokens_api.TokensApi.add_key_and_csr',
                                        return_value=TokenTestData.add_key_with_csr_response):
                            token_controller = TokenController()
                            token_controller.app = app
                            token_controller.load_config = (lambda: self.ss_config)
                            token_controller.init_keys()

    def test_token_init_keys_without_cas_available(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.certificate_authorities_api.CertificateAuthoritiesApi.get_approved_certificate_authorities') as mock_get_cas:
                mock_get_cas.return_value.__enter__.return_value = []
                with mock.patch(
                        'xrdsst.api.security_servers_api.SecurityServersApi.get_security_servers',
                        return_value=TokenTestData.security_servers_current_server_response):
                    token_controller = TokenController()
                    token_controller.app = app
                    token_controller.load_config = (lambda: self.ss_config)
                    self.assertRaises(IndexError, lambda: token_controller.init_keys())

    def test_token_list_nonresolving_url(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.ss_config)
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: token_controller.list())

    def test_token_login_nonresolving_url(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.ss_config)
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: token_controller.login())

    def test_token_init_keys_nonresolving_url(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.ss_config)
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: token_controller.init_keys())
