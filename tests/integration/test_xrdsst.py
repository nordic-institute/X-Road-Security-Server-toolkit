import urllib3

from tests.integration.integration_base import IntegrationTestBase
from tests.integration.integration_ops import IntegrationOpBase
from tests.util.test_util import get_client, auth_cert_registration_global_configuration_update_received, waitfor, get_service_clients
from tests.util.test_util import get_service_description, assert_server_statuses_transitioned
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import ServerStatus
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
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
        configuration = base.initialize_basic_config_values(self.config["security_server"][0], self.config)
        status = init.check_init_status(configuration)
        assert status.is_anchor_imported is False
        assert status.is_server_code_initialized is False
        init.initialize_server(self.config)
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

    def step_add_service_description(self, client_id):
        with XRDSSTTest() as app:
            service_controller = ServiceController()
            service_controller.app = app
            service_controller.load_config = (lambda: self.config)
            service_controller.add_description()
            service_description = get_service_description(self.config, client_id)
            assert service_description["disabled"] is True

    def step_enable_service_description(self, client_id):
        with XRDSSTTest() as app:
            service_controller = ServiceController()
            service_controller.app = app
            service_controller.load_config = (lambda: self.config)
            service_controller.enable_description()
            service_description = get_service_description(self.config, client_id)
            assert service_description["disabled"] is False

    def step_add_service_access(self, client_id):
        with XRDSSTTest() as app:
            service_controller = ServiceController()
            service_controller.app = app
            service_controller.load_config = (lambda: self.config)
            service_controller.add_access
            description = get_service_description(self.config, client_id)
            service_clients = get_service_clients(self.config, description["services"][0]["id"])
            assert len(service_clients) == 1

    def step_update_service_parameters(self, client_id):
        with XRDSSTTest() as app:
            service_controller = ServiceController()
            description = get_service_description(self.config, client_id)
            assert description["services"][0]["timeout"] == 60
            assert description["services"][0]["ssl_auth"] is False
            assert description["services"][0]["url"] == 'http://petstore'
            service_controller.app = app
            service_controller.load_config = (lambda: self.config)
            service_controller.update_parameters
            description = get_service_description(self.config, client_id)
            assert description["services"][0]["timeout"] == 120
            assert description["services"][0]["ssl_auth"] is True
            assert description["services"][0]["url"] == 'http://petstore.swagger.io/v1'

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # Uninitialized security server can already have functioning API interface and status query must function
        unconfigured_servers_at_start = self.query_status()
        self.step_init()

        self.query_status()
        self.step_timestamp_init()

        self.query_status()
        self.step_token_login()

        self.query_status()
        self.step_token_init_keys()

        self.query_status()

        # certificates
        downloaded_csrs = self.step_cert_download_csrs()
        signed_certs = self.step_acquire_certs(downloaded_csrs)

        self.apply_cert_config(signed_certs)
        self.query_status()

        self.step_cert_import()
        self.query_status()

        self.step_cert_register()
        self.query_status()

        self.step_cert_activate()
        self.query_status()

        # Wait for global configuration status updates
        waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config), self.retry_wait, self.max_retries)
        self.query_status()

        # subsystems
        self.step_subsystem_add_client()
        self.query_status()

        self.step_subsystem_register()
        self.query_status()

        client = get_client(self.config)
        client_id = client['id']

        # service descriptions
        self.step_add_service_description(client_id)
        self.query_status()

        self.step_enable_service_description(client_id)
        self.query_status()

        self.step_add_service_access(client_id)
        self.query_status()

        self.step_update_service_parameters(client_id)
        configured_servers_at_end = self.query_status()

        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)

        # Run autoconfiguration which should at this stage NOT AFFECT anything since configuration has not been
        # changed, all operations need to act idempotently and no new errors should occur if previous was successful.
        self.step_autoconf()

        auto_reconfigured_servers_after = self.query_status()
        assert server_statuses_equal(configured_servers_at_end, auto_reconfigured_servers_after)
