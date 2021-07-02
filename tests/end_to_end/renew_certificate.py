from xrdsst.controllers.cert import CertController
from xrdsst.controllers.token import TokenController
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.core.util import default_sign_key_label
from xrdsst.main import XRDSSTTest
from xrdsst.models.key_usage_type import KeyUsageType
from xrdsst.controllers.cert import CertOperations
from datetime import datetime


class RenewCertificate:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_token_create_new_keys(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.test.config)
                member_class = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS]
                member_code = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE]
                member_name = security_server[ConfKeysSecurityServer.CONF_KEY_DN_ORG]

                auth_key_label = security_server["name"] + "-default-auth-key" + "_" + datetime.today().strftime('%Y_%m_%d')
                sign_key_label = security_server["name"] + "-default-sign-key" + "_" + datetime.today().strftime('%Y_%m_%d')
                token_controller.remote_token_add_all_keys_with_csrs(configuration,
                                                                     security_server,
                                                                     member_class,
                                                                     member_code,
                                                                     member_name,
                                                                     auth_key_label,
                                                                     sign_key_label)

                for client in security_server["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE not in client:
                        sign_key_label_new_member = default_sign_key_label(security_server) + "_" \
                                                    + client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CLASS] + "_" \
                                                    + str(client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CODE]) + "_" \
                                                    + datetime.today().strftime('%Y_%m_%d')

                        token_controller.remote_token_add_sign_keys_with_csrs(configuration,
                                                                              security_server,
                                                                              True,
                                                                              client,
                                                                              auth_key_label)

                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert len(response[0].keys) == 6

                auth_cert = list(filter(lambda key: auth_key_label == key.label, response[0].keys))
                sign_cert = list(filter(lambda key: sign_key_label == key.label, response[0].keys))
                sign_cert_new_member = list(filter(lambda key: sign_key_label_new_member == key.label, response[0].keys))
                assert len(auth_cert) == 1
                assert len(sign_cert) == 1
                assert len(sign_cert_new_member) == 1

    def step_unregister_certificates(self, old_certificates):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)

            auth_certs = list(filter(lambda cert: cert["type"] == KeyUsageType.AUTHENTICATION, old_certificates))
            auth_hashes = list((auth_cert["hash"] for auth_cert in auth_certs))

            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                for auth_hash in auth_hashes:
                    cert_controller.remote_cert_operation(configuration, security_server, auth_hash, CertOperations.unregister)
                certificates_unregister = cert_controller.list()
                for cert_unregister in certificates_unregister:
                    if cert_unregister["type"] == KeyUsageType.AUTHENTICATION and cert_unregister["hash"] in auth_hashes:
                        assert cert_unregister["status"] == "DELETION_IN_PROGRESS"

    def step_disable_certificates(self, old_certificates):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)

            old_hashes = list((old_certificate["hash"] for old_certificate in old_certificates))
            certificates = cert_controller.list()
            for security_server in self.test.config["security_server"]:
                ss_certificates = list(filter(lambda cert: cert["ss"] == security_server["name"] and cert["hash"] not in old_hashes, certificates))
                assert len(ss_certificates) == 3

                configuration = cert_controller.create_api_config(security_server, self.test.config)
                for old_hash in old_hashes:
                    cert_controller.remote_cert_operation(configuration, security_server, old_hash, CertOperations.disable)

                certificates = cert_controller.list()
                ss_certificates = list(filter(lambda cert: cert["ss"] == security_server["name"] and cert["hash"] in old_hashes, certificates))
                for ss_certificate in ss_certificates:
                    assert bool(ss_certificate["active"] is not True)

    def step_delete_certificates(self, old_certificates):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)

            old_hashes = list((old_certificate["hash"] for old_certificate in old_certificates))
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.test.config)
                for old_hash in old_hashes:
                    cert_controller.remote_cert_operation(configuration, security_server, old_hash, CertOperations.delete)

                certificates = cert_controller.list()
                ss_certificates = list(filter(lambda cert: cert["ss"] == security_server["name"] and cert["hash"] in old_hashes, certificates))
                assert len(ss_certificates) == 0

    def get_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)
            return cert_controller.list()

    def test_run_configuration(self):

        old_certificates = self.get_certificates()

        self.step_token_create_new_keys()

        downloaded_csrs = self.test.step_cert_download_csrs()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            signed_certs = self.test.step_acquire_certs(downloaded_csrs[(ssn * 3):(ssn * 3 + 3)], security_server)
            self.test.apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

        self.test.step_cert_import()
        self.test.step_cert_register()
        self.test.step_cert_activate()

        # self.step_unregister_certificates(old_certificates)
        self.step_disable_certificates(old_certificates)
        # self.step_delete_certificates(old_certificates)
