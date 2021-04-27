from cement import ex
from xrdsst.api import ClientsApi, EndpointsApi, ServicesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.client import ClientController
from xrdsst.models import Endpoint, ServiceType
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts


class EndpointController(BaseController):
    class Meta:
        label = 'endpoint'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['endpoint.controller.description']

    @ex(label='add-endpoints', help="Add endpoints", arguments=[])
    def add_endpoints(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)
        self.add_service_endpoints(active_config)

    def add_service_endpoints(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1]]:
            BaseController.log_debug('Starting service description access adding process for security server: ' + security_server['name'])
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        for service_description in client["service_descriptions"]:
                            for endpoint in service_description["endpoints"]:
                                self.remote_add_service_endpoints(ss_api_config, security_server, client, service_description, endpoint)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_add_service_endpoints(self, ss_api_config, security_server_conf, client_conf, service_description_conf, endpoint_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
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
                            serviceId = service_description.services[0].id
                            endpoint = Endpoint(id=None, service_code=service_description_conf["rest_service_code"], method=endpoint_conf["method"], path=endpoint_conf["path"], generated= None)

                            try:
                                services_api = ServicesApi(ApiClient(ss_api_config))
                                response = services_api.add_endpoint(id=serviceId, body=endpoint)
                                if response:
                                    BaseController.log_info("Added service endpoint '" + endpoint.method + " " + endpoint.path + "' for service '" + serviceId + "'")
                            except ApiException as err:
                                if err.status == 409:
                                    BaseController.log_info("Service endpoint '" + endpoint.method + " " + endpoint.path + "' for service '" + serviceId + "' already added")
                                else:
                                    BaseController.log_api_error('ServicesApi->add_endpoint', err)
                except ApiException as find_err:
                    BaseController.log_api_error('ClientsApi->get_client_service_description', find_err)
        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_clients', find_err)
