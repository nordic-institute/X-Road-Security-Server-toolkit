from tests.util.test_util import get_client
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.service import ServiceController
from xrdsst.main import XRDSSTTest
from xrdsst.models import ClientStatus


class ClientTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_subsystem_add_client_fail_member_code_missing(self):
        member_code = []
        with XRDSSTTest() as app:

            ssn = 0
            for security_server in self.test.config["security_server"]:
                cln = 0
                for client in security_server["clients"]:
                    member_code.append(client["member_code"])
                    self.test.config["security_server"][ssn]["clients"][cln]["member_code"] = ''
                    cln = cln + 1
                ssn = ssn + 1

            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    response = client_controller.remote_add_client(configuration, client)
                    assert response is None
                ssn = ssn + 1

        ssn = 0
        idx = 0
        for security_server in self.test.config["security_server"]:
            cln = 0
            for client in security_server["clients"]:
                self.test.config["security_server"][ssn]["clients"][cln]["member_code"] = member_code[idx]
                cln = cln + 1
                idx = idx + 1
            ssn = ssn + 1

    def step_subsystem_add_client_fail_member_class_missing(self):
        member_class = []
        with XRDSSTTest() as app:

            ssn = 0
            for security_server in self.test.config["security_server"]:
                cln = 0
                for client in security_server["clients"]:
                    member_class.append(client["member_class"])
                    self.test.config["security_server"][ssn]["clients"][cln]["member_class"] = ''
                    cln = cln + 1
                ssn = ssn + 1

            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    response = client_controller.remote_add_client(configuration, client)
                    assert response is None
                ssn = ssn + 1

        ssn = 0
        idx = 0
        for security_server in self.test.config["security_server"]:
            cln = 0
            for client in security_server["clients"]:
                self.test.config["security_server"][ssn]["clients"][cln]["member_class"] = member_class[idx]
                cln = cln + 1
                idx = idx + 1
            ssn = ssn + 1

    def step_subsystem_register_fail_client_not_saved(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) == 0
                    client_controller.remote_register_client(configuration, security_server, client)
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) == 0
                ssn = ssn + 1

    def step_add_service_description_fail_client_not_saved(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        found_client = get_client(self.test.config, client, ssn)
                        assert len(found_client) == 0
                        response = service_controller.remote_add_service_description(configuration, client, service_description)
                        assert response is None
            ssn = ssn + 1

    def step_subsystem_add_client(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) == 0
                    response = client_controller.remote_add_client(configuration, client)
                    assert response is not None
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] != ClientStatus.GLOBAL_ERROR
                ssn = ssn + 1

    def client_step_make_owner(self):
        member = 'DEV:COM:222'
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(self.test.config["security_server"][0], self.test.config)
                client_controller.remote_make_member_owner(configuration, security_server["name"], member)

    def test_run_configuration(self):
        self.step_subsystem_add_client_fail_member_class_missing()
        self.step_subsystem_add_client_fail_member_code_missing()
        self.step_subsystem_register_fail_client_not_saved()
        self.step_add_service_description_fail_client_not_saved()
        self.step_subsystem_add_client()
        self.client_step_make_owner()
