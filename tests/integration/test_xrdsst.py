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
from xrdsst.main import XRDSSTTest


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
            timestamp_controller.load_config = (lambda: self.config)
            timestamp_controller.init()

    def step_token_login(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            token_controller.load_config = (lambda: self.config)
            token_controller.login()

    def step_token_init_keys(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            token_controller.load_config = (lambda: self.config)
            token_controller.init_keys()

    def step_cert_import(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            cert_controller.import_()

    def step_cert_register(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            cert_controller.register()

    def step_cert_activate(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            cert_controller.activate()

    def step_subsystem_add_client(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            client_controller.load_config = (lambda: self.config)
            client_controller.add()

    def step_subsystem_register(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            client_controller.load_config = (lambda: self.config)
            client_controller.register()

    def step_add_service_description(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    service_controller.remote_add_service_description(configuration, security_server, client, service_description)
            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id, ssn)
            assert description["disabled"] is True
            ssn = ssn + 1

    def step_enable_service_description(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    service_controller.remote_enable_service_description(configuration, security_server, client, service_description)
            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id, ssn)
            assert description["disabled"] is False
            ssn = ssn + 1

    def step_add_service_access(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    service_controller.remote_add_access_rights(configuration, security_server, client, service_description)
            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id, ssn)
            service_clients = get_service_clients(self.config, description["services"][0]["id"], ssn)
            assert len(service_clients) == 1
            ssn = ssn + 1

    def step_update_service_parameters(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.config["security_server"]:
            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id, ssn)
            assert description["services"][0]["timeout"] == 60
            assert description["services"][0]["url"] == 'http://petstore.swagger.io/v1'
            ssn = ssn + 1

        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    service_controller.remote_update_service_parameters(configuration, security_server, client, service_description)
            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id, ssn)
            assert description["services"][0]["timeout"] == 120
            assert description["services"][0]["url"] == 'http://petstore.xxx'
            ssn = ssn + 1

    def step_add_service_endpoints(self):
        endpoint_controller = EndpointController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    for endpoint in service_description["endpoints"]:
                        endpoint_controller.remote_add_service_endpoints(configuration, security_server, client, service_description, endpoint)

            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id, ssn)
            assert len(description["services"][0]["endpoints"]) == 5
            assert str(description["services"][0]["endpoints"][4]["path"]) == "/testPath"
            assert str(description["services"][0]["endpoints"][4]["method"]) == "POST"
            ssn = ssn + 1

    def step_add_endpoints_access(self):
        endpoint_controller = EndpointController()
        ssn = 0
        for security_server in self.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.config)
            for client in security_server["clients"]:
                for service_description in client["service_descriptions"]:
                    endpoint_controller.remote_add_endpoints_access(configuration, security_server, client, service_description)

            client = get_client(self.config, ssn)
            client_id = client['id']
            description = get_service_description(self.config, client_id)
            service_clients = get_endpoint_service_clients(self.config, description["services"][0]["endpoints"][4]["id"])
            assert len(service_clients) == 1
            ssn = ssn + 1

    def step_configure_certs(self):
        ssn = 0
        downloaded_csrs = self.step_cert_download_csrs()
        for security_server in self.config["security_server"]:
            csrs = downloaded_csrs[(ssn * 2):(ssn * 2 + 2)]
            signed_certs = self.step_acquire_certs(csrs, security_server)
            self.apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        unconfigured_servers_at_start = self.query_status()
        self.step_init()

        self.query_status()
        self.step_timestamp_init()

        self.query_status()
        self.step_token_login()

        self.query_status()
        self.step_token_init_keys()

        self.query_status()
        self.step_configure_certs()

        self.query_status()
        self.step_cert_import()

        self.query_status()
        self.step_cert_register()

        self.query_status()
        self.step_cert_activate()

        # Wait for global configuration status updates
        ssn = 0
        for security_server in self.config["security_server"]:
            waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config, ssn), self.retry_wait, self.max_retries)
            self.query_status()
            ssn = ssn + 1

        self.query_status()
        self.step_subsystem_add_client()

        self.query_status()
        self.step_subsystem_register()

        self.query_status()
        self.step_add_service_description()

        self.query_status()
        self.step_enable_service_description()

        self.query_status()
        self.step_add_service_access()

        self.query_status()
        self.step_update_service_parameters()

        configured_servers_at_end = self.query_status()

        self.query_status()
        self.step_add_service_endpoints()

        self.query_status()
        self.step_add_endpoints_access()

        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)
