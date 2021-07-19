import json
import os
import subprocess
import sys
import unittest

import urllib3

from tests.util.test_util import find_test_ca_sign_url, perform_test_ca_sign, get_client, get_service_description, \
    assert_server_statuses_transitioned, auth_cert_registration_global_configuration_update_received, waitfor, get_service_clients, \
    get_endpoint_service_clients, getClientTlsCertificates, get_service_descriptions
from xrdsst.controllers.backup import BackupController
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.diagnostics import DiagnosticsController
from xrdsst.controllers.endpoint import EndpointController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.member import MemberController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import StatusController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.controllers.user import UserController
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.core.util import revoke_api_key, get_admin_credentials, get_ssh_key, get_ssh_user
from xrdsst.main import XRDSSTTest
from xrdsst.models import ClientStatus, ServiceClientType, KeyUsageType
from tests.end_to_end.renew_certificate import RenewCertificate
from tests.end_to_end.local_group_test import LocalGroupTest


class EndToEndTest(unittest.TestCase):
    config_file = None
    config = None
    transient_api_key_id = []

    def setUp(self):
        with XRDSSTTest() as app:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            idx = 0
            for arg in sys.argv:
                idx += 1
                if arg == "-c":
                    self.config_file = sys.argv[idx]
            base = BaseController()
            base.app = app
            self.config = base.load_config(baseconfig=self.config_file)
            ssn = 0
            for security_server in self.config["security_server"]:
                if security_server.get(ConfKeysSecurityServer.CONF_KEY_API_KEY):
                    try:
                        api_key = base.create_api_key(self.config, BaseController._TRANSIENT_API_KEY_ROLES, security_server)
                        self.transient_api_key_id.append(base.api_key_id[security_server['name']][0])
                        self.create_api_key(api_key, ssn)
                    except Exception as err:
                        base.log_api_error('BaseController->get_api_key:', err)
                ssn = ssn + 1
            base.api_key_id.clear()

    def tearDown(self):
        with XRDSSTTest() as app:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            base = BaseController()
            app.Meta.handlers[0].config_file = self.config_file
            ssn = 0
            for security_server in self.config["security_server"]:
                app.api_keys[security_server["name"]] = os.getenv(security_server["api_key"], "")
                base.api_key_id[security_server['name']] = self.transient_api_key_id[ssn], base.security_server_address(security_server)
                ssn = ssn + 1
            base.app = app
            revoke_api_key(app)
            self.step_verify_final_transient_api_keys()
            del os.environ[self.config["security_server"][0]["api_key"]]
            del os.environ[self.config["security_server"][1]["api_key"]]
            if self.config_file is not None:
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)

    def step_verify_initial_transient_api_keys(self):
        transient_api_key_id = []
        for security_server in self.config["security_server"]:
            credentials = get_admin_credentials(security_server, self.config)
            ssh_key = get_ssh_key(security_server, self.config)
            ssh_user = get_ssh_user(security_server, self.config)
            url = security_server["api_key_url"]
            curl_cmd = "curl -X GET -u " + credentials + " --silent " + url + "/ -k"
            cmd = "ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
                  ssh_key + "\" " + ssh_user + "@" + security_server["name"] + " \"" + curl_cmd + "\""
            exitcode, data = subprocess.getstatusoutput(cmd)
            if exitcode == 0:
                api_key_json = json.loads(data)
                for api_key_data in api_key_json:
                    transient_api_key_id.append(api_key_data["id"])
            else:
                transient_api_key_id.append('error')
        assert len(transient_api_key_id) == 2
        assert len(self.transient_api_key_id) == 2
        assert transient_api_key_id[0] == self.transient_api_key_id[0]
        assert transient_api_key_id[1] == self.transient_api_key_id[1]

    def step_verify_final_transient_api_keys(self):
        transient_api_key_id = []
        for security_server in self.config["security_server"]:
            credentials = get_admin_credentials(security_server, self.config)
            ssh_key = get_ssh_key(security_server, self.config)
            ssh_user = get_ssh_user(security_server, self.config)
            url = security_server["api_key_url"]
            curl_cmd = "curl -X GET -u " + credentials + " --silent " + url + "/ -k"
            cmd = "ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
                  ssh_key + "\" " + ssh_user + "@" + security_server["name"] + " \"" + curl_cmd + "\""
            exitcode, data = subprocess.getstatusoutput(cmd)
            if exitcode == 0:
                api_key_json = json.loads(data)
                for api_key_data in api_key_json:
                    transient_api_key_id.append(api_key_data["id"])
            else:
                transient_api_key_id.append('error')
        assert len(transient_api_key_id) == 0

    def step_member_find(self):
        with XRDSSTTest() as app:
            base = BaseController()
            member_controller = MemberController()
            member_controller.app = app

            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = member_controller.remote_find_name(configuration,
                                                              security_server,
                                                              security_server["owner_member_class"],
                                                              security_server["owner_member_code"])
                assert response.member_name == security_server["owner_dn_org"]

    def step_member_list_classes(self):
        with XRDSSTTest() as app:
            base = BaseController()
            member_controller = MemberController()
            member_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = member_controller.remote_list_classes(configuration, security_server, 'DEV')
                assert response == ['COM', 'PRIVATE-FOR-DEV', 'ORG', 'GOV']

    def step_upload_anchor_fail_file_missing(self):
        base = BaseController()
        init = InitServerController()
        configuration_anchor = []
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.upload_anchor(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            ssn = ssn + 1

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_upload_anchor_fail_file_bogus_content(self):
        base = BaseController()
        init = InitServerController()
        configuration_anchor = []

        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor-bogus.xml")
            init.upload_anchor(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            ssn = ssn + 1

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_owner_member_class_missing(self):
        base = BaseController()
        init = InitServerController()
        member_class = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.config["security_server"]:
            member_class.append(security_server["owner_member_class"])
            self.config["security_server"][ssn]["owner_member_class"] = ''
            ssn = ssn + 1

        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["owner_member_class"] = member_class[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_owner_member_code_missing(self):
        base = BaseController()
        init = InitServerController()
        member_code = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.config["security_server"]:
            member_code.append(security_server["owner_member_code"])
            self.config["security_server"][ssn]["owner_member_code"] = ''
            ssn = ssn + 1

        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["owner_member_code"] = member_code[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_server_code_missing(self):
        base = BaseController()
        init = InitServerController()
        server_code = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.config["security_server"]:
            server_code.append(security_server["security_server_code"])
            self.config["security_server"][ssn]["security_server_code"] = ''
            ssn = ssn + 1

        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["security_server_code"] = server_code[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_token_pin_missing(self):
        base = BaseController()
        init = InitServerController()
        token_pin = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.config["security_server"]:
            token_pin.append(security_server["software_token_pin"])
            self.config["security_server"][ssn]["software_token_pin"] = ''
            ssn = ssn + 1

        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["software_token_pin"] = token_pin[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_init(self):
        base = BaseController()
        init = InitServerController()
        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            assert status.is_server_code_initialized is False

        init.initialize_server(self.config)

        for security_server in self.config["security_server"]:
            configuration = base.create_api_config(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is True
            assert status.is_server_code_initialized is True

    def step_timestamp_init(self):
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = timestamp_controller.create_api_config(security_server, self.config)
                response = timestamp_controller.remote_get_configured(configuration)
                assert response == []
                timestamp_controller.remote_timestamp_service_init(configuration, security_server)
                response = timestamp_controller.remote_get_configured(configuration)
                assert len(response) > 0
                assert len(response[0].name) > 0
                assert len(response[0].url) > 0

    def step_token_login(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.config)
                token_controller.remote_token_login(configuration, security_server)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True

    def step_token_login_already_logged_in(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.config)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True
                assert 'LOGOUT' in response[0].possible_actions
                token_controller.remote_token_login(configuration, security_server)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True
                assert 'LOGOUT' in response[0].possible_actions

    def step_token_init_keys(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.config)
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

    def step_cert_download_internal_tls(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                ss_configuration = cert_controller.create_api_config(security_server, self.config)
                result = cert_controller.remote_download_internal_tls(ss_configuration, security_server)
                assert len(result) == 1

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

    def create_api_key(self, api_key, ssn):
        api_key_env_name = self.config["security_server"][ssn]["api_key"]
        os.environ[api_key_env_name] = api_key

    def step_cert_import_fail_certificates_missing(self):
        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["certificates"] = ''

        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                response = cert_controller.remote_import_certificates(configuration, security_server)
                assert len(response) == 0

    def step_cert_register_fail_certificates_not_imported(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                cert_controller.remote_register_certificate(configuration, security_server)

    def step_cert_import(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                response = cert_controller.remote_import_certificates(configuration, security_server)
                assert len(response) > 0

    def step_cert_register(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                cert_controller.remote_register_certificate(configuration, security_server)

    def step_cert_activate(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                cert_controller.remote_activate_certificate(configuration, security_server)

    def step_subsystem_add_client_fail_member_code_missing(self):
        member_code = []
        with XRDSSTTest() as app:

            ssn = 0
            for security_server in self.config["security_server"]:
                cln = 0
                for client in security_server["clients"]:
                    member_code.append(client["member_code"])
                    self.config["security_server"][ssn]["clients"][cln]["member_code"] = ''
                    cln = cln + 1
                ssn = ssn + 1

            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    response = client_controller.remote_add_client(configuration, client)
                    assert response is None
                ssn = ssn + 1

        ssn = 0
        idx = 0
        for security_server in self.config["security_server"]:
            cln = 0
            for client in security_server["clients"]:
                self.config["security_server"][ssn]["clients"][cln]["member_code"] = member_code[idx]
                cln = cln + 1
                idx = idx + 1
            ssn = ssn + 1

    def step_subsystem_add_client_fail_member_class_missing(self):
        member_class = []
        with XRDSSTTest() as app:

            ssn = 0
            for security_server in self.config["security_server"]:
                cln = 0
                for client in security_server["clients"]:
                    member_class.append(client["member_class"])
                    self.config["security_server"][ssn]["clients"][cln]["member_class"] = ''
                    cln = cln + 1
                ssn = ssn + 1

            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    response = client_controller.remote_add_client(configuration, client)
                    assert response is None
                ssn = ssn + 1

        ssn = 0
        idx = 0
        for security_server in self.config["security_server"]:
            cln = 0
            for client in security_server["clients"]:
                self.config["security_server"][ssn]["clients"][cln]["member_class"] = member_class[idx]
                cln = cln + 1
                idx = idx + 1
            ssn = ssn + 1

    def step_subsystem_register_fail_client_not_saved(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) == 0
                    client_controller.remote_register_client(configuration, security_server, client)
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) == 0
                ssn = ssn + 1

    def step_add_service_description_fail_client_not_saved(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        found_client = get_client(self.config, client, ssn)
                        assert len(found_client) == 0
                        response = service_controller.remote_add_service_description(configuration, client, service_description)
                        assert response is None
            ssn = ssn + 1

    def step_subsystem_add_client(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) == 0
                    response = client_controller.remote_add_client(configuration, client)
                    assert response is not None
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] != ClientStatus.GLOBAL_ERROR
                ssn = ssn + 1

    def step_subsystem_register(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] != ClientStatus.GLOBAL_ERROR
                    client_controller.remote_register_client(configuration, security_server, client)
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] != ClientStatus.GLOBAL_ERROR
                ssn = ssn + 1

    def step_subsystem_update_parameters(self):
        connection_type = []
        ssn = 0
        for security_server in self.config["security_server"]:
            connection_type.append(security_server["clients"][0]["connection_type"])
            connection_type.append(security_server["clients"][1]["connection_type"])
            ssn = ssn + 1

        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
                cln = 0
                for client in security_server["clients"]:
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["connection_type"] == 'HTTP'
                    self.config["security_server"][ssn]["clients"][cln]["connection_type"] = 'HTTPS'
                    client_controller.remote_update_client(configuration, security_server, client)
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["connection_type"] == 'HTTPS'
                    cln = cln + 1
                ssn = ssn + 1

            for ssn in range(0, len(self.config["security_server"])):
                self.config["security_server"][ssn]["clients"][0]["connection_type"] = connection_type[ssn]
                self.config["security_server"][ssn]["clients"][1]["connection_type"] = connection_type[ssn]

    def step_add_service_description_fail_url_missing(self):
        description_url = []
        ssn = 0
        for security_server in self.config["security_server"]:
            description_url.append(security_server["clients"][0]["service_descriptions"][0]["url"])
            description_url.append(security_server["clients"][0]["service_descriptions"][1]["url"])
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = ''
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["url"] = ''
            ssn = ssn + 1

        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = description_url[0]
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["url"] = description_url[1]

    def step_add_service_description_fail_type_missing(self):
        types = []
        ssn = 0
        for security_server in self.config["security_server"]:
            types.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            types.append(security_server["clients"][0]["service_descriptions"][1]["type"])
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = ''
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = ''
            ssn = ssn + 1

        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = types[0]
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = types[1]

    def step_enable_service_description_fail_service_description_not_added(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description is None
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_enable_service_description(configuration, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

    def step_add_service_description(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description["disabled"] is True
            ssn = ssn + 1

    def step_enable_service_description(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.config, client_id, ssn)
                    for description in descriptions:
                        assert description["disabled"] is True
                        for service_description in client["service_descriptions"]:
                            service_controller.remote_enable_service_description(configuration, client, service_description)
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_description(self.config, client_id, ssn)
                        assert description["disabled"] is False
            ssn = ssn + 1

    def step_add_service_access(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_access_rights(configuration, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    service_clients = get_service_clients(self.config, description["services"][0]["id"], ssn)
                    assert len(service_clients) == 1
            ssn = ssn + 1

    def step_update_service_parameters(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.config, client_id, ssn)
                    for description in descriptions:
                        if description["type"] != "WSDL":
                            assert description["services"][0]["timeout"] == 60
                            assert description["services"][0]["url"] == 'http://petstore.swagger.io/v1'
            ssn = ssn + 1

        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_update_service_parameters(configuration, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.config, client_id, ssn)
                    for description in descriptions:
                        if description["type"] != "WSDL":
                            assert description["services"][0]["timeout"] == 120
                            assert description["services"][0]["url"] == 'http://petstore.xxx'
            ssn = ssn + 1

    def step_list_service_descriptions(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        response = service_controller.remote_list_service_descriptions(configuration, security_server, [client_id])
                        assert len(response) == 2
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == client_id
                        assert response[0]["type"] == 'WSDL'
                        assert response[0]["disabled"] is False
                        assert response[0]["services"] == 4
                        assert response[1]["security_server"] == security_server["name"]
                        assert response[1]["client_id"] == client_id
                        assert response[1]["type"] == 'OPENAPI3'
                        assert response[1]["disabled"] is False
                        assert response[1]["services"] == 1
                ssn = ssn + 1

    def step_list_service_description_services(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)

                        list_of_services = service_controller.remote_list_services(configuration, security_server, client_id, [description[0]["id"]])
                        assert len(list_of_services) == 4

                        service_codes = ['authCertDeletion', 'clientDeletion', 'clientReg', 'ownerChange']
                        sn = 0
                        for service in list_of_services:
                            assert service["security_server"] == security_server["name"]
                            assert service["client_id"] == client_id
                            assert service["service_id"] == client_id + ':' + service_codes[sn]
                            assert service["service_code"] == service_codes[sn]
                            sn = sn + 1

                        list_of_services = service_controller.remote_list_services(configuration, security_server, client_id, [description[1]["id"]])
                        assert len(list_of_services) == 1
                        assert list_of_services[0]["security_server"] == security_server["name"]
                        assert list_of_services[0]["client_id"] == client_id
                        assert list_of_services[0]["service_id"] == client_id + ':Petstore'
                        assert list_of_services[0]["service_code"] == 'Petstore'
                        assert list_of_services[0]["timeout"] == 120
                        assert list_of_services[0]["url"] == 'http://petstore.xxx'
                ssn = ssn + 1

    def step_update_service_description(self):
        rest_service_code = []
        ssn = 0
        for security_server in self.config["security_server"]:
            rest_service_code.append(security_server["clients"][0]["service_descriptions"][0]["rest_service_code"])
            ssn = ssn + 1

        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[1]["client_id"] == client_id
                        assert description[1]["type"] == 'OPENAPI3'
                        assert len(description[1]["services"]) == 1
                        assert description[1]["services"][0]["service_code"] == 'Petstore'

                        service_controller.remote_update_service_descriptions(configuration,
                                                                              client_id,
                                                                              [description[1]["id"]],
                                                                              'NewPetstore',
                                                                              None)

                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[1]["client_id"] == client_id
                        assert description[1]["type"] == 'OPENAPI3'
                        assert len(description[1]["services"]) == 1
                        assert description[1]["services"][0]["service_code"] == 'NewPetstore'
                ssn = ssn + 1

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["rest_service_code"] = rest_service_code[0]

    def step_refresh_service_description(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[1]["client_id"] == client_id
                        assert description[1]["type"] == 'OPENAPI3'
                        assert len(description[1]["services"]) == 1
                        assert description[1]["services"][0]["service_code"] == 'Petstore'

                        service_controller.remote_refresh_service_descriptions(configuration,
                                                                               client_id,
                                                                               [description[0]["id"]])

                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[1]["client_id"] == client_id
                        assert description[1]["type"] == 'OPENAPI3'
                        assert len(description[1]["services"]) == 1
                        assert description[1]["services"][0]["service_code"] == 'Petstore'
                ssn = ssn + 1

    def step_delete_service_access_rights(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)
                        response = service_controller.remote_list_access_for_services(configuration, security_server, client_id, [description[1]["id"]])
                        assert len(response) == 1
                        service_controller.remote_delete_service_access(configuration,
                                                                        security_server,
                                                                        response[0]["service_id"],
                                                                        client_id,
                                                                        description[1]["id"],
                                                                        [response[0]["service_client_id"]])
                        response = service_controller.remote_list_access_for_services(configuration, security_server, client_id, [description[1]["id"]])
                        assert len(response) == 0
                ssn = ssn + 1

    def step_disable_service_description(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[0]["disabled"] is False

                        service_controller.remote_disable_service_descriptions(configuration,
                                                                               client_id,
                                                                               [description[0]["id"]],
                                                                               'disable notice')

                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[0]["client_id"] == client_id
                        assert description[0]["disabled"] is True
                ssn = ssn + 1

    def step_delete_service_description(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        response = service_controller.remote_list_service_descriptions(configuration, security_server, [client_id])

                        assert len(response) == 2
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == client_id
                        assert response[0]["type"] == 'WSDL'
                        assert response[0]["services"] == 4
                        assert response[1]["security_server"] == security_server["name"]
                        assert response[1]["client_id"] == client_id
                        assert response[1]["type"] == 'OPENAPI3'
                        assert response[1]["services"] == 1

                        service_controller.remote_delete_service_descriptions(configuration, client_id, [description[0]["id"]])

                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 1
                        response = service_controller.remote_list_service_descriptions(configuration, security_server, [client_id])
                        assert len(response) == 1
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == client_id
                        assert response[0]["type"] == 'OPENAPI3'
                        assert response[0]["services"] == 1
                ssn = ssn + 1

    def step_list_service_access_rights(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.config, client_id, ssn)
                        assert len(description) == 2
                        response = service_controller.remote_list_access_for_services(configuration, security_server, client_id, [description[1]["id"]])
                        assert len(response) == 1
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == 'DEV:ORG:111:TEST'
                        assert response[0]["service_id"] == 'DEV:ORG:111:TEST:Petstore'
                        assert response[0]["service_client_id"] == 'DEV:security-server-owners'
                        assert response[0]["name"] == 'Security server owners'
                        assert response[0]["type"] == ServiceClientType.GLOBALGROUP

                ssn = ssn + 1

    def step_create_admin_user_fail_admin_credentials_missing(self):
        admin_credentials_env_var = self.config["security_server"][0]["admin_credentials"]
        admin_credentials = os.getenv(admin_credentials_env_var, "")
        os.environ[admin_credentials_env_var] = ""
        user = UserController()
        user_created = user.create_user(self.config)
        assert user_created is None
        os.environ[admin_credentials_env_var] = admin_credentials

    def step_create_admin_user_fail_ssh_user_missing(self):
        ssh_user_env_var = self.config["security_server"][0]["ssh_user"]
        ssh_user = os.getenv(ssh_user_env_var, "")
        os.environ[ssh_user_env_var] = ""
        user = UserController()
        user_created = user.create_user(self.config)
        assert user_created is None
        os.environ[ssh_user_env_var] = ssh_user

    def step_create_admin_user_fail_ssh_private_key_missing(self):
        ssh_private_key_env_var = self.config["security_server"][0]["ssh_private_key"]
        ssh_private_key = os.getenv(ssh_private_key_env_var, "")
        os.environ[ssh_private_key_env_var] = ""
        user = UserController()
        user_created = user.create_user(self.config)
        assert user_created is None
        os.environ[ssh_private_key_env_var] = ssh_private_key

    def step_create_admin_user(self):
        admin_credentials_env_var = self.config["security_server"][0]["admin_credentials"]
        old_admin_user = os.getenv(admin_credentials_env_var, "")
        os.environ[admin_credentials_env_var] = 'newxrd:pwd'
        user = UserController()
        user_created = user.create_user(self.config)
        assert len(user_created) == 2
        for ssn in range(0, len(self.config["security_server"])):
            assert user_created[ssn] is True
        os.environ[admin_credentials_env_var] = old_admin_user

    def step_add_service_endpoints_fail_endpoints_service_type_wsdl(self):
        service_type = []
        ssn = 0
        for security_server in self.config["security_server"]:
            service_type.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            service_type.append(security_server["clients"][0]["service_descriptions"][1]["type"])
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = 'WSDL'
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = 'WSDL'
            ssn = ssn + 1

        endpoint_controller = EndpointController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        if "endpoints" in service_description:
                            for endpoint in service_description["endpoints"]:
                                endpoint_controller.remote_add_service_endpoints(configuration, client, service_description, endpoint)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_descriptions(self.config, client_id, ssn)
                    assert len(description[0]["services"][0]["endpoints"]) == 1
                    assert len(description[1]["services"][0]["endpoints"]) == 4
            ssn = ssn + 1

        for ssn in range(0, len(self.config["security_server"])):
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = service_type[0]
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = service_type[1]

    def step_add_service_endpoints(self):
        endpoint_controller = EndpointController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        if "endpoints" in service_description:
                            for endpoint in service_description["endpoints"]:
                                endpoint_controller.remote_add_service_endpoints(configuration, client, service_description, endpoint)

                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.config, client_id, ssn)
                    for description in descriptions:
                        if description["type"] != "WSDL":
                            assert len(description["services"][0]["endpoints"]) == 5
                            assert str(description["services"][0]["endpoints"][4]["path"]) == "/testPath"
                            assert str(description["services"][0]["endpoints"][4]["method"]) == "POST"
            ssn = ssn + 1

    def step_add_endpoints_access(self):
        ssn = 0
        endpoint_controller = EndpointController()
        for security_server in self.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_description" in client:
                    for service_description in client["service_descriptions"]:
                        endpoint_controller.remote_add_endpoints_access(configuration, client, service_description)

                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    service_clients = get_endpoint_service_clients(self.config, description["services"][0]["endpoints"][4]["id"], ssn)
                    assert len(service_clients) == 1
                    assert str(service_clients[0]["id"]) == "DEV:security-server-owners"
            ssn = ssn + 1

    def step_import_tls_certificate(self):
        tls_certificate = "tests/resources/cert.pem"
        for security_server in self.config["security_server"]:
            security_server["tls_certificates"] = [os.path.join(ROOT_DIR, tls_certificate)]
            for client in security_server["clients"]:
                if "tls_certificates" in client:
                    client["tls_certificates"] = [os.path.join(ROOT_DIR, tls_certificate)]
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.config)
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
                            tls_certs = getClientTlsCertificates(self.config, client, ssn)
                            assert len(tls_certs) == 1
                ssn = ssn + 1

    def step_client_unregister(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            configuration = client_controller.create_api_config(self.config["security_server"][0], self.config)
            for client in self.config["security_server"][0]["clients"]:
                if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client:
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] == ClientStatus.REGISTERED
                    client_controller.remote_unregister_client(configuration, self.config["security_server"][0]["name"], [found_client[0]["id"]])
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] == ClientStatus.DELETION_IN_PROGRESS

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

    def list_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)

            certificates = cert_controller.list()
            headers = [*certificates[0]]
            for header in headers:
                assert header in cert_controller.app._last_rendered[0][0]

            assert len(certificates) == 6
            assert len(cert_controller.app._last_rendered[0]) == 7

    def step_disable_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)

            certificates = cert_controller.list()

            for security_server in self.config["security_server"]:
                security_server["certificate_management"] = [cert["hash"] for cert in certificates if cert["ss"] == security_server["name"]]

            cert_controller.load_config = (lambda: self.config)
            cert_controller.disable()
            certificates_disabled = cert_controller.list()
            for cert_disabled in certificates_disabled:
                assert cert_disabled["ocsp_status"] == "DISABLED"

    def step_unregister_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)

            certificates = cert_controller.list()

            for security_server in self.config["security_server"]:
                security_server["certificate_management"] = [cert["hash"] for cert in certificates
                                                             if cert["ss"] == security_server["name"] and cert["type"] == KeyUsageType.AUTHENTICATION]

            cert_controller.load_config = (lambda: self.config)
            cert_controller.unregister()
            certificates_unregister = cert_controller.list()
            for cert_unregister in certificates_unregister:
                if cert_unregister["type"] == KeyUsageType.AUTHENTICATION:
                    assert cert_unregister["status"] == "DELETION_IN_PROGRESS"

    def step_delete_certificates(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)

            certificates = cert_controller.list()

            for security_server in self.config["security_server"]:
                security_server["certificate_management"] = [cert["hash"] for cert in certificates
                                                             if cert["ss"] == security_server["name"] and cert["type"] == KeyUsageType.AUTHENTICATION]

            cert_controller.load_config = (lambda: self.config)
            cert_controller.delete()
            certificates = cert_controller.list()
            for cert in certificates:
                assert cert["type"] != KeyUsageType.AUTHENTICATION

    def step_client_delete(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            configuration = client_controller.create_api_config(self.config["security_server"][0], self.config)
            for client in self.config["security_server"][0]["clients"]:
                if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client:
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] == ClientStatus.DELETION_IN_PROGRESS
                    client_controller.remote_delete_client(configuration, self.config["security_server"][0]["name"], [found_client[0]["id"]])
                    found_client = get_client(self.config, client, ssn)
                    assert len(found_client) == 0

    def step_add_backup(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                backups = backup_controller.remote_list_backups(configuration, security_server)
                assert len(backups) == 0
                response = backup_controller.remote_add_backup(configuration, security_server["name"])
                assert response is not None
                assert "conf_backup" in response.filename
                assert response.created_at is not None

    def step_list_backups(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                assert "conf_backup" in response[0]["file_name"]
                assert response[0]["created"] is not None

    def step_download_backups(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                file_name = response[0]["file_name"]
                response = backup_controller.remote_download_backup(configuration, security_server["name"], [file_name])
                assert len(response) == 1
                assert response[0] == '/tmp/' + file_name

    def step_restore_backup(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                file_name = response[0]["file_name"]
                response = backup_controller.remote_restore_backup(configuration, security_server["name"], file_name)
                assert response is not None

    def step_delete_backups(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                file_name = response[0]["file_name"]
                backup_controller.remote_delete_backup(configuration, security_server["name"], [file_name])
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 0

    def step_list_global_conf_diagnostics(self):
        with XRDSSTTest() as app:
            base = BaseController()
            diagnostics_controller = DiagnosticsController()
            diagnostics_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = diagnostics_controller.remote_list_global_configuration(configuration, security_server)
                assert len(response) == 1
                assert response[0]["status_class"] == 'OK'
                assert response[0]["status_code"] == 'SUCCESS'
                assert response[0]["prev_update_at"] is not None
                assert response[0]["next_update_at"] is not None

    def step_list_ocsp_responders_diagnostics(self):
        with XRDSSTTest() as app:
            base = BaseController()
            diagnostics_controller = DiagnosticsController()
            diagnostics_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = diagnostics_controller.remote_list_ocsp_responders(configuration, security_server)
                assert len(response) == 2
                assert response[0]["name"] == 'CN=X-Road CA G1, O=X-Road Test'
                assert response[0]["url"] == 'http://dev-cs.i.x-road.rocks:8888/G1/'
                assert response[0]["status_class"] == 'OK'
                assert response[0]["status_code"] == 'SUCCESS'
                assert response[0]["prev_update_at"] is not None
                assert response[0]["next_update_at"] is not None

    def step_list_timestamping_services_diagnostics(self):
        with XRDSSTTest() as app:
            base = BaseController()
            diagnostics_controller = DiagnosticsController()
            diagnostics_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = base.create_api_config(security_server, self.config)
                response = diagnostics_controller.remote_list_timestamping_services(configuration, security_server)
                assert len(response) == 1
                assert response[0]["url"] == 'http://'
                assert response[0]["status_class"] == 'OK'
                assert response[0]["status_code"] == 'SUCCESS'
                assert response[0]["prev_update_at"] is not None

    def test_run_configuration(self):
        unconfigured_servers_at_start = self.query_status()

        self.step_verify_initial_transient_api_keys()
        self.step_upload_anchor_fail_file_missing()
        self.step_upload_anchor_fail_file_bogus_content()
        self.step_initialize_server_owner_member_class_missing()
        self.step_initialize_server_owner_member_code_missing()
        self.step_initialize_server_server_code_missing()
        self.step_initialize_server_token_pin_missing()

        self.step_init()
        self.step_timestamp_init()

        self.step_token_login()
        self.step_token_login_already_logged_in()

        self.step_subsystem_add_client_fail_member_class_missing()
        self.step_subsystem_add_client_fail_member_code_missing()
        self.step_subsystem_register_fail_client_not_saved()
        self.step_add_service_description_fail_client_not_saved()
        self.step_subsystem_add_client()
        self.step_token_init_keys()

        self.step_cert_import_fail_certificates_missing()
        ssn = 0
        downloaded_csrs = self.step_cert_download_csrs()
        for security_server in self.config["security_server"]:
            signed_certs = self.step_acquire_certs(downloaded_csrs[(ssn * 3):(ssn * 3 + 3)], security_server)
            self.apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

        self.step_cert_register_fail_certificates_not_imported()
        self.step_cert_import()
        self.step_cert_register()

        # Wait for global configuration status updates
        for ssn in range(0, len(self.config["security_server"])):
            waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config, ssn), 1, 300)
            self.query_status()

        self.step_cert_activate()
        self.list_certificates()

        self.step_import_tls_certificate()
        self.step_add_service_description_fail_url_missing()
        self.step_add_service_description_fail_type_missing()
        self.step_enable_service_description_fail_service_description_not_added()
        self.step_add_service_description()
        self.step_enable_service_description()
        self.step_add_service_access()

        self.step_member_find()
        self.step_member_list_classes()

        self.step_create_admin_user_fail_admin_credentials_missing()
        self.step_create_admin_user_fail_ssh_user_missing()
        self.step_create_admin_user_fail_ssh_private_key_missing()
        self.step_create_admin_user()

        self.step_add_service_endpoints_fail_endpoints_service_type_wsdl()
        self.step_add_service_endpoints()
        self.step_add_endpoints_access()
        self.step_subsystem_register()
        self.step_subsystem_update_parameters()
        self.step_update_service_parameters()
        self.step_list_service_descriptions()
        self.step_list_service_description_services()
        self.step_list_service_access_rights()
        self.step_delete_service_access_rights()
        self.step_refresh_service_description()
        self.step_disable_service_description()
        self.step_update_service_description()
        self.step_delete_service_description()
        self.step_cert_download_internal_tls()

        self.step_add_backup()
        self.step_list_backups()
        self.step_download_backups()
        self.step_restore_backup()
        self.step_delete_backups()

        self.step_list_global_conf_diagnostics()
        self.step_list_ocsp_responders_diagnostics()
        self.step_list_timestamping_services_diagnostics()

        RenewCertificate(self).test_run_configuration()
        LocalGroupTest(self).test_run_configuration()

        self.step_client_unregister()
        self.step_client_delete()

        configured_servers_at_end = self.query_status()
        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)
