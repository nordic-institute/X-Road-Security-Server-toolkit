from tests.util.test_util import get_endpoint_service_clients, get_client, get_service_description, get_service_descriptions, get_service_clients
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.endpoint import EndpointController
from xrdsst.controllers.service import ServiceController
from xrdsst.main import XRDSSTTest
from xrdsst.models import ServiceClientType, ClientStatus


class ServiceEndpointTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_subsystem_register(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] != ClientStatus.GLOBAL_ERROR
                    client_controller.remote_register_client(configuration, security_server, client)
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["status"] != ClientStatus.GLOBAL_ERROR
                ssn = ssn + 1

    def step_subsystem_update_parameters(self):
        connection_type = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            connection_type.append(security_server["clients"][0]["connection_type"])
            connection_type.append(security_server["clients"][1]["connection_type"])
            ssn = ssn + 1

        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = client_controller.create_api_config(security_server, self.test.config)
                cln = 0
                for client in security_server["clients"]:
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["connection_type"] == 'HTTP'
                    self.test.config["security_server"][ssn]["clients"][cln]["connection_type"] = 'HTTPS'
                    client_controller.remote_update_client(configuration, security_server, client)
                    found_client = get_client(self.test.config, client, ssn)
                    assert len(found_client) > 0
                    assert found_client[0]["connection_type"] == 'HTTPS'
                    cln = cln + 1
                ssn = ssn + 1

            for ssn in range(0, len(self.test.config["security_server"])):
                self.test.config["security_server"][ssn]["clients"][0]["connection_type"] = connection_type[ssn]
                self.test.config["security_server"][ssn]["clients"][1]["connection_type"] = connection_type[ssn]

    def step_add_service_description_fail_url_missing(self):
        description_url = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            description_url.append(security_server["clients"][0]["service_descriptions"][0]["url"])
            description_url.append(security_server["clients"][0]["service_descriptions"][1]["url"])
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = ''
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["url"] = ''
            ssn = ssn + 1

        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, client, service_description)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = description_url[0]
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["url"] = description_url[1]

    def step_add_service_description_fail_type_missing(self):
        types = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            types.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            types.append(security_server["clients"][0]["service_descriptions"][1]["type"])
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = ''
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = ''
            ssn = ssn + 1

        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, client, service_description)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = types[0]
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = types[1]

    def step_enable_service_description_fail_service_description_not_added(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    assert description is None
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_enable_service_description(configuration, client, service_description)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    assert description is None
            ssn = ssn + 1

    def step_add_service_description(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_service_description(configuration, client, service_description)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    assert description["disabled"] is True
            ssn = ssn + 1

    def step_enable_service_description(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.test.config, client_id, ssn)
                    for description in descriptions:
                        assert description["disabled"] is True
                        for service_description in client["service_descriptions"]:
                            service_controller.remote_enable_service_description(configuration, client, service_description)
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_description(self.test.config, client_id, ssn)
                        assert description["disabled"] is False
            ssn = ssn + 1

    def step_add_service_access(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_add_access_rights(configuration, client, service_description)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    service_clients = get_service_clients(self.test.config, description["services"][0]["id"], ssn)
                    assert len(service_clients) == 1
            ssn = ssn + 1

    def step_update_service_parameters(self):
        service_controller = ServiceController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.test.config, client_id, ssn)
                    for description in descriptions:
                        if description["type"] != "WSDL":
                            assert description["services"][0]["timeout"] == 60
                            assert description["services"][0]["url"] == 'http://petstore.swagger.io/v1'
            ssn = ssn + 1

        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = service_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        service_controller.remote_update_service_parameters(configuration, client, service_description)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.test.config, client_id, ssn)
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
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
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
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)

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
        for security_server in self.test.config["security_server"]:
            rest_service_code.append(security_server["clients"][0]["service_descriptions"][0]["rest_service_code"])
            ssn = ssn + 1

        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)
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

                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[1]["client_id"] == client_id
                        assert description[1]["type"] == 'OPENAPI3'
                        assert len(description[1]["services"]) == 1
                        assert description[1]["services"][0]["service_code"] == 'NewPetstore'
                ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["rest_service_code"] = rest_service_code[0]

    def step_refresh_service_description(self):
        with XRDSSTTest() as app:
            base = BaseController()
            service_controller = ServiceController()
            service_controller.app = app
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[1]["client_id"] == client_id
                        assert description[1]["type"] == 'OPENAPI3'
                        assert len(description[1]["services"]) == 1
                        assert description[1]["services"][0]["service_code"] == 'Petstore'

                        service_controller.remote_refresh_service_descriptions(configuration,
                                                                               client_id,
                                                                               [description[0]["id"]])

                        description = get_service_descriptions(self.test.config, client_id, ssn)
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
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)
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
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert len(description) == 2
                        assert description[0]["disabled"] is False

                        service_controller.remote_disable_service_descriptions(configuration,
                                                                               client_id,
                                                                               [description[0]["id"]],
                                                                               'disable notice')

                        description = get_service_descriptions(self.test.config, client_id, ssn)
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
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)
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

                        description = get_service_descriptions(self.test.config, client_id, ssn)
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
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        found_client = get_client(self.test.config, client, ssn)
                        client_id = found_client[0]['id']
                        description = get_service_descriptions(self.test.config, client_id, ssn)
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

    def step_add_service_endpoints_fail_endpoints_service_type_wsdl(self):
        service_type = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            service_type.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            service_type.append(security_server["clients"][0]["service_descriptions"][1]["type"])
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = 'WSDL'
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = 'WSDL'
            ssn = ssn + 1

        endpoint_controller = EndpointController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        if "endpoints" in service_description:
                            for endpoint in service_description["endpoints"]:
                                endpoint_controller.remote_add_service_endpoints(configuration, client, service_description, endpoint)
                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_descriptions(self.test.config, client_id, ssn)
                    assert len(description[0]["services"][0]["endpoints"]) == 1
                    assert len(description[1]["services"][0]["endpoints"]) == 4
            ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = service_type[0]
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][1]["type"] = service_type[1]

    def step_add_service_endpoints(self):
        endpoint_controller = EndpointController()
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_descriptions" in client:
                    for service_description in client["service_descriptions"]:
                        if "endpoints" in service_description:
                            for endpoint in service_description["endpoints"]:
                                endpoint_controller.remote_add_service_endpoints(configuration, client, service_description, endpoint)

                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    descriptions = get_service_descriptions(self.test.config, client_id, ssn)
                    for description in descriptions:
                        if description["type"] != "WSDL":
                            assert len(description["services"][0]["endpoints"]) == 5
                            assert str(description["services"][0]["endpoints"][4]["path"]) == "/testPath"
                            assert str(description["services"][0]["endpoints"][4]["method"]) == "POST"
            ssn = ssn + 1

    def step_add_endpoints_access(self):
        ssn = 0
        endpoint_controller = EndpointController()
        for security_server in self.test.config["security_server"]:
            configuration = endpoint_controller.create_api_config(security_server, self.test.config)
            for client in security_server["clients"]:
                if "service_description" in client:
                    for service_description in client["service_descriptions"]:
                        endpoint_controller.remote_add_endpoints_access(configuration, client, service_description)

                    found_client = get_client(self.test.config, client, ssn)
                    client_id = found_client[0]['id']
                    description = get_service_description(self.test.config, client_id, ssn)
                    service_clients = get_endpoint_service_clients(self.test.config, description["services"][0]["endpoints"][4]["id"], ssn)
                    assert len(service_clients) == 1
                    assert str(service_clients[0]["id"]) == "DEV:security-server-owners"
            ssn = ssn + 1

    def test_run_configuration(self):
        self.step_add_service_description_fail_url_missing()
        self.step_add_service_description_fail_type_missing()
        self.step_enable_service_description_fail_service_description_not_added()
        self.step_add_service_description()
        self.step_enable_service_description()
        self.step_add_service_access()
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
