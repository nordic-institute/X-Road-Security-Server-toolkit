import copy
import os
import sys
import unittest
from datetime import datetime
from unittest import mock

import pytest
import urllib3
from dateutil.tz import tzutc

from definitions import ROOT_DIR
from xrdsst.controllers.cert import CertController
from xrdsst.models import Token, TokenStatus, TokenType, KeyUsageType, Key, TokenCertificate, CertificateOcspStatus, \
    CertificateStatus, CertificateDetails, KeyUsage, PossibleAction
from xrdsst.main import XRDSSTTest
from xrdsst.rest.rest import ApiException


class CertTestData:
    single_cert = TokenCertificate(
        active=False,
        ocsp_status=CertificateOcspStatus.DISABLED,
        saved_to_configuration=True,
        status=CertificateStatus.REGISTRATION_IN_PROGRESS,
        possible_actions=[PossibleAction.ACTIVATE, PossibleAction.UNREGISTER],
        certificate_details=CertificateDetails(
            hash='D1D0A8699703CF164A9DBE8099CB0EEEBA4FF1BD',
            issuer_common_name='Test CA',
            issuer_distinguished_name='CN=Test CA, O=X-Road Test CA',
            subject_common_name='',
            subject_distinguished_name='',
            key_usages=[KeyUsage.KEY_AGREEMENT, KeyUsage.DATA_ENCIPHERMENT],
            not_after=datetime(2099, 10, 31, 22, 24, 45, tzinfo=tzutc()),
            not_before=datetime(2020, 11, 5, 22, 24, 45, tzinfo=tzutc()),
            public_key_algorithm='RSA',
            rsa_public_key_exponent=65537,
            rsa_public_key_modulus=214432,  # Not even a prime, but fine ATM
            signature='30eb0bde826774031726',
            signature_algorithm='SHA256withRSA',
            serial=5,
            version=3,
        )
    )

    single_registrable_auth_cert = TokenCertificate(
        active=False,
        ocsp_status=CertificateOcspStatus.DISABLED,
        saved_to_configuration=True,
        certificate_details=CertificateDetails(
            issuer_distinguished_name="CN=Test CA, O=X-Road Test CA",
            issuer_common_name="Test CA",
            subject_distinguished_name="SERIALNUMBER=DEV/UNS-SSX/GOV, CN=ssX, O=UNS, C=FI",
            subject_common_name="ssX",
            not_before=datetime(2020, 11, 5, 22, 24, 45, tzinfo=tzutc()),
            not_after=datetime(2099, 10, 31, 22, 24, 45, tzinfo=tzutc()),
            serial=12,
            version=3,
            signature_algorithm='SHA256withRSA',
            signature="0e33bd65218456beb755ec8dba09c1687d48ca24532a0e7ca9274bd283a5eea03c3cb40b65df347c94f790cf939e6fcceb0bf533eaf22bee65bfb4e9af76f4c96b2aa42622020196d7036d839e1e6eec0459c3bdbfb504bb45dd1433b6403698bd15c179262b72d19fcb1445f631b2e502ab195044688cbaba8284ce33d31b232acbb49034014de5a059c5617e2ddb4ae30eebe10e6140454c8b59f232d93dfff6c460bd4e3d9511684cb33b7698c3c6c714c3a8aa5019b6f732794675a286e829ed555f28de30b4663d0af80b11e1a18d37daaa8b74aa965627610930c6b89741c2624e72b65cbfb52df3c5cd1d8d1033748810e2f52731fb03a2097c5fdd5cd9c05eed9fa496fbb2290e68c0aa880d414fff44c732772b99ef7c83b2a5d9bf5b206df13b109469e0204a874be8181c1aeec4bf58f055540ee447846a50ae7cdc11808063958814c836be3cd709e67900ce4f7e40d51714a945ac3c7fcd37f701445d86c9317d0164b86c40608905505ca311ad1a498a307bb524b15c1a40099ca3a27631a5ad9b47b8be86c97d9bb9874785de2922179c522229bf3f2c4131da629cc739961cee79ec2409cb14956208d0f1b3ef5c5b09e81401347ecb6861afed37b073890d1cf6d5b4dc6fa458ff148571f197c577595ea675bb7feea43fffb02562fd6806c6b9325252a89f3dd7ff11c6ba4c41e618ebafb2cb747a934b",
            public_key_algorithm="RSA",
            rsa_public_key_modulus="bb18cb4aec60cddf8bcd33f360e27de7038a54332c4a708fff67ba97fffeeb1da70f8ea395f55acbde976eeea182f78a390e549f9780b2ba361663cdd0f643039cd0d320ee9e0ba3c9834bb46f5c91626efa16bc464c48483fae1960cbeea06104da2c2f60e875e96ef6443946806c9523ab0f8925abfb5ea3c51c2edd976a7f3257d3c4ff2409298080c55b9229e79d502f355a0144c99fcff8b00dd8c78007d771c2367b272e93019ecc422f8b4bd1f1f5008360026f4d1eafe0e64a171df5754e48552072f0f4d465e70f8d6f9ccfc60e0df316da84fa7f9be711ef74acbf8f2028223c70a102b75a51d6bc54039f561e08fc7c7834e26c21eba8888e229d",
            rsa_public_key_exponent= 65537,
            hash="E1A9054439514C2ABBDE3CFC4107BD9429487756",
            key_usages=[KeyUsage.DIGITAL_SIGNATURE, KeyUsage.KEY_ENCIPHERMENT, KeyUsage.DATA_ENCIPHERMENT, KeyUsage.KEY_AGREEMENT],
        ),
        status=CertificateStatus.SAVED,
        possible_actions=[PossibleAction.DELETE, PossibleAction.ACTIVATE, PossibleAction.REGISTER],
    )

    single_auth_key_with_cert = Key(
        id='D9DEE1CE125B72461D60DB4AB1ED0A547866B33D',
        available=True,
        label='ssX-default-auth-key',
        name='ssX-default-auth-key',
        saved_to_configuration=True,
        usage=KeyUsageType.AUTHENTICATION,
        certificate_signing_requests=[],
        certificates=[
            single_cert
        ]
    )

    single_auth_key_with_registrable_cert = Key(
        id='9F840E4C09C7812D703435155E41C3A4AD41D26A',
        available=True,
        label='ssX-default-auth-key',
        name='ssX-default-auth-key',
        saved_to_configuration=True,
        usage=KeyUsageType.AUTHENTICATION,
        certificate_signing_requests=[],
        certificates=[
            single_registrable_auth_cert
        ]
    )

    single_auth_key_with_two_registrable_certs = Key(
        id='9F840E4C09C7812D703435155E41C3A4AD41D26A',
        available=True,
        label='ssX-default-auth-key',
        name='ssX-default-auth-key',
        saved_to_configuration=True,
        usage=KeyUsageType.AUTHENTICATION,
        certificate_signing_requests=[],
        certificates=[
            single_registrable_auth_cert, single_registrable_auth_cert
        ]
    )

    single_auth_key_without_certs_or_csr1 = Key(
        id='D9DEE1CE125B72461D60DB4AB1ED0A547866B33D',
        available=True,
        label='ssX-default-auth-key',
        name='ssX-default-auth-key',
        saved_to_configuration=True,
        usage=KeyUsageType.AUTHENTICATION,
        certificate_signing_requests=[],
        certificates=[]
    )

    single_auth_key_without_certs_or_csr2 = Key(
        id='125B72D9DEE1CE461D60DB4AB1ED0A547866B33D',
        available=True,
        label='ssX-default-auth-key',
        name='ssX-default-auth-key',
        saved_to_configuration=True,
        usage=KeyUsageType.AUTHENTICATION,
        certificate_signing_requests=[],
        certificates=[]
    )

    keyless_token_response = Token(
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
        keys=[]
    )

    single_auth_key_without_certs_token_response = Token(
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
        keys=[single_auth_key_without_certs_or_csr1]
    )

    single_auth_key_with_cert_token_response = Token(
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
        keys=[single_auth_key_with_cert]
    )


    multiple_keys_labelled_as_auth_response = Token(
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
        keys=[single_auth_key_without_certs_or_csr1, single_auth_key_without_certs_or_csr2]
    )

    single_key_with_multiple_registrable_auth_cert_response = Token(
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
        keys=[single_auth_key_with_two_registrable_certs]
    )


