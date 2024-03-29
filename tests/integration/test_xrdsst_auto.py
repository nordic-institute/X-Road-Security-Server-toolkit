import copy
import os

import urllib3

from tests.integration.integration_base import IntegrationTestBase
from tests.integration.integration_ops import IntegrationOpBase
from tests.util.test_util import waitfor, auth_cert_registration_global_configuration_update_received, \
    assert_server_statuses_transitioned, api_GET


def assert_clients_transitioned(api_url, api_key):
    clients = api_GET(api_url, "clients", api_key)

    assert (2 == len(clients))
    assert (2 == len([x for x in clients if x['status'] == 'REGISTERED']))
    others = [x for x in clients if not x.get('subsystem_code', None)]
    subsystems = [x for x in clients if x.get('subsystem_code', None)]
    assert (1 == len(others))
    assert (1 == len(subsystems))

    assert (others[0]['owner'] is True)
    owner = others[0]
    sub = subsystems[0]

    assert (owner['has_valid_local_sign_cert'] is True)
    assert (owner['id'] == 'DEV:ORG:111')  # This DEV prefix unfortunately does depend on central server.
    assert (owner['instance_id'] == 'DEV')
    assert (owner['member_class'] == 'ORG')
    assert (owner['member_code'] == '111')
    assert (owner['member_name'] == 'NIIS')
    assert (owner['member_class'] == 'ORG')
    # Registration, ownership asserted already

    assert (sub['has_valid_local_sign_cert'] is True)
    assert (sub['connection_type'] == 'HTTP')
    assert (sub['id'] == 'DEV:ORG:111:BUS')  # This DEV prefix unfortunately does depend on central server.
    assert (sub['instance_id'] == 'DEV')
    assert (sub['member_class'] == 'ORG')
    assert (sub['member_code'] == '111')
    assert (sub['member_name'] == 'NIIS')
    assert (sub['owner'] is False)
    assert (sub['subsystem_code'] == 'BUS')
    # Registration asserted already


def assert_client_service_descs_transitioned(api_url, api_key):
    client_service_descs = api_GET(api_url, "clients/DEV:ORG:111:BUS/service-descriptions", api_key)

    assert (1 == len(client_service_descs))

    csds = client_service_descs[0]
    assert (1 == len(csds['services']))
    assert (csds['client_id'] == 'DEV:ORG:111:BUS')
    assert (csds['disabled'] is False)
    assert (csds['type'] == 'OPENAPI3')
    assert (csds['url'] == 'https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/modules/openapi-generator-gradle-plugin/samples/local-spec/petstore-v3.0.yaml')

    sd = csds['services'][0]
    assert (0 < len(sd['endpoints']))
    assert (sd['full_service_code'] == 'Petstore')
    assert (sd['service_code'] == 'Petstore')
    assert (sd['id'] == 'DEV:ORG:111:BUS:Petstore')
    # Skip 'ssl_auth' & 'timeout'


def assert_client_service_clients_transitioned(api_url, api_key):
    client_service_clients = api_GET(api_url, "services/DEV:ORG:111:BUS:Petstore/service-clients", api_key)

    assert (1 == len(client_service_clients))
    # Skip 'ssl_auth' & 'timeout'


def assert_non_status_ops_transitioned(api_url, api_key):
    assert_clients_transitioned(api_url, api_key)
    assert_client_service_descs_transitioned(api_url, api_key)
    assert_client_service_clients_transitioned(api_url, api_key)


class TestXrdsstAuto(IntegrationTestBase, IntegrationOpBase):
    __test__ = True

    def test_run_auto_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # Uninitialized security server can already have functioning API interface and status query must function
        unconfigured_servers_at_start = self.query_status()

        # Expected to run until the certificates that are not there
        conf = copy.deepcopy(self.config)
        self.step_autoconf()
        self.config = copy.deepcopy(conf)

        # Get signed certificates
        ssn = 0
        downloaded_csrs = self.step_cert_download_csrs()
        for security_server in self.config["security_server"]:
            signed_certs = self.step_acquire_certs(downloaded_csrs[(ssn * 3):(ssn * 3 + 3)], security_server)
            self.apply_cert_config(signed_certs, ssn)
            ssn = ssn + 1

        # Expected to import certificates, but not get further straight away, since registration globally is time-consuming.
        conf = copy.deepcopy(self.config)
        self.step_autoconf()
        self.config = copy.deepcopy(conf)

        # Wait for global configuration status updates
        for ssn in range(0, len(self.config["security_server"])):
            waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config, ssn), self.retry_wait, self.max_retries)
            self.query_status()

        # Now that registered auth cert is globally accepted, should proceed with everything else to successful end.
        self.step_autoconf()

        # configured_servers_at_end = self.query_status()
        # assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)

        # Verify non-base operation transitions
        # ssn = 0
        # for security_server in self.config["security_server"]:
        #    assert_non_status_ops_transitioned(security_server["url"], os.getenv(IntegrationTestBase.api_key_env[ssn], ""))
        #    ssn = ssn + 1
