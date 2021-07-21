import os

from tests.util.test_util import getClientTlsCertificates, perform_test_ca_sign, find_test_ca_sign_url, waitfor, \
    auth_cert_registration_global_configuration_update_received
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.token import TokenController
from xrdsst.core.conf_keys import ConfKeysSecServerClients, ConfKeysSecurityServer
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.main import XRDSSTTest


class CertificateTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_cert_download_internal_tls(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                ss_configuration = cert_controller.create_api_config(security_server, self.test.config)
                result = cert_controller.remote_download_internal_tls(ss_configuration, security_server)
                assert len(result) == 1

    def step_import_tls_certificate(self):
        tls_certificate = "tests/resources/cert.pem"
        for security_server in self.test.config["security_server"]:
            security_server["tls_certificates"] = [os.path.join(ROOT_DIR, tls_certificate)]
            for client in security_server["clients"]:
                if "tls_certificates" in client:
                    client["tls_certificates"] = [os.path.join(ROOT_DIR, tls_certificate)]
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                client_conf = {
                    "member_name": security_server["owner_dn_org"],
                    "member_code": security_server["owner_member_code"],
                    "member_class": security_server["owner_member_class"]
                }
                client_controller.remote_import_tls_certificate(configuration, security_server["tls_certificates"], client_conf)

                if "clients" in security_server:
                    for client in security_server["clients"]:
                        if "tls_certificates" in client:
                            client_controller.remote_import_tls_certificate(configuration, client["tls_certificates"], client)
                            tls_certs = getClientTlsCertificates(self.test.config, client, ssn)
                            assert len(tls_certs) == 1
                ssn = ssn + 1

    def list_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)

            certificates = cert_controller.list()
            headers = [*certificates[0]]
            for header in headers:
                assert header in cert_controller.app._last_rendered[0][0]

            assert len(certificates) == 6
            assert len(cert_controller.app._last_rendered[0]) == 7

    def step_cert_import_fail_certificates_missing(self):
        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["certificates"] = ''

        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                response = cert_controller.remote_import_certificates(configuration, security_server)
                assert len(response) == 0

    def step_cert_register_fail_certificates_not_imported(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                cert_controller.remote_register_certificate(configuration, security_server)

    def step_cert_import(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                response = cert_controller.remote_import_certificates(configuration, security_server)
                assert len(response) > 0

    def step_cert_register(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                cert_controller.remote_register_certificate(configuration, security_server)

    def step_cert_activate(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                cert_controller.remote_activate_certificate(configuration, security_server)

    def step_token_init_keys(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.test.config)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert len(response[0].keys) == 0
                member_class = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS]
                member_code = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE]
                member_name = security_server[ConfKeysSecurityServer.CONF_KEY_DN_ORG]

                auth_key_label = security_server['name'] + '-default-auth-key'
                sign_key_label = security_server['name'] + '-default-sign-key'
                token_controller.remote_token_add_all_keys_with_csrs(configuration,
                                                                     security_server,
                                                                     member_class,
                                                                     member_code,
                                                                     member_name,
                                                                     auth_key_label,
                                                                     sign_key_label)
                for client in security_server["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE not in client:
                        token_controller.remote_token_add_sign_keys_with_csrs(configuration,
                                                                              security_server,
                                                                              False,
                                                                              client)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert len(response[0].keys) == 3
                assert str(response[0].keys[0].label) == auth_key_label
                assert str(response[0].keys[1].label) == sign_key_label

    def step_cert_download_csrs(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)
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
        self.test.config['security_server'][ssn]['certificates'] = signed_certs

    def test_run_configuration(self):
        self.step_token_init_keys()
        self.step_cert_import_fail_certificates_missing()
        ssn = 0
        downloaded_csrs = CertificateTest(self.test).step_cert_download_csrs()
        for security_server in self.test.config["security_server"]:
            signed_certs = CertificateTest(self.test).step_acquire_certs(downloaded_csrs[(ssn * 3):(ssn * 3 + 3)], security_server)
            CertificateTest(self.test).apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

        self.step_cert_register_fail_certificates_not_imported()
        self.step_cert_import()
        self.step_cert_register()

        # Wait for global configuration status updates
        for ssn in range(0, len(self.test.config["security_server"])):
            waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.test.config, ssn), 1, 300)

        self.step_cert_activate()
        self.list_certificates()
        self.step_import_tls_certificate()
        self.step_cert_download_internal_tls()