class TestCert(unittest.TestCase):
    authcert_existing = os.path.join(ROOT_DIR, "tests/resources/authcert.pem")
    ss_config = {
        'logging': [{'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'}],
        'api_key': [{'url': 'https://localhost:4000/api/v1/api-keys',
                     'key': 'private key',
                     'credentials': 'user:pass',
                     'roles': 'XROAD_SYSTEM_ADMINISTRATOR'}],
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'certificates': [
                  '/some/where/authcert',
                  '/some/where/signcert',
              ],
              'api_key': 'X-Road-apikey token=api-key',
              'owner_dn_country': 'FI',
              'owner_dn_org': 'UNSERE',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122'}]}

    def ss_config_with_authcert(self):
        config = copy.deepcopy(self.ss_config)
        config['security_server'][0]['certificates'] = [self.authcert_existing]
        return config

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_cert_import_nonexisting_certs(self):
        cert_controller = CertController()
        cert_controller.load_config = (lambda: self.ss_config)
        cert_controller.import_()

        out, err = self.capsys.readouterr()
        assert out.count("does not exist") > 0

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

    def test_cert_import_nonresolving_url(self):
        cert_controller = CertController()
        cert_controller.load_config = (lambda: self.ss_config_with_authcert())
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: cert_controller.import_())

    def test_cert_import_already_existing(self):
        class AlreadyExistingResponse:
            status = 409
            data = '{"status":409,"error":{"code":"certificate_already_exists"}}'
            reason = None
            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.single_auth_key_with_cert_token_response):
                with mock.patch('xrdsst.api.token_certificates_api.TokenCertificatesApi.import_certificate',
                                side_effect=ApiException(http_resp=AlreadyExistingResponse())):
                    cert_controller = CertController()
                    cert_controller.app = app
                    cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                    cert_controller.import_()

                    out, err = self.capsys.readouterr()
                    assert out.count("already imported") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)


    def test_cert_register_nonresolving_url(self):
        cert_controller = CertController()
        cert_controller.load_config = (lambda: self.ss_config)
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: cert_controller.register())

    def test_cert_register_no_auth_key(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.keyless_token_response):
                cert_controller = CertController()
                cert_controller.app = app
                cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                cert_controller.register()

                out, err = self.capsys.readouterr()
                assert out.count("not found authentication key") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_cert_register_multiple_auth_labelled_keys(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.multiple_keys_labelled_as_auth_response):
                cert_controller = CertController()
                cert_controller.app = app
                cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                cert_controller.register()

                out, err = self.capsys.readouterr()
                assert out.count("multiple authentication keys") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_cert_register_no_certs_for_auth_key(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.single_auth_key_without_certs_token_response):
                cert_controller = CertController()
                cert_controller.app = app
                cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                cert_controller.register()

                out, err = self.capsys.readouterr()
                assert out.count("No certificates available for authentication key") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_cert_register_multiple_certs_for_auth_key(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.single_key_with_multiple_registrable_auth_cert_response):
                cert_controller = CertController()
                cert_controller.app = app
                cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                cert_controller.register()

                out, err = self.capsys.readouterr()
                assert out.count("Multiple certificates to 'REGISTER' for key") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_cert_activate(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.single_auth_key_with_cert_token_response):
                with mock.patch('xrdsst.api.token_certificates_api.TokenCertificatesApi.activate_certificate',
                                return_value={}):
                    with mock.patch('xrdsst.api.token_certificates_api.TokenCertificatesApi.get_possible_actions_for_certificate',
                                    return_value=[PossibleAction.DISABLE, PossibleAction.UNREGISTER]):
                        cert_controller = CertController()
                        cert_controller.app = app
                        cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                        cert_controller.activate()

                        out, err = self.capsys.readouterr()
                        assert out.count("Activated certificate") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)
