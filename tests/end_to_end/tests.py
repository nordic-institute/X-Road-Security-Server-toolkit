import os
import sys
import unittest
import urllib3

from tests.util.test_util import find_test_ca_sign_url, perform_test_ca_sign, waitfor, auth_cert_registration_global_configuration_update_received
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest


class EndToEndTest(unittest.TestCase):
    config_file = None
    config = None
    max_retries = 300
    retry_wait = 1  # in seconds

    def setUp(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        idx = 0
        for arg in sys.argv:
            idx += 1
            if arg == "-c":
                self.config_file = sys.argv[idx]

    def tearDown(self):
        if self.config_file is not None:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)

    def step_init(self):
        base = BaseController()
        init = InitServerController()
        self.config = base.load_config(baseconfig=self.config_file)
        for security_server in self.config["security_server"]:
            configuration = init.initialize_basic_config_values(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False and status.is_server_code_initialized is False
            init.initialize_server(self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is True and status.is_server_code_initialized is True

    def step_timestamp_init(self):
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = timestamp_controller.initialize_basic_config_values(security_server, self.config)
                response = timestamp_controller.remote_get_configured(configuration)
                assert response == []
                timestamp_controller.remote_timestamp_service_init(configuration, security_server)
                response = timestamp_controller.remote_get_configured(configuration)
                assert len(response) > 0
                assert len(response[0].name) > 0
                assert len(response[0].url) > 0

    def step_token_login(self):
        token_controller = TokenController()
        for security_server in self.config["security_server"]:
            configuration = token_controller.initialize_basic_config_values(security_server, self.config)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert response[0].logged_in is False
            token_controller.remote_token_login(configuration, security_server)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert response[0].logged_in is True

    def step_token_init_keys(self):
        token_controller = TokenController()
        for security_server in self.config["security_server"]:
            configuration = token_controller.initialize_basic_config_values(security_server, self.config)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert len(response[0].keys) == 0
            token_controller.remote_token_add_keys_with_csrs(configuration, security_server)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert len(response[0].keys) == 2
            auth_key_label = security_server['name'] + '-default-auth-key'
            sign_key_label = security_server['name'] + '-default-sign-key'
            assert str(response[0].keys[0].label) == auth_key_label
            assert str(response[0].keys[1].label) == sign_key_label

    def step_cert_download_csrs(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            result = cert_controller.download_csrs()
            assert len(result) == 2
            assert result[0].fs_loc != result[1].fs_loc

            return [
                ('sign', next(csr.fs_loc for csr in result if csr.key_type == 'SIGN')),
                ('auth', next(csr.fs_loc for csr in result if csr.key_type == 'AUTH')),
            ]

    def step_acquire_certs(self, downloaded_csrs):
        tca_sign_url = find_test_ca_sign_url(self.config['security_server'][0]['configuration_anchor'])
        cert_files = []
        for down_csr in downloaded_csrs:
            cert = perform_test_ca_sign(tca_sign_url, down_csr[1], down_csr[0])
            cert_file = down_csr[1] + ".signed.pem"
            cert_files.append(cert_file)
            with open(cert_file, "w") as out_cert:
                out_cert.write(cert)

        return cert_files

    def apply_cert_config(self, signed_certs):
        self.config['security_server'][0]['certificates'] = signed_certs

    def step_cert_import(self):
        cert_controller = CertController()
        for security_server in self.config["security_server"]:
            configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
            response = cert_controller.remote_import_certificates(configuration, security_server)
            assert len(response) > 0

    def step_cert_register(self):
        cert_controller = CertController()
        for security_server in self.config["security_server"]:
            configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
            response = cert_controller.remote_register_certificate(configuration, security_server)
            assert len(response) > 0

    def step_cert_activate(self):
        cert_controller = CertController()
        for security_server in self.config["security_server"]:
            configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
            response = cert_controller.remote_activate_certificate(configuration, security_server)
            assert len(response) > 0
            assert 'ACTIVATE' in response

    def step_subsystem_add_client(self):
        client_controller = ClientController()
        for security_server in self.config["security_server"]:
            configuration = client_controller.initialize_basic_config_values(security_server, self.config)
            for client in security_server["clients"]:
                response = client_controller.remote_add_client(configuration, client)
                assert len(response) > 0

    def step_subsystem_register(self):
        client_controller = ClientController()
        for security_server in self.config["security_server"]:
            configuration = client_controller.initialize_basic_config_values(security_server, self.config)
            for client in security_server["clients"]:
                response = client_controller.remote_register_client(configuration, security_server, client)
                assert len(response) > 0

    def test_run_configuration(self):
        self.step_init()
        self.step_timestamp_init()
        self.step_token_login()
        self.step_token_init_keys()

        downloaded_csrs = self.step_cert_download_csrs()
        signed_certs = self.step_acquire_certs(downloaded_csrs)
        self.apply_cert_config(signed_certs)
        self.step_cert_import()
        self.step_cert_register()
        self.step_cert_activate()

        # Wait for global configuration status updates
        waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config), self.retry_wait, self.max_retries)

        # subsystems
        self.step_subsystem_add_client()
        self.step_subsystem_register()
