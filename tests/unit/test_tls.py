import copy
import os
import unittest
from unittest import mock
import pytest
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.controllers.tls import TlsController
from xrdsst.main import XRDSSTTest
from argparse import Namespace
import sys

class TestTls(unittest.TestCase):
    authcert_existing = os.path.join(ROOT_DIR, "tests/resources/authcert.pem")
    ss_config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'logging': {'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'},
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'certificates': [
                  '/some/where/authcert',
                  '/some/where/signcert',
              ],
              'api_key': 'TOOLKIT_SS1_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_dn_country': 'FI',
              'owner_dn_org': 'UNSERE',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122',
              },
             {'name': 'ssY',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'certificates': [
                  '/some/where/authcert',
                  '/some/where/signcert',
              ],
              'api_key': 'TOOLKIT_SS2_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_dn_country': 'FI',
              'owner_dn_org': 'UNSERE',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122',
              }
             ]}

    def ss_config_with_authcert(self):
        config = copy.deepcopy(self.ss_config)
        config['security_server'][0]['certificates'] = [self.authcert_existing]
        return config

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_internal_tls_download(self):
        class MockTls:
            def __init__(self, status, data):
                self.status = status
                self.data = data

        def mocked_download_tls(self, **kwargs):
            return MockTls(
                200,
                b'0\x82\x02\x890\x82\x01q\x02\x01\x000D1\x0b0\t\x06\x03U\x04\x06\x13\x02FI1\x0c0\n\x06\x03U\x04\n\x0c\x03UNS1\x180\x16\x06\x03U\x04\x05\x13\x0fDEV/UNS-SS5/GOV1\r0\x0b\x06\x03U\x04\x03\x0c\x0498760\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\xb3\x18w\xd4P\x16%\x9d\xc5\x0b\xc2m\x82-l\x1a\xc9\x90\x1b-\xa2\xa1f}\x86\x11AW\xca\xdf\xfb\xd9P\x93N\xcf\xaa\xa9[#\x10\x12\xe3\x1b\x07\n\xc2#9t\x8d\xda"\xb4\x93\xf7\xa9\xde;\x98\xf1,\xef\x89S\xb7\xad\xab\x00\xbbwm\xffr\x19\xb1d\xdf/\xe2\xa1\x14\xd3\xa8\xbf\xfe\xa5:\xab,\xab\xd0\x01\x813}\xe5\xe2\x12)y\xc6\x9d\xea\x96\xbe\xb2\xa81\x99\xdc/Z\x12\xe2\xfdZ&OB\xed\xf3\x8f\xbc\xca\x92lL\x1eJt\xe5\x7f\xbd\xe5\x83W\x19\x95\x9d\x8fv\xac\xdb\x03V1\xff\x80\xaf\xb1Qs\x97O\xd7\x98\x966\xf4\xb3\xff\xfaA6\xf6\xd6\xd6\x9b\xcf\xb2\x94\xb0\xbc\xb9\xf2\\\xfcct\x12`\x8e\xebh8\xc7\xf1 \x93\xd01D\xc1\xc6\xb8\xc4\xf6^\xb5\xa8\xe3\x87~^\xea\x812\x85\xf7\xd7\x99\xd2\xd4\x06\xadvo\xd7\x8ea\xbb\x16\x08\x9c\xc9\x15|;\xacl\xf4\xb7\x88\x9e\x9c\xd2.k\xda\xa4K\xd8\xea\xcf\xac\x8a)\x8dm\x9d#\xad\xd7\xe7-\x02\x03\x01\x00\x01\xa0\x000\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x003!\xa0M\x9bC\xa9\xe5\x8c\x86G\xcf\xc4\xee\xeaoW\x96\xd9\x8e\xd2\nz2\x05\xb7\xaa\xf3\xe0Vi\xf3\x0c\xc4\x1ay\x9eU \x12\xbf\xaen\x88\x04D0O\x19BJy\x88\xd6\xf7\x95w\x9a\x04w\xf4XQz\xceg2\x96\xc1\xdf\xbas\xf8\xb3\xd5~&\xc7:\'\x83}6\x0b\xddE\x15l\xd3H7\x8c6J\x9cf\x0f\xa6y\x7f\xab\xef"\'\xa4\xca\xf4\xf9\xd0\xddf\xf1\xdd4\x10\xe9\xf1;g\x08=\xd1\x17\xabva\xd6\xdb%\x19\xe1*mA\xca\xcc\xa7\x07m\xeb&k\xcaB\xa5\xb8\x93\x11]\xe9x\xcd\xa4\x90\x80\xb2\x9d\x91\x8d\x92}\xca\xd5,\xc8\x7f\x8dT\xa1h\x92\x8bv\x1c\xb8\x17\x7f\xe2\xa3\xdaL\x02<D8\xe4\xd1\xc5bYW\xa5_\nEl}\x93U\x96\t$\\yr6\x0f\x88\xe4\xd8\x96\x81\xe1A\x1f\xe7\x02\x9a\xa6\x19\xff\xdc\x8e\x95\x9e\x89kLAN\xcf\xf4n\x15\xb2\x99\xf5v\xd9\x89\xb7v4$\xce\xf1\xdapr\xd1\x16\x18\x84C\xb3\x1c'
            )

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.download_system_certificate', new=mocked_download_tls):
                tls_controller = TlsController()
                tls_controller.app = app
                tls_controller.load_config = (lambda: self.ss_config)

                # cert_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                reported_downloads = tls_controller.download()

                assert len(reported_downloads) == 2
                assert reported_downloads[0].security_server.count("ssX") == 1
                assert reported_downloads[1].security_server.count("ssY") == 1

                assert tls_controller.app._last_rendered[1].count('ssY') == 2
                # Check file creation
                ssY_cert = list(filter(lambda s: s.count('ssY') > 0, map(lambda s: s.strip(), tls_controller.app._last_rendered[1].split('│')))).pop()

                assert ssY_cert == reported_downloads[1].fs_loc
                assert os.path.exists(ssY_cert)

    def test_generate_new_tls_key(self):
        with XRDSSTTest() as app:
            ss_name = 'ssX'
            app._parsed_args = Namespace(ss=ss_name)
            with mock.patch('xrdsst.api.system_api.SystemApi.generate_system_tls_key_and_certificate',
                            return_value={}):
                tls_controller = TlsController()
                tls_controller.app = app
                tls_controller.load_config = (lambda: self.ss_config)
                tls_controller.generate_key()

                out, err = self.capsys.readouterr()
                assert out.count("Generated TLS key and certificate for security server: '%s'" % ss_name) > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)