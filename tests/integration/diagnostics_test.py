from xrdsst.controllers.base import BaseController
from xrdsst.controllers.diagnostics import DiagnosticsController
from xrdsst.main import XRDSSTTest


class DiagnosticsTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_list_global_conf_diagnostics(self):
        with XRDSSTTest() as app:
            base = BaseController()
            diagnostics_controller = DiagnosticsController()
            diagnostics_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = diagnostics_controller.remote_list_global_configuration(configuration, security_server)
                assert len(response) == 1
                assert response[0]["status_class"] == 'OK'
                assert response[0]["status_code"] == 'SUCCESS'

    def step_list_ocsp_responders_diagnostics(self):
        with XRDSSTTest() as app:
            base = BaseController()
            diagnostics_controller = DiagnosticsController()
            diagnostics_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = diagnostics_controller.remote_list_ocsp_responders(configuration, security_server)
                assert len(response) == 2
                assert response[0]["name"] == 'CN=X-Road CA G1, O=X-Road Test'
                assert response[0]["url"] == 'http://dev-cs.i.x-road.rocks:8888/G1/'
                assert response[0]["status_class"] is not None
                assert response[0]["status_code"] is not None

    def step_list_timestamping_services_diagnostics(self):
        with XRDSSTTest() as app:
            base = BaseController()
            diagnostics_controller = DiagnosticsController()
            diagnostics_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = diagnostics_controller.remote_list_timestamping_services(configuration, security_server)
                assert len(response) == 1
                assert response[0]["url"] == 'http://dev-cs.i.x-road.rocks:8899'
                assert response[0]["status_class"] is not None
                assert response[0]["status_code"] is not None

    def test_run_configuration(self):
        self.step_list_global_conf_diagnostics()
        self.step_list_ocsp_responders_diagnostics()
        self.step_list_timestamping_services_diagnostics()
