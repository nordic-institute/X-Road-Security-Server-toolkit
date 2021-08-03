from xrdsst.controllers.security_server import SecurityServerController, SecurityServerListMapper
from xrdsst.main import XRDSSTTest


class SecurityServerTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_security_servers_list(self):
        with XRDSSTTest() as app:
            security_server_controller = SecurityServerController()
            security_server_controller.app = app
            security_server_controller.load_config = (lambda: self.test.config)

            security_servers_list = security_server_controller.list_security_servers(self.test.config)
            for header in SecurityServerListMapper.headers():
                assert header in security_server_controller.app._last_rendered[0][0]
            assert len(security_server_controller.app._last_rendered[0]) == (len(security_servers_list) + 1)

    def test_run_configuration(self):
        self.step_security_servers_list()
