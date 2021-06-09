import os

import urllib3

from tests.integration.integration_base import IntegrationTestBase
from tests.integration.integration_ops import IntegrationOpBase
from tests.util.test_util import get_client, auth_cert_registration_global_configuration_update_received, waitfor, get_service_clients, \
    get_endpoint_service_clients
from tests.util.test_util import get_service_description, assert_server_statuses_transitioned
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import ServerStatus
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.controllers.endpoint import EndpointController
from xrdsst.controllers.user import UserController
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.main import XRDSSTTest
from xrdsst.models import ClientStatus


def server_statuses_equal(sl1: [ServerStatus], sl2: [ServerStatus]):
    assert len(sl1) == len(sl2)

    # Ignore the global status that can have temporal changes and sometimes relies on flaky development central server
    # Ignore the roles which can freely change and be divided among API keys.
    for i in range(0, len(sl1)):
        assert sl1[i].security_server_name == sl2[i].security_server_name  # Config match sanity check

        assert sl1[i].version_status.__dict__ == sl2[i].version_status.__dict__
        assert sl1[i].token_status.__dict__ == sl2[i].token_status.__dict__
        assert sl1[i].server_init_status.__dict__ == sl2[i].server_init_status.__dict__
        assert sl1[i].status_keys.__dict__ == sl2[i].status_keys.__dict__
        assert sl1[i].status_csrs.__dict__ == sl2[i].status_csrs.__dict__
        assert sl1[i].status_certs.__dict__ == sl2[i].status_certs.__dict__
        assert sl1[i].timestamping_status == sl2[i].timestamping_status

    return True


