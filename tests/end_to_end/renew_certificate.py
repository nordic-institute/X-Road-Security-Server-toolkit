import json
import os
import subprocess
import sys
import unittest
from argparse import Namespace

import urllib3

from tests.util.test_util import find_test_ca_sign_url, perform_test_ca_sign, get_client, get_service_description, \
    assert_server_statuses_transitioned, auth_cert_registration_global_configuration_update_received, waitfor, get_service_clients, \
    get_endpoint_service_clients, getClientTlsCertificates
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.endpoint import EndpointController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.member import MemberController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import StatusController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.controllers.user import UserController
from xrdsst.core.conf_keys import ConfKeysSecurityServer
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.core.util import revoke_api_key, get_admin_credentials, get_ssh_key, get_ssh_user
from xrdsst.main import XRDSSTTest
from xrdsst.models import ClientStatus
from xrdsst.models.key_usage_type import KeyUsageType
from tests.end_to_end.tests import EndToEndTest
from xrdsst.controllers.token import KeyTypes

class RenewCertificate():

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

                auth_key_label = security_server["name"] + "_" + "auth_label_test"
                sign_key_label = security_server["name"] + "_" + "sign_label_test"
                response = token_controller.remote_token_add_keys_with_csrs(self.test.config, security_server, KeyTypes.ALL,
                                                                            member_class, member_code, member_name, auth_key_label, sign_key_label)
                assert len(response) > 0
                token_controller.token_add_keys_with_csrs(configuration)

                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert len(response[0].keys) == 6

                auth_certs = filter(lambda key: auth_key_label in key, response[0].keys)
                sign_certs = filter(lambda key: sign_key_label in key, response[0].keys)
                assert len(auth_certs) == 1
                assert len(sign_certs) == 2

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

    def step_cert_activate(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                cert_controller.remote_activate_certificate(configuration, security_server)

    def step_unregister_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)

            certificates = cert_controller.list()

            for security_server in self.test.config["security_server"]:
                security_server["certificate_management"] = [cert["hash"] for cert in certificates
                                                                  if cert["ss"] == security_server["name"] and cert["type"] == KeyUsageType.AUTHENTICATION]

            cert_controller.load_config = (lambda: self.test.config)
            cert_controller.unregister()
            certificates_unregister = cert_controller.list()
            for cert_unregister in certificates_unregister:
                if cert_unregister["type"] == KeyUsageType.AUTHENTICATION:
                    assert cert_unregister["status"] == "DELETION_IN_PROGRESS"

    def step_delete_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.test.config)

            certificates = cert_controller.list()

            for security_server in self.test.config["security_server"]:
                security_server["certificate_management"] = [cert["hash"] for cert in certificates
                                                                  if cert["ss"] == security_server["name"] and cert["type"] == KeyUsageType.AUTHENTICATION]

            cert_controller.load_config = (lambda: self.test.config)
            cert_controller.delete()
            certificates = cert_controller.list()
            for cert in certificates:
                assert cert["type"] != KeyUsageType.AUTHENTICATION

    def test_run_configuration(self):

        downloaded_csrs = self.step_cert_download_csrs()
        for security_server in self.test.config["security_server"]:
            signed_certs = self.test.step_acquire_certs(downloaded_csrs[(ssn * 3):(ssn * 3 + 3)], security_server)
            self.test.apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

        self.step_unregister_certificates()
        self.step_delete_certificates()

