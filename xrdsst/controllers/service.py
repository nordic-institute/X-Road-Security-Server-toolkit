from cement import ex
from xrdsst.api import ClientsApi, ServiceDescriptionsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.models import ServiceDescriptionAdd
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts


class ServiceController(BaseController):
    class Meta:
        label = 'service'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['service.controller.description']

    @ex(label='add-description', help="Add service description", arguments=[])
    def add_description(self):
        self.add_service_description(self.load_config())

    @ex(label='enable-description', help="Enable service description", arguments=[])
    def enable_description(self):
        self.enable_service_description(self.load_config())

    def add_service_description(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting service description add process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        for service_description in client["service_descriptions"]:
                            self.remote_add_service_description(ss_configuration, security_server, client, service_description)

    def enable_service_description(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting service description enabling process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        for service_description in client["service_descriptions"]:
                            self.remote_enable_service_description(ss_configuration, security_server, client, service_description)

    @staticmethod
    def remote_add_service_description(ss_configuration, security_server_conf, client_conf, service_description_conf):
        code = service_description_conf['rest_service_code'] if service_description_conf['rest_service_code'] else None
        description_add = ServiceDescriptionAdd(url=service_description_conf['url'],
                                                rest_service_code=code,
                                                ignore_warnings=True,
                                                type=service_description_conf['type'])
        clients_api = ClientsApi(ApiClient(ss_configuration))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, security_server_conf, client_conf)
            if client:
                try:
                    response = clients_api.add_client_service_description(client.id, body=description_add)
                    if response:
                        BaseController.log_info("Added service description with type '" + response.type + "' and url '" + response.url +
                                                "' (got full id " + response.id + ")")
                except ApiException as err:
                    if err.status == 409:
                        BaseController.log_info("Service description for '" + client_controller.partial_client_id(client_conf) +
                                                "' with url '" + description_add.url +
                                                "' and type '" + description_add.type + "' already exists.")
                    else:
                        BaseController.log_api_error('ClientsApi->add_client_service_description', err)
        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_clients', find_err)

    def remote_enable_service_description(self, ss_configuration, security_server_conf, client_conf, service_description_conf):
        clients_api = ClientsApi(ApiClient(ss_configuration))
        service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_configuration))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, security_server_conf, client_conf)
            if client:
                try:
                    service_description = self.get_client_service_description(clients_api, client, service_description_conf)
                    if service_description:
                        try:
                            service_descriptions_api.enable_service_description(service_description.id)
                            BaseController.log_info("Service description for '" + client_controller.partial_client_id(client_conf) +
                                                    "' with id: '" + service_description.id + "' enabled successfully.")
                        except ApiException as err:
                            if err.status == 409:
                                BaseController.log_info("Service description for '" + client_controller.partial_client_id(client_conf) +
                                                        "' with id: '" + service_description.id + "' already enabled.")
                            else:
                                BaseController.log_api_error('ServiceDescriptionsApi->enable_service_description', err)
                except ApiException as find_err:
                    BaseController.log_api_error('ClientsApi->get_client_service_description', find_err)
        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_clients', find_err)

    @staticmethod
    def get_client_service_description(clients_api, client, service_description_conf):
        url = service_description_conf['url']
        service_type = service_description_conf['type']
        service_descriptions = clients_api.get_client_service_descriptions(client.id)
        for service_description in service_descriptions:
            if service_description.url == url and service_description.type == service_type:
                return service_description
