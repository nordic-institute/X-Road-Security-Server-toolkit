from tests.util.test_util import get_client, get_service_description, get_endpoint_service_clients, get_service_descriptions, get_service_clients
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.endpoint import EndpointController, EndpointListMapper, EndpointAccessListMapper
from xrdsst.controllers.service import ServiceController
from xrdsst.core.conf_keys import ConfKeysSecServerClients
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
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = ''
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
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["url"] = description_url[ssn]

    def step_add_service_description_fail_type_missing(self):
        types = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            types.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = ''
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
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = types[ssn]

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
                    description = get_service_description(self.test.config, client_id, ssn)
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
                    description = get_service_description(self.test.config, client_id, ssn)
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
                    description = get_service_description(self.test.config, client_id, ssn)
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
                        assert len(response) == 1
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == 'DEV:ORG:111:BUS'
                        assert response[0][
                                   "url"] == 'https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/modules/openapi-generator-gradle-plugin/samples/local-spec/petstore-v3.0.yaml'
                        assert response[0]["type"] == 'OPENAPI3'
                        assert response[0]["disabled"] is False
                        assert response[0]["services"] == 1
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
                        description = get_service_description(self.test.config, client_id, ssn)
                        response = service_controller.remote_list_services(configuration, security_server, client_id, [description["id"]])
                        assert len(response) == 1
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == 'DEV:ORG:111:BUS'
                        assert response[0]["service_id"] == 'DEV:ORG:111:BUS:Petstore'
                        assert response[0]["service_code"] == 'Petstore'
                        assert response[0]["timeout"] == 120
                        assert response[0]["url"] == 'http://petstore.xxx'
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
                        assert len(description) == 1
                        assert description[0]["client_id"] == client_id
                        assert description[0]["type"] == 'OPENAPI3'
                        assert len(description[0]["services"]) == 1
                        assert description[0]["services"][0]["service_code"] == 'Petstore'

                        service_controller.remote_update_service_descriptions(configuration,
                                                                              client_id,
                                                                              [description[0]["id"]],
                                                                              'NewPetstore',
                                                                              None)

                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert len(description) == 1
                        assert description[0]["client_id"] == client_id
                        assert description[0]["type"] == 'OPENAPI3'
                        assert len(description[0]["services"]) == 1
                        assert description[0]["services"][0]["service_code"] == 'NewPetstore'
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
                        assert len(description) == 1
                        assert description[0]["client_id"] == client_id
                        assert description[0]["type"] == 'OPENAPI3'
                        assert len(description[0]["services"]) == 1
                        assert description[0]["services"][0]["service_code"] == 'Petstore'

                        service_controller.remote_refresh_service_descriptions(configuration,
                                                                               client_id,
                                                                               [description[0]["id"]])

                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert len(description) == 1
                        assert description[0]["client_id"] == client_id
                        assert description[0]["type"] == 'OPENAPI3'
                        assert len(description[0]["services"]) == 1
                        assert description[0]["services"][0]["service_code"] == 'Petstore'
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
                        assert len(description) == 1
                        response = service_controller.remote_list_access_for_services(configuration, security_server, client_id, [description[0]["id"]])
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == 'DEV:ORG:111:BUS'
                        assert response[0]["service_id"] == 'DEV:ORG:111:BUS:Petstore'
                        assert response[0]["service_client_id"] == 'DEV:security-server-owners'
                        assert response[0]["name"] == 'Security server owners'
                        assert response[0]["type"] == ServiceClientType.GLOBALGROUP
                        service_controller.remote_delete_service_access(configuration,
                                                                        security_server,
                                                                        response[0]["service_id"],
                                                                        client_id,
                                                                        description[0]["id"],
                                                                        [response[0]["service_client_id"]])
                        response = service_controller.remote_list_access_for_services(configuration, security_server, client_id, [description[0]["id"]])
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
                        assert len(description) == 1
                        assert description[0]["disabled"] is False

                        service_controller.remote_disable_service_descriptions(configuration,
                                                                               client_id,
                                                                               [description[0]["id"]],
                                                                               'disable notice')

                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert len(description) == 1
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
                        assert len(description) == 1
                        response = service_controller.remote_list_service_descriptions(configuration, security_server, [client_id])

                        assert len(response) == 1
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == client_id
                        assert response[0]["type"] == 'OPENAPI3'
                        assert response[0]["services"] == 1

                        service_controller.remote_delete_service_descriptions(configuration, client_id, [description[0]["id"]])

                        description = get_service_descriptions(self.test.config, client_id, ssn)
                        assert description is None
                        response = service_controller.remote_list_service_descriptions(configuration, security_server, [client_id])
                        assert len(response) == 0
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
                        assert len(description) == 1
                        response = service_controller.remote_list_access_for_services(configuration, security_server, client_id, [description[0]["id"]])
                        assert response[0]["security_server"] == security_server["name"]
                        assert response[0]["client_id"] == 'DEV:ORG:111:BUS'
                        assert response[0]["service_id"] == 'DEV:ORG:111:BUS:Petstore'
                        assert response[0]["service_client_id"] == 'DEV:security-server-owners'
                        assert response[0]["name"] == 'Security server owners'
                        assert response[0]["type"] == ServiceClientType.GLOBALGROUP

                ssn = ssn + 1

    def step_add_service_endpoints_fail_endpoints_service_type_wsdl(self):
        service_type = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            service_type.append(security_server["clients"][0]["service_descriptions"][0]["type"])
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = 'WSDL'
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
                    description = get_service_description(self.test.config, client_id, ssn)
                    assert len(description["services"][0]["endpoints"]) == 4
            ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["clients"][0]["service_descriptions"][0]["type"] = service_type[ssn]

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
                    description = get_service_description(self.test.config, client_id, ssn)
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

    def step_endpoint_list(self):
        list_endpoints_dic = []
        with XRDSSTTest() as app:
            endpoint_controller = EndpointController()
            endpoint_controller.app = app
            endpoint_controller.load_config = (lambda: self.test.config)
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = endpoint_controller.create_api_config(security_server, self.test.config)
                endpoints_count = 0
                descriptions_ids = []
                for client in security_server["clients"]:
                    if client.get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE):
                        found_client = get_client(self.test.config, client, ssn)
                        descriptions = get_service_descriptions(self.test.config, found_client[0]["id"], ssn)
                        for description in descriptions:
                            descriptions_ids.append(description["id"])
                            for service in description["services"]:
                                endpoints_count = endpoints_count + len(service["endpoints"])
                endpoints_list = endpoint_controller.remote_list_endpoints(configuration, security_server["name"], descriptions_ids)
                for header in EndpointListMapper.headers():
                    assert header in endpoint_controller.app._last_rendered[0][0]

                assert len(endpoints_list) == endpoints_count
                assert len(endpoint_controller.app._last_rendered[0]) == (endpoints_count + 1)

                list_endpoints_dic.append({
                    'ss_name': security_server["name"],
                    'list_endpoints': endpoints_list
                })
                ssn = ssn + 1

        return list_endpoints_dic

    def step_endpoint_update(self):
        with XRDSSTTest() as app:
            endpoint_controller = EndpointController()
            endpoint_controller.app = app
            endpoint_controller.load_config = (lambda: self.test.config)
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = endpoint_controller.create_api_config(security_server, self.test.config)
                descriptions_ids = []
                for client in security_server["clients"]:
                    if client.get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE):
                        found_client = get_client(self.test.config, client, ssn)
                        descriptions = get_service_descriptions(self.test.config, found_client[0]["id"], ssn)
                        for description in descriptions:
                            descriptions_ids.append(description["id"])

                endpoints_list = endpoint_controller.remote_list_endpoints(configuration, security_server["name"], descriptions_ids)

                endpoints_no_generated = list(filter(lambda e: e["generated"] is False, endpoints_list))
                endpoint_update_id = endpoints_no_generated[0]["endpoint_id"]
                method = "PUT"
                path = "/updated_path"

                endpoint_controller.remote_update_endpoint(configuration, security_server["name"], endpoint_update_id, method, path)

                endpoints_list_after = endpoint_controller.remote_list_endpoints(configuration, security_server["name"], descriptions_ids)
                endpoint_after = list(filter(lambda e: e["endpoint_id"] == endpoint_update_id, endpoints_list_after))

                assert endpoint_after[0]["endpoint_method"] == method
                assert endpoint_after[0]["endpoint_path"] == path

                ssn = ssn + 1

    def step_endpoint_delete(self):
        with XRDSSTTest() as app:
            endpoint_controller = EndpointController()
            endpoint_controller.app = app
            endpoint_controller.load_config = (lambda: self.test.config)
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = endpoint_controller.create_api_config(security_server, self.test.config)
                descriptions_ids = []
                for client in security_server["clients"]:
                    if client.get(ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE):
                        found_client = get_client(self.test.config, client, ssn)
                        descriptions = get_service_descriptions(self.test.config, found_client[0]["id"], ssn)
                        for description in descriptions:
                            descriptions_ids.append(description["id"])

                endpoints_list = endpoint_controller.remote_list_endpoints(configuration, security_server["name"], descriptions_ids)

                endpoints_no_generated = list(filter(lambda e: e["generated"] is False, endpoints_list))
                endpoint_update_id = endpoints_no_generated[0]["endpoint_id"]
                endpoint_controller.remote_delete_endpoint(configuration, security_server["name"], endpoint_update_id)

                endpoints_list_after = endpoint_controller.remote_list_endpoints(configuration, security_server["name"], descriptions_ids)
                endpoint_after = list(filter(lambda e: e["endpoint_id"] == endpoint_update_id, endpoints_list_after))

                assert len(endpoint_after) == 0

                ssn = ssn + 1

    def step_endpoint_list_access(self, list_endpoints_dic):
        with XRDSSTTest() as app:
            endpoint_controller = EndpointController()
            endpoint_controller.app = app
            endpoint_controller.load_config = (lambda: self.test.config)
            for security_server in self.test.config["security_server"]:
                configuration = endpoint_controller.create_api_config(security_server, self.test.config)
                list_endpoints = list(filter(lambda e: e["ss_name"] == security_server["name"], list_endpoints_dic))[0]["list_endpoints"]
                endpoints_ids = [e["endpoint_id"] for e in list_endpoints]

                endpoint_access_list = endpoint_controller.remote_list_endpoint_access(configuration, security_server["name"], endpoints_ids)

                for header in EndpointAccessListMapper.headers():
                    assert header in endpoint_controller.app._last_rendered[0][0]

                assert len(endpoint_access_list) == len(endpoints_ids)
                assert len(endpoint_controller.app._last_rendered[0]) == (len(endpoints_ids) + 1)

    def step_endpoint_delete_access(self, list_endpoints_dic):
        access_rights = ['DEV:security-server-owners']
        with XRDSSTTest() as app:
            endpoint_controller = EndpointController()
            endpoint_controller.app = app
            endpoint_controller.load_config = (lambda: self.test.config)
            for security_server in self.test.config["security_server"]:
                configuration = endpoint_controller.create_api_config(security_server, self.test.config)
                list_endpoints = list(filter(lambda e: e["ss_name"] == security_server["name"], list_endpoints_dic))[0]["list_endpoints"]

                print("---------------------list endpoints------------------------------------------")
                print(list_endpoints)

                endpoints_for_delete = list(filter(lambda e: e["service_code"] == "Petstore", list_endpoints))

                print("---------------------endpoints for delete------------------------------------------")
                print(endpoints_for_delete)
                id_endpoints_for_delete = [e["endpoint_id"] for e in endpoints_for_delete]

                print("---------------------endpoints ids for delete------------------------------------------")
                print(id_endpoints_for_delete)

                endpoint_controller.remote_delete_endpoint_access(configuration, security_server["name"], id_endpoints_for_delete, access_rights)

                endpoint_list_after = endpoint_controller.remote_list_endpoint_access(configuration, security_server["name"], id_endpoints_for_delete)

                print("---------------------endpoints list after------------------------------------------")
                print(endpoint_list_after)

                for endpoint in endpoint_list_after:
                    assert access_rights[0] not in endpoint["access"]

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
        endpoint_list_dic = self.step_endpoint_list()
        self.step_endpoint_list_access(endpoint_list_dic)
        self.step_endpoint_delete_access(endpoint_list_dic)
        self.step_endpoint_update()
        self.step_endpoint_delete()
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
