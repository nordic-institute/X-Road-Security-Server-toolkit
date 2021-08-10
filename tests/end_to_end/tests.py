import json
import os
import subprocess
import sys
import unittest
import urllib3

from tests.end_to_end.admin_test import AdminTest
from tests.end_to_end.backup_test import BackupTest
from tests.end_to_end.certificate_test import CertificateTest
from tests.end_to_end.client_test import ClientTest
from tests.end_to_end.diagnostics_test import DiagnosticsTest
from tests.end_to_end.initialization_test import InitializationTest
from tests.end_to_end.member_test import MemberTest
from tests.end_to_end.service_endpoint_test import ServiceEndpointTest
from tests.end_to_end.keys_test import KeysTest
from tests.util.test_util import get_client, assert_server_statuses_transitioned
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.status import StatusController
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.core.util import revoke_api_key, get_admin_credentials, get_ssh_key, get_ssh_user
from xrdsst.main import XRDSSTTest
from xrdsst.models import ClientStatus
from tests.end_to_end.renew_certificate import RenewCertificate
from tests.end_to_end.local_group_test import LocalGroupTest
from tests.end_to_end.csr_test import CsrTest
from tests.end_to_end.instance_test import InstanceTest
from tests.end_to_end.security_server_test import SecurityServerTest
from tests.end_to_end.internal_tls_test import TlsTest


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

    def create_api_key(self, api_key, ssn):
        api_key_env_name = self.config["security_server"][ssn]["api_key"]
        os.environ[api_key_env_name] = api_key

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

        self.step_verify_initial_transient_api_keys()
        InitializationTest(self).test_run_configuration()
        InstanceTest(self).test_run_configuration()
        SecurityServerTest(self).test_run_configuration()
        ClientTest(self).test_run_configuration()
        CertificateTest(self).test_run_configuration()
        TlsTest(self).test_run_configuration()
        ServiceEndpointTest(self).test_run_configuration()
        AdminTest(self).test_run_configuration()
        MemberTest(self).test_run_configuration()
        DiagnosticsTest(self).test_run_configuration()
        RenewCertificate(self).test_run_configuration()
        LocalGroupTest(self).test_run_configuration()
        self.step_client_unregister()
        self.step_client_delete()
        KeysTest(self).test_run_configuration()
        CsrTest(self).test_run_configuration()
        BackupTest(self).test_run_configuration()
        configured_servers_at_end = self.query_status()
        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)
