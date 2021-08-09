import urllib3

from tests.integration.backup_test import BackupTest
from tests.integration.certificate_test import CertificateTest
from tests.integration.client_test import ClientTest
from tests.integration.diagnostics_test import DiagnosticsTest
from tests.integration.initialization_test import InitializationTest
from tests.integration.integration_base import IntegrationTestBase
from tests.integration.integration_ops import IntegrationOpBase
from tests.integration.member_test import MemberTest
from tests.integration.service_endpoint_test import ServiceEndpointTest
from tests.util.test_util import assert_server_statuses_transitioned
from xrdsst.controllers.status import ServerStatus
from tests.integration.renew_certificate_test import RenewCertificate
from tests.integration.local_group_test import LocalGroupTest
from tests.integration.keys_test import KeysTest
from tests.integration.csr_test import CsrTest
from tests.integration.instance_test import InstanceTest
from tests.integration.security_server_test import SecurityServerTest
from tests.integration.tls_test import TlsTest


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

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        unconfigured_servers_at_start = self.query_status()

        InitializationTest(self).test_run_configuration()
        self.query_status()

        InstanceTest(self).test_run_configuration()
        self.query_status()

        SecurityServerTest(self).test_run_configuration()
        self.query_status()

        ClientTest(self).test_run_configuration()
        self.query_status()

        CertificateTest(self).test_run_configuration()
        self.query_status()

        TlsTest(self).test_run_configuration()
        self.query_status()

        ServiceEndpointTest(self).test_run_configuration()
        self.query_status()

        MemberTest(self).test_run_configuration()
        self.query_status()

        BackupTest(self).test_run_configuration()
        self.query_status()

        DiagnosticsTest(self).test_run_configuration()
        self.query_status()

        LocalGroupTest(self).test_run_configuration()
        self.query_status()

        RenewCertificate(self).test_run_configuration()
        self.query_status()

        KeysTest(self).test_run_configuration()
        self.query_status()

        CsrTest(self).test_run_configuration()
        self.query_status()

        configured_servers_at_end = self.query_status()
        assert_server_statuses_transitioned(unconfigured_servers_at_start, configured_servers_at_end)
