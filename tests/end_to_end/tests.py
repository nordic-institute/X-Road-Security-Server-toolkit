import os
import subprocess
import sys
import time
import unittest
from unittest import mock

import urllib3

from tests.util.test_util import find_test_ca_sign_url, perform_test_ca_sign, get_client, get_service_description, \
    assert_server_statuses_transitioned
from xrdsst.controllers.auto import AutoController
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import StatusController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest


class EndToEndTest(unittest.TestCase):
    config_file = None
    config = None

    def setUp(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        idx = 0
        for arg in sys.argv:
            idx += 1
            if arg == "-c":
                self.config_file = sys.argv[idx]
        base = BaseController()
        self.config = base.load_config(baseconfig=self.config_file)
        for security_server in self.config["security_server"]:
            api_key = base.get_api_key(self.config, security_server)
            self.create_api_key(api_key)

    def tearDown(self):
        self.revoke_api_key()
        if self.config_file is not None:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)

    def step_init(self):
        init = InitServerController()
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
            for security_server in self.config["security_server"]:
                ss_configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
                result = cert_controller.remote_download_csrs(ss_configuration, security_server)
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

    def create_api_key(self, api_key):
        self.config["security_server"][0]["api_key"] = api_key

    def revoke_api_key(self):
        base = BaseController()
        curl_cmd = "curl -X DELETE -u " + self.config["api_key"][0]["credentials"] + " --silent " + \
                   self.config["api_key"][0]["url"] + "/" + str(base.api_key_id[self.config["security_server"][0]['name']]) + " -k"
        cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
              self.config["api_key"][0]["key"] + "\" root@" + self.config["security_server"][0]["name"] + " \"" + curl_cmd + "\""
        subprocess.run(cmd, shell=True, check=False, capture_output=True)

    def step_cert_import(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
                cert_controller.remote_import_certificates(configuration, security_server)

    def step_cert_register(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
                cert_controller.remote_register_certificate(configuration, security_server)

    def step_cert_activate(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.initialize_basic_config_values(security_server, self.config)
                cert_controller.remote_activate_certificate(configuration, security_server)

    def step_subsystem_add_client(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = client_controller.initialize_basic_config_values(security_server, self.config)
                for client in security_server["clients"]:
                    client_controller.remote_add_client(configuration, client)

    def step_subsystem_register(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = client_controller.initialize_basic_config_values(security_server, self.config)
                for client in security_server["clients"]:
                    client_controller.remote_register_client(configuration, security_server, client)

    def step_add_service_description(self, client_id):
        service_controller = ServiceController()
        for security_server in self.config["security_server"]:
            configuration = service_controller.initialize_basic_config_values(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    service_controller.remote_add_service_description(configuration, security_server, client, service_description)
        description = get_service_description(self.config, client_id)
        assert description["disabled"] is True

    def step_enable_service_description(self, client_id):
        service_controller = ServiceController()
        for security_server in self.config["security_server"]:
            configuration = service_controller.initialize_basic_config_values(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    service_controller.remote_enable_service_description(configuration, security_server, client, service_description)
        description = get_service_description(self.config, client_id)
        assert description["disabled"] is False

    def step_autoconf(self):
        with XRDSSTTest() as app:
            with mock.patch.object(BaseController, 'load_config',  (lambda x, y=None: self.config)):
                auto_controller = AutoController()
                auto_controller.app = app
                auto_controller._default()

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

    def test_run_configuration(self):
        unconfigured_servers_at_start = self.query_status()

        self.step_init()
        self.step_timestamp_init()
        self.step_token_login()
        self.step_token_init_keys()
        downloaded_csrs = self.step_cert_download_csrs()
        signed_certs = self.step_acquire_certs(downloaded_csrs)
        self.apply_cert_config(signed_certs)
        self.step_cert_import()
        self.step_cert_import()
        self.step_cert_register()
        self.step_cert_activate()

        # Wait for global configuration status updates
        time.sleep(120)

        self.step_subsystem_add_client()
        self.step_subsystem_register()
        client = get_client(self.config)
        client_id = client['id']

        self.step_add_service_description(client_id)
        self.step_enable_service_description(client_id)
        self.step_autoconf()  # Idempotent

        configured_servers_at_end = self.query_status()

        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)
