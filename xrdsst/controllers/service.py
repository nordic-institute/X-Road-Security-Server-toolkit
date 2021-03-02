from datetime import datetime

from cement import ex
from xrdsst.api import ClientsApi, ServiceDescriptionsApi, ServicesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.models import ServiceDescriptionAdd, ServiceClient, ServiceClientType, ServiceClients
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts


class ServiceController(BaseController):
    class Meta:
        label = 'service'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['service.controller.description']

    @ex(help="Add service description", arguments=[])
    def add_description(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.add_service_description(active_config)

    @ex(help="Enable service description", arguments=[])
    def enable_description(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.enable_service_description(active_config)

    @ex(help="Add access rights for service", arguments=[])
    def add_access(self):
        self.add_access_rights(self.load_config())

    def add_service_description(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_debug('Starting service description add process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if client.get("service_descriptions"):
                        for service_description in client["service_descriptions"]:
                            self.remote_add_service_description(ss_configuration, security_server, client, service_description)

    def enable_service_description(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_debug('Starting service description enabling process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if client.get("service_descriptions"):
                        for service_description in client["service_descriptions"]:
                            self.remote_enable_service_description(ss_configuration, security_server, client, service_description)

    def add_access_rights(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting service description enabling process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        for service_description in client["service_descriptions"]:
                            self.remote_add_access_rights(ss_configuration, security_server, client, service_description)

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

    def remote_add_access_rights(self, ss_configuration, security_server_conf, client_conf, service_description_conf):
        clients_api = ClientsApi(ApiClient(ss_configuration))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, security_server_conf, client_conf)
            if client:
                try:
                    service_description = self.get_client_service_description(clients_api, client, service_description_conf)
                    if service_description:
                        for service in service_description.services:
                            try:
                                services_api = ServicesApi(ApiClient(ss_configuration))
                                service_client = ServiceClient(id=client.id,
                                                               name=client.member_name,
                                                               service_client_type=ServiceClientType.SUBSYSTEM)
                                service_clients = ServiceClients(items=[service_client])
                                response = services_api.add_service_service_clients(service.id, body=service_clients)
                                if response:
                                    BaseController.log_info("Added access rights for client '" + client.id +
                                                            "' to use service '" + service.id + "' (got full id " + response[0].id + ")")
                            except ApiException as err:
                                if err.status == 409:
                                    BaseController.log_info("Added access rights for client '" + client.id +
                                                            "' to use service '" + service.id + "' already added")
                                else:
                                    BaseController.log_api_error('ServicesApi->add_service_service_clients', err)
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
