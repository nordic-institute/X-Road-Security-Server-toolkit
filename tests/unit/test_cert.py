import copy
import os
import sys
import unittest
from datetime import datetime
from unittest import mock

import pytest
from dateutil.tz import tzutc

from definitions import ROOT_DIR
from tests.util.test_util import TokenTestData, StatusTestData
from xrdsst.controllers.cert import CertController
from xrdsst.models import Token, TokenStatus, TokenType, KeyUsageType, Key, TokenCertificate, CertificateOcspStatus, \
    CertificateStatus, CertificateDetails, KeyUsage, PossibleAction, TokenCertificateSigningRequest
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
            subject_alternative_names=''
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
            rsa_public_key_exponent=65537,
            hash="E1A9054439514C2ABBDE3CFC4107BD9429487756",
            key_usages=[KeyUsage.DIGITAL_SIGNATURE, KeyUsage.KEY_ENCIPHERMENT, KeyUsage.DATA_ENCIPHERMENT, KeyUsage.KEY_AGREEMENT],
            subject_alternative_names=''
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

    token_with_two_csrs_response = Token(
        available=True,
        id=0,
        logged_in=True,
        name='softToken-0',
        possible_actions=[PossibleAction.LOGOUT, PossibleAction.GENERATE_KEY, PossibleAction.EDIT_FRIENDLY_NAME],
        read_only=False,
        saved_to_configuration=True,
        serial_number=None,
        status=TokenStatus.OK,
        token_infos=[{'key': 'Type'}, {'value': 'Software'}],
        type=TokenType.SOFTWARE,

        keys=[Key(
                id='4209807ADA8CF6824CF741FFCEC56855827510B2',
                available=True,
                label='ssX-default-auth-key',
                name='ssX-default-auth-key',
                saved_to_configuration=True,
                usage=KeyUsageType.AUTHENTICATION,
                certificate_signing_requests=[
                    TokenCertificateSigningRequest(
                        id='6766344A138328780CE721979868EAD7981B3BD5',
                        possible_actions=[PossibleAction.DELETE]
                    )
                ],
                certificates=[],
                possible_actions=[PossibleAction.DELETE, PossibleAction.EDIT_FRIENDLY_NAME, PossibleAction.GENERATE_AUTH_CSR]
            ),
            Key(
                id='EC866CE2587F2660BBFCA20C6369E3B178DE3E2B',
                available=True,
                label='ssX-default-sign-key',
                name='ssX-default-sign-key',
                saved_to_configuration=True,
                usage=KeyUsageType.SIGNING,
                certificate_signing_requests=[
                    TokenCertificateSigningRequest(
                        id='1A8E6C45A9D3FDF3BF17769FC0650AA40EFC2CD5',
                        owner_id="DEV:GOV:9876",
                        possible_actions=[PossibleAction.DELETE],
                    )
                ],
                certificates=[]
            )
        ]
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
        'admin_credentials': 'user:pass',
        'logging': [{'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'}],
        'ssh_access': [{'user': 'user', 'private_key': 'key'}],
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'certificates': [
                  '/some/where/authcert',
                  '/some/where/signcert',
              ],
              'api_key': 'X-Road-apikey token=88888888-8000-4000-a000-727272727272',
              'api_key_roles': ['XROAD_SYSTEM_ADMINISTRATOR'],
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
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

    def test_csr_download(self):
        class MockCsr:
            def __init__(self, status, data):
                self.status = status
                self.data = data

        def mocked_download_csr(self, id, csr_id, **kwargs):
            if csr_id == '6766344A138328780CE721979868EAD7981B3BD5':  # auth
                return MockCsr(
                    200,
                    b'0\x82\x02\x890\x82\x01q\x02\x01\x000D1\x0b0\t\x06\x03U\x04\x06\x13\x02FI1\x0c0\n\x06\x03U\x04\n\x0c\x03UNS1\x180\x16\x06\x03U\x04\x05\x13\x0fDEV/UNS-SS5/GOV1\r0\x0b\x06\x03U\x04\x03\x0c\x0498760\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\xb3\x18w\xd4P\x16%\x9d\xc5\x0b\xc2m\x82-l\x1a\xc9\x90\x1b-\xa2\xa1f}\x86\x11AW\xca\xdf\xfb\xd9P\x93N\xcf\xaa\xa9[#\x10\x12\xe3\x1b\x07\n\xc2#9t\x8d\xda"\xb4\x93\xf7\xa9\xde;\x98\xf1,\xef\x89S\xb7\xad\xab\x00\xbbwm\xffr\x19\xb1d\xdf/\xe2\xa1\x14\xd3\xa8\xbf\xfe\xa5:\xab,\xab\xd0\x01\x813}\xe5\xe2\x12)y\xc6\x9d\xea\x96\xbe\xb2\xa81\x99\xdc/Z\x12\xe2\xfdZ&OB\xed\xf3\x8f\xbc\xca\x92lL\x1eJt\xe5\x7f\xbd\xe5\x83W\x19\x95\x9d\x8fv\xac\xdb\x03V1\xff\x80\xaf\xb1Qs\x97O\xd7\x98\x966\xf4\xb3\xff\xfaA6\xf6\xd6\xd6\x9b\xcf\xb2\x94\xb0\xbc\xb9\xf2\\\xfcct\x12`\x8e\xebh8\xc7\xf1 \x93\xd01D\xc1\xc6\xb8\xc4\xf6^\xb5\xa8\xe3\x87~^\xea\x812\x85\xf7\xd7\x99\xd2\xd4\x06\xadvo\xd7\x8ea\xbb\x16\x08\x9c\xc9\x15|;\xacl\xf4\xb7\x88\x9e\x9c\xd2.k\xda\xa4K\xd8\xea\xcf\xac\x8a)\x8dm\x9d#\xad\xd7\xe7-\x02\x03\x01\x00\x01\xa0\x000\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x003!\xa0M\x9bC\xa9\xe5\x8c\x86G\xcf\xc4\xee\xeaoW\x96\xd9\x8e\xd2\nz2\x05\xb7\xaa\xf3\xe0Vi\xf3\x0c\xc4\x1ay\x9eU \x12\xbf\xaen\x88\x04D0O\x19BJy\x88\xd6\xf7\x95w\x9a\x04w\xf4XQz\xceg2\x96\xc1\xdf\xbas\xf8\xb3\xd5~&\xc7:\'\x83}6\x0b\xddE\x15l\xd3H7\x8c6J\x9cf\x0f\xa6y\x7f\xab\xef"\'\xa4\xca\xf4\xf9\xd0\xddf\xf1\xdd4\x10\xe9\xf1;g\x08=\xd1\x17\xabva\xd6\xdb%\x19\xe1*mA\xca\xcc\xa7\x07m\xeb&k\xcaB\xa5\xb8\x93\x11]\xe9x\xcd\xa4\x90\x80\xb2\x9d\x91\x8d\x92}\xca\xd5,\xc8\x7f\x8dT\xa1h\x92\x8bv\x1c\xb8\x17\x7f\xe2\xa3\xdaL\x02<D8\xe4\xd1\xc5bYW\xa5_\nEl}\x93U\x96\t$\\yr6\x0f\x88\xe4\xd8\x96\x81\xe1A\x1f\xe7\x02\x9a\xa6\x19\xff\xdc\x8e\x95\x9e\x89kLAN\xcf\xf4n\x15\xb2\x99\xf5v\xd9\x89\xb7v4$\xce\xf1\xdapr\xd1\x16\x18\x84C\xb3\x1c'
                )

            if csr_id == '1A8E6C45A9D3FDF3BF17769FC0650AA40EFC2CD5':  # sign
                return MockCsr(
                    200,
                    b'0\x82\x02\x890\x82\x01q\x02\x01\x000D1\x0b0\t\x06\x03U\x04\x06\x13\x02FI1\x0c0\n\x06\x03U\x04\n\x0c\x03UNS1\x180\x16\x06\x03U\x04\x05\x13\x0fDEV/UNS-SS5/GOV1\r0\x0b\x06\x03U\x04\x03\x0c\x0498760\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\x9a\x07\x9e\xbe:\x03T\x94\xd3\xbb\x15\x14\xf5>\xa3\x145\x9d\xc8m\x12\x9d\xd3n1\xd9t\x0bw\x0e\xc0x\xa79C\xa2\xe7\xb2\x94\xf6\xbbY\xbc\xe7\xb5\xa7\xc1\xe70\xc5\x91\x87\xbfE\xe1\xec`\x1fR\xbaP\xc3\xb6o\x94*\xa1j\x05\xf3Q*\xfb6\xd3\x1c,g\xd2b\x9f=B\xc8\xa1\x8e\xafya`\x84\xf4\x9c\x14\x13\xc7\xb7\xc1\xa7\x83p\xedq\xa1\x93H\xe8\xfc\x007M{\x91\xc0X\xf4\x94$n\xe3\xfb8\xed\xe2\xed\xad\t\xf8\x1a3B\xc0V\xeb\x07@\xf4 \xafl\n\xdbI\x8a,\x06.\xfdz\xa7\x98$Z%\xc0\xfc\x1d\xe5Q\xdb\xd2\xc4\x9a\xc4\xbdn\x9cxx(\xbc2\xe8Vhm\x14\x06\xd1\xa9&T\x806x\x0fD\xd8~\xe8\x90lg\x1b\x86\x91\xdb\xb1\x109\xb1;(}\xb6\x96\xbb\x1d]\xb9n+<i\x87\xcc\xa9[\x05\xd5\xca\x9c\xe0\xcc\xf9\xf4\xad\xf6{\xee\xb1\xb2\x04Cx*\xb6d9\xce\x9c-d\x98\xc7\xbf\xe8:\xb2fG\xf5N\x8e\n\xcd\x02\x03\x01\x00\x01\xa0\x000\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x00\x8c\x95\xe3\xe3h\xdf\x9a\x11\x8dA\xa8r1\x82\xc7\x05j(z\xdd!,j\xae\x92\xd5\xe5\x8f\x00\xffn\x0f\xa4\x17\xfb\xfc\x04\x88\xf5\x96Y\xdb\xf3ss/%\xfeX\xbc%`QD\xa9 5W\xf2IX\x00\xfa~5\xfb\xd1\x9drn\xf6\xf1J\x99qE\xf6\xf3<\xe97\xc7\xebQ\xdb,j}\x07\xd7T\xea\x05\xdd\xda{e=k\xd0gJ\x07\x84`\xc3E\xbf>:Uk\xcan;g\xc0\xf1\xdf\x81\x94\xd22~\xde\x97\x13\x85\xc8aY\xdc\x1a\x1f\xe4Qg\xb9-\xfc\x15S\xbc\xeb\xe9\xbf\x18\xdbr\x8dD\xc6\xb9F\xd0\x94\xa8\xf8\xd9\xcc5K\x9c$\x8a?\xc7\x0b\xae\x86\x0e\x04R\x19\x0c9\xb0;t\xec(\xf6\'\xe1\x9fky9\xb2\xe1\xd6\xd3\xfc\xdd\xd1\xbf%\xb4(?\xde]\xf7\xd4o`O\xf4\x99v,@\xb5\xb2.\xc0\xae\x97\n\xd2\xa5\xc6\xa2\x98\x14ZA\xdeJK\xfe\xb1\xf6\n\xad\xea\x8fq\xa3\xf3*=)\x04\xc9\x84sK\xa0%!\x07\xba\xa0\xf6\x94'
                )

            raise Exception("No mock for CSR '" + csr_id + "'")

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.token_with_two_csrs_response):
                with mock.patch('xrdsst.api.keys_api.KeysApi.download_csr', new=mocked_download_csr):
                    cert_controller = CertController()
                    cert_controller.app = app
                    cert_controller.load_config = (lambda: self.ss_config)
                    cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    reported_downloads = cert_controller.download_csrs()

                    assert len(reported_downloads) == 2

                    assert cert_controller.app._last_rendered[1].count('ssX-auth') == 1
                    assert cert_controller.app._last_rendered[1].count('ssX-sign') == 1
                    # Check file creation
                    auth_csr_file = list(filter(lambda s: s.count('ssX-auth') > 0,
                                                map(lambda s: s.strip(), cert_controller.app._last_rendered[1].split('│')))).pop()
                    sign_csr_file = list(filter(lambda s: s.count('ssX-sign') > 0,
                                                map(lambda s: s.strip(), cert_controller.app._last_rendered[1].split('│')))).pop()
                    assert auth_csr_file == reported_downloads[0].fs_loc or auth_csr_file == reported_downloads[1].fs_loc
                    assert sign_csr_file == reported_downloads[0].fs_loc or auth_csr_file == reported_downloads[1].fs_loc
                    assert auth_csr_file != sign_csr_file
                    assert os.path.exists(auth_csr_file)
                    assert os.path.exists(sign_csr_file)

    def test_cert_import_nonexisting_certs(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.ss_config)
            cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
            cert_controller.import_()

            out, err = self.capsys.readouterr()
            assert out.count("references non-existent file") > 0

            with self.capsys.disabled():
                sys.stdout.write(out)
                sys.stderr.write(err)

    @mock.patch('xrdsst.core.api_util.is_ss_connectable', lambda x: (False, 'connection error (test injected)'))
    def test_cert_import_nonresolving_url(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.ss_config_with_authcert())
            cert_controller.import_()

            out, err = self.capsys.readouterr()
            assert out.count("SKIPPED 'ssX': no connectivity") > 0

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
                    cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    cert_controller.import_()

                    out, err = self.capsys.readouterr()
                    assert out.count("already imported") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_cert_import_permission_denied(self):
        class PermissionDeniedResponse:
            status = 403
            data = '{"status":403,"error":{"code":"permission_denied"}}'
            reason = None
            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=CertTestData.single_auth_key_with_cert_token_response):
                with mock.patch('xrdsst.api.token_certificates_api.TokenCertificatesApi.import_certificate',
                                side_effect=ApiException(http_resp=PermissionDeniedResponse())):
                    cert_controller = CertController()
                    cert_controller.app = app
                    cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                    cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    cert_controller.import_()

                    out, err = self.capsys.readouterr()
                    assert err.count("permission") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    @mock.patch('xrdsst.core.api_util.is_ss_connectable', lambda x: (False, 'connection error (test injected)'))
    def test_cert_register_nonresolving_url(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.ss_config)
            cert_controller.register()

            out, err = self.capsys.readouterr()
            assert out.count("SKIPPED 'ssX': no connectivity") > 0

    def test_cert_register_no_auth_key(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.tokens_api.TokensApi.get_token',
                            return_value=TokenTestData.token_keyless):
                cert_controller = CertController()
                cert_controller.app = app
                cert_controller.load_config = (lambda: self.ss_config_with_authcert())
                cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
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
                cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
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
                cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
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
                cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
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
                        cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        cert_controller.activate()

                        out, err = self.capsys.readouterr()
                        assert out.count("Activated certificate") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)
