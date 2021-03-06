from cement import ex
from xrdsst.api import ClientsApi, EndpointsApi, ServicesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.client import ClientController
from xrdsst.models import Endpoint, ServiceType, ServiceClients
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts

class EndpointController(BaseController):
    class Meta:
        label = 'endpoint'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['endpoint.controller.description']

    @ex(help="Add endpoints", arguments=[])
    def add(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)
        self.add_service_endpoints(active_config)

    @ex(help="Add access rights to endpoints ", arguments=[])
    def add_access(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)
        self.add_endpoint_access(active_config)

    def add_service_endpoints(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for service_description_dic in self.get_services_description(config):
            for endpoint_conf in service_description_dic["service_description"]["endpoints"]:
                self.remote_add_service_endpoints(service_description_dic["ss_api_config"], service_description_dic["security_server"], service_description_dic["client"], service_description_dic["service_description"], endpoint_conf)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def add_endpoint_access(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        for service_description_dic in self.get_services_description(config):
            self.remote_add_endpoints_access(service_description_dic["ss_api_config"], service_description_dic["security_server"],
                                             service_description_dic["client"], service_description_dic["service_description"])

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    @staticmethod
    def remote_add_service_endpoints(ss_api_config, security_server_conf, client_conf, service_description_conf, endpoint_conf):
        try:
            clients_api = ClientsApi(ApiClient(ss_api_config))
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, security_server_conf, client_conf)
            if client:
                try:
                    service_description = ServiceController().get_client_service_description(clients_api, client, service_description_conf)
                    if service_description:
                        if service_description.type == ServiceType().WSDL:
                            BaseController.log_info("Wrong service description, endpoints for WSDL services are not"
                                                    " allowed, skipped endpoint creation for service '" + service_description.url + "'")
                        else:
                            endpoint = Endpoint(id=None, service_code=service_description_conf["rest_service_code"], method=endpoint_conf["method"], path=endpoint_conf["path"], generated= None)

                            try:
                                services_api = ServicesApi(ApiClient(ss_api_config))
                                response = services_api.add_endpoint(id=service_description.services[0].id, body=endpoint)
                                if response:
                                    BaseController.log_info("Added service endpoint '" + endpoint.method + " " + endpoint.path + "' for service '" + service_description.services[0].id + "'")
                            except ApiException as err:
                                if err.status == 409:
                                    BaseController.log_info("Service endpoint '" + endpoint.method + " " + endpoint.path + "' for service '" + service_description.services[0].id + "' already added")
                                else:
                                    BaseController.log_api_error('ServicesApi->add_endpoint', err)
                except ApiException as find_err:
                    BaseController.log_api_error('ClientsApi->get_client_service_description', find_err)
        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_clients', find_err)

    @staticmethod
    def remote_add_endpoints_access(ss_api_config, security_server_conf, client_conf, service_description_conf):
        try:
            client_controller = ClientController()
            clients_api = ClientsApi(ApiClient(ss_api_config))
            client = client_controller.find_client(clients_api, security_server_conf, client_conf)
            if client:
                service_clients_candidates = client_controller.get_clients_service_client_candidates(clients_api, client.id, [])
                try:
                    service_controller = ServiceController()
                    clients_api = ClientsApi(ApiClient(ss_api_config))
                    service_description = service_controller.get_client_service_description(clients_api, client, service_description_conf)
                    if service_description.type != ServiceType().WSDL:
                        for endpoint_conf in service_description_conf["endpoints"]:
                            try:
                                access_list = endpoint_conf["access"] if endpoint_conf["access"] else []
                                if len(access_list) > 0:
                                    for access in access_list:
                                        candidate = [c for c in service_clients_candidates if c.id == access]
                                        if len(candidate) == 0:
                                            BaseController.log_info("Error adding client access rights '" + access + "' for the endpoint '"
                                                                    + endpoint_conf["method"] + " " + endpoint_conf["path"] + "' for service '" + service_description.id + "', no valid candidate found")
                                        else:

                                            endpoint = [e for e in service_description.services[0].endpoints if e.method == endpoint_conf["method"] and e.path == endpoint_conf["path"]]
                                            if len(endpoint) == 0:
                                                BaseController.log_info(
                                                    "Error adding client access rights '" + access + "' for the endpoint '" + endpoint_conf["method"] + " " + endpoint_conf["path"] + "' for service '" + service_description.id + "', endpoint not found")
                                            else:
                                                try:
                                                    endpoints_api = EndpointsApi(ApiClient(ss_api_config))
                                                    response = endpoints_api.add_endpoint_service_clients(endpoint[0].id, body=ServiceClients(items=candidate))
                                                    if response:
                                                        BaseController.log_info("Added client access rights: '"+candidate[0].id + "'for endpoint '" + endpoint[0].method +
                                                                                "' '" + endpoint[0].path + "' in service '" + service_description.services[0].id + "'")
                                                except ApiException as err:
                                                    if err.status == 409:
                                                        BaseController.log_info(
                                                            "Added client access rights: '" + candidate[
                                                                0].id + "'for endpoint '" + endpoint[0].method +
                                                            "' '" + endpoint[0].path + "' in service '" +
                                                            service_description.services[0].id + "' already added")
                                                    else:
                                                        BaseController.log_api_error('EndpointsApi->add_endpoint_service_clients', err)

                            except ApiException as find_err:
                                BaseController.log_api_error('ClientsApi->get_client_service_description', find_err)
                except ApiException as find_err:
                    BaseController.log_api_error('ClientsApi->get_client_service_description', find_err)
        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_clients', find_err)


    def get_services_description(self, config):
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting service description access adding process for security server: ' + security_server['name'])
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        for service_description in client["service_descriptions"]:
                            yield {'service_description': service_description, 'client': client, 'security_server': security_server, 'ss_api_config': ss_api_config}