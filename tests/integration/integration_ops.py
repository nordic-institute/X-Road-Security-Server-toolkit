from unittest import mock

from tests.util.test_util import perform_test_ca_sign, find_test_ca_sign_url
from xrdsst.controllers.auto import AutoController
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.status import StatusController
from xrdsst.main import XRDSSTTest


class IntegrationOpBase:

    def step_cert_download_csrs(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            result = cert_controller.download_csrs()

            assert len(result) == 6

            fs_loc_list = []
            csrs = []
            for csr in result:
                fs_loc_list.append(csr.fs_loc)
                csrs.append((str(csr.key_type).lower(), csr.fs_loc))
            flag = len(set(fs_loc_list)) == len(fs_loc_list)

            assert flag is True

            return csrs

    @staticmethod
    def step_acquire_certs(downloaded_csrs, security_server):
        tca_sign_url = find_test_ca_sign_url(security_server['configuration_anchor'])
        cert_files = []
        for down_csr in downloaded_csrs:
            cert = perform_test_ca_sign(tca_sign_url, down_csr[1], down_csr[0])
            cert_file = down_csr[1] + ".signed.pem"
            cert_files.append(cert_file)
            with open(cert_file, "w") as out_cert:
                out_cert.write(cert)

        return cert_files

    def apply_cert_config(self, signed_certs, ssn):
        self.config['security_server'][ssn]['certificates'] = signed_certs

    def query_status(self):
        with XRDSSTTest() as app:
            status_controller = StatusController()
            status_controller.app = app
            status_controller.load_config = (lambda: self.config)

            servers = status_controller._default()

            # Must not throw exception, must produce output, test with global status only -- should be ALWAYS present
            # in the configuration that integration test will be run, even when it is still failing as security server
            # has only recently been started up.
            assert status_controller.app._last_rendered[0][1][0].count('LAST') == 1
            assert status_controller.app._last_rendered[0][1][0].count('NEXT') == 1

            return servers

    def step_autoconf(self):
        with XRDSSTTest() as app:
            with mock.patch.object(BaseController, 'load_config', (lambda x, y=None: self.config)):
                auto_controller = AutoController()
                auto_controller.app = app
                auto_controller._default()

    def step_cert_download_internal_tsl(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                result = cert_controller.remote_download_internal_tsl(configuration, security_server)
                assert len(result) == 1