class TestXRDSST(IntegrationTestBase, IntegrationOpBase):
    __test__ = True

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

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]
            ssn = ssn + 1

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

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]
            ssn = ssn + 1

    def step_initalize_server_owner_member_class_missing(self):
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

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["owner_member_class"] = member_class[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]
            ssn = ssn + 1

    def step_initalize_server_owner_member_code_missing(self):
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

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["owner_member_code"] = member_code[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]
            ssn = ssn + 1

    def step_initalize_server_server_code_missing(self):
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

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["security_server_code"] = server_code[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]
            ssn = ssn + 1

    def step_initalize_server_token_pin_missing(self):
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

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["software_token_pin"] = token_pin[ssn]
            self.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]
            ssn = ssn + 1

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
                assert response[0].possible_actions == ['TOKEN_CHANGE_PIN', 'LOGOUT', 'GENERATE_KEY']
                token_controller.remote_token_login(configuration, security_server)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True
                assert response[0].possible_actions == ['TOKEN_CHANGE_PIN', 'LOGOUT', 'GENERATE_KEY']

    def step_token_init_keys(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.config)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert len(response[0].keys) == 0
                token_controller.remote_token_add_keys_with_csrs(configuration, security_server)
                if "clients" in security_server:
                    for client in security_server["clients"]:
                        if client["member_class"] != security_server["owner_member_class"] or client["member_code"] != \
                                security_server["owner_member_code"]:
                            token_controller.remote_token_add_signing_key_new_member(configuration, security_server, client)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert len(response[0].keys) == 3
                auth_key_label = security_server['name'] + '-default-auth-key'
                sign_key_label = security_server['name'] + '-default-sign-key'
                assert str(response[0].keys[0].label) == auth_key_label
                assert str(response[0].keys[1].label) == sign_key_label

    def step_cert_import_fail_certificates_missing(self):
        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["certificates"] = ''
            ssn = ssn + 1

        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = cert_controller.create_api_config(security_server, self.config)
                response = cert_controller.remote_import_certificates(configuration, security_server)
                assert response is None

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
                cert_controller.remote_import_certificates(configuration, security_server)

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
                        response = service_controller.remote_add_service_description(configuration, security_server, client, service_description)
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

            ssn = 0
            for security_server in self.config["security_server"]:
                self.config["security_server"][ssn]["clients"][0]["connection_type"] = connection_type[ssn]
                self.config["security_server"][ssn]["clients"][1]["connection_type"] = connection_type[ssn]
                ssn = ssn + 1

    def step_add_service_description_fail_url_missing(self):
        description_url = []
        ssn = 0
        for security_server in self.config["security_server"]:
            description_url.append(security_server["clients"][0]["service_descriptions"][0]["url"])
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = ''
            ssn = ssn + 1

        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, security_server, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = description_url[ssn]
            ssn = ssn + 1

    def step_add_service_description_fail_type_missing(self):
        type = []
        ssn = 0
        for security_server in self.config["security_server"]:
            type.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = ''
            ssn = ssn + 1

        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, security_server, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = type[ssn]
            ssn = ssn + 1

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
                        service_controller.remote_enable_service_description(configuration, security_server, client, service_description)
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
                        service_controller.remote_add_service_description(configuration, security_server, client, service_description)
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
                    description = get_service_description(self.config, client_id, ssn)
                    assert description["disabled"] is True
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_enable_service_description(configuration, security_server, client, service_description)
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
                        service_controller.remote_add_access_rights(configuration, security_server, client, service_description)
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
                    description = get_service_description(self.config, client_id, ssn)
                    assert description["services"][0]["timeout"] == 60
                    assert description["services"][0]["url"] == 'http://petstore.swagger.io/v1'
            ssn = ssn + 1

        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_update_service_parameters(configuration, security_server, client, service_description)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert description["services"][0]["timeout"] == 120
                    assert description["services"][0]["url"] == 'http://petstore.xxx'
            ssn = ssn + 1

    def step_add_service_endpoints_fail_endpoints_service_type_wsdl(self):
        service_type = []
        ssn = 0
        for security_server in self.config["security_server"]:
            service_type.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = 'WSDL'
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
                                endpoint_controller.remote_add_service_endpoints(configuration, security_server, client, service_description, endpoint)
                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    assert len(description["services"][0]["endpoints"]) == 4
            ssn = ssn + 1

        ssn = 0
        for security_server in self.config["security_server"]:
            self.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = service_type[ssn]
            ssn = ssn + 1

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
                                endpoint_controller.remote_add_service_endpoints(configuration, security_server, client, service_description, endpoint)

                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
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
                        endpoint_controller.remote_add_endpoints_access(configuration, service_description, client, service_description)

                    found_client = get_client(self.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.config, client_id, ssn)
                    service_clients = get_endpoint_service_clients(self.config, description["services"][0]["endpoints"][4]["id"], ssn)
                    assert len(service_clients) == 1
                    assert str(service_clients[0]["id"]) == "DEV:security-server-owners"
            ssn = ssn + 1

    def step_configure_certs(self):
        ssn = 0
        downloaded_csrs = self.step_cert_download_csrs()
        for security_server in self.config["security_server"]:
            signed_certs = self.step_acquire_certs(downloaded_csrs[(ssn*3):(ssn * 3 + 3)], security_server)
            self.apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        unconfigured_servers_at_start = self.query_status()

        self.query_status()
        self.step_upload_anchor_fail_file_missing()
        self.step_upload_anchor_fail_file_bogus_content()
        self.step_initalize_server_owner_member_class_missing()
        self.step_initalize_server_owner_member_code_missing()
        self.step_initalize_server_server_code_missing()
        self.step_initalize_server_token_pin_missing()

        self.query_status()
        self.step_init()
        self.step_timestamp_init()

        self.query_status()
        self.step_token_login()
        self.step_token_login_already_logged_in()

        self.query_status()
        self.step_subsystem_add_client_fail_member_class_missing()
        self.step_subsystem_add_client_fail_member_code_missing()
        self.step_subsystem_register_fail_client_not_saved()
        self.step_add_service_description_fail_client_not_saved()
        self.step_subsystem_add_client()
        self.step_token_init_keys()
        self.step_cert_import_fail_certificates_missing()
        self.step_configure_certs()

        self.query_status()
        self.step_cert_register_fail_certificates_not_imported()
        self.step_cert_import()
        self.step_cert_import()
        self.step_cert_import()
        self.step_cert_register()

        # Wait for global configuration status updates
        ssn = 0
        for security_server in self.config["security_server"]:
            waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config, ssn), self.retry_wait, 400)
            self.query_status()
            ssn = ssn + 1

        self.query_status()
        self.step_cert_activate()
        self.step_add_service_description_fail_url_missing()
        self.step_add_service_description_fail_type_missing()
        self.step_enable_service_description_fail_service_description_not_added()
        self.step_add_service_description()
        self.step_enable_service_description()
        self.step_add_service_access()

        self.query_status()
        self.step_add_service_endpoints_fail_endpoints_service_type_wsdl()
        self.step_add_service_endpoints()
        self.step_add_endpoints_access()
        self.step_subsystem_register()
        self.step_subsystem_update_parameters()
        self.step_update_service_parameters()
        self.step_cert_download_internal_tsl()

        configured_servers_at_end = self.query_status()

        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)
