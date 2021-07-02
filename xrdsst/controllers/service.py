from cement import ex
from xrdsst.api import ClientsApi, ServiceDescriptionsApi, ServicesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.core.util import parse_argument_list
from xrdsst.models import ServiceDescriptionAdd, ServiceClients, ServiceUpdate
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts
from xrdsst.core.conf_keys import ConfKeysSecServerClientServiceDesc, ConfKeysSecServerClients


class ServiceDescriptionListMapper:
    @staticmethod
    def headers():
        return ['SS', 'CLIENT', 'ID', 'URL', 'TYPE', 'DISABLED', 'SERVICES']

    @staticmethod
    def as_list(description):
        return [description.get('security_server'),
                description.get('client_id'),
                description.get('description_id'),
                description.get('url'),
                description.get('type'),
                description.get('disabled'),
                description.get('services')]

    @staticmethod
    def as_object(description):
        return {
            'security_server': description.get('security_server'),
            'client_id': description.get('client_id'),
            'description_id': description.get('description_id'),
            'url': description.get('url'),
            'type': description.get('type'),
            'disabled': description.get('disabled'),
            'services': description.get('services')
        }


class ServiceListMapper:
    @staticmethod
    def headers():
        return ['SS', 'CLIENT', 'DESCRIPTION', 'SERVICE', 'CODE', 'TIMEOUT', 'URL']

    @staticmethod
    def as_list(service):
        return [service.get('security_server'),
                service.get('client_id'),
                service.get('description_id'),
                service.get('service_id'),
                service.get('service_code'),
                service.get('timeout'),
                service.get('url')]

    @staticmethod
    def as_object(service):
        return {
            'security_server': service.get('security_server'),
            'client_id': service.get('client_id'),
            'description_id': service.get('description_id'),
            'service_id': service.get('service_id'),
            'service_code': service.get('service_code'),
            'timeout': service.get('timeout'),
            'url': service.get('url')
        }


class ServiceController(BaseController):
    class Meta:
        label = 'service'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['service.controller.description']

    SERVICE_DESCRIPTION_FOR = 'Service description for'
    WITH_ID = 'with id'

    @ex(help="Execute all sub-commands", arguments=[])
    def apply(self):
        self.add_description()
        self.enable_description()
        self.add_access()
        self.update_parameters()

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
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.add_access_rights(active_config)

    @ex(label='update-parameters', help="Update service parameters", arguments=[])
    def update_parameters(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.update_service_parameters(active_config)

    @ex(help="List service descriptions", arguments=[(['--client'], {'help': 'Client id', 'dest': 'client'})])
    def list_descriptions(self):
        active_config = self.load_config()

        if self.app.pargs.client is None:
            self.log_info('Client parameter is required for listing client service descriptions')
            return

        self.list_service_descriptions(active_config, self.app.pargs.client)

    @ex(help="List services", arguments=[(['--client'], {'help': 'Client id', 'dest': 'client'}),
                                         (['--description'], {'help': 'Service description id', 'dest': 'description'})])
    def list_services(self):
        active_config = self.load_config()

        if self.app.pargs.client is None:
            self.log_info('Client parameter is required for listing client service descriptions')
            return

        if self.app.pargs.description is None:
            self.log_info('Description parameter is required for listing service description services')
            return

        self.list_service_description_services(active_config, self.app.pargs.client, self.app.pargs.description)

    @ex(help="Delete service descriptions", arguments=[(['--client'], {'help': 'Client id', 'dest': 'client'}),
                                                       (['--description'], {'help': 'Service description id', 'dest': 'description'})])
    def delete_descriptions(self):
        active_config = self.load_config()

        if self.app.pargs.client is None:
            self.log_info('Client parameter is required for deleting service descriptions')
            return

        if self.app.pargs.description is None:
            self.log_info('Description parameter is required for deleting service descriptions')
            return

        self.delete_service_descriptions(active_config, self.app.pargs.client, self.app.pargs.description)

    def add_service_description(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting service description add process for security server: ' + security_server['name'])
            if "clients" in security_server:
                self.add_client_service_description(ss_api_config, security_server)
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def enable_service_description(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting service description enabling process for security server: ' + security_server['name'])
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if client.get("service_descriptions"):
                        for service_description in client["service_descriptions"]:
                            self.remote_enable_service_description(ss_api_config, security_server, client, service_description)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def add_access_rights(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting service description access adding process for security server: ' + security_server['name'])
            if "clients" in security_server:
                self.add_client_service_access_rights(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def update_service_parameters(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting service description updating parameters process for security server: ' + security_server['name'])
            if "clients" in security_server:
                self.update_client_service_parameters(ss_api_config, security_server)
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def add_client_service_description(self, ss_api_config, security_server):
        for client in security_server["clients"]:
            if client.get("service_descriptions"):
                for service_description in client["service_descriptions"]:
                    self.remote_add_service_description(ss_api_config, security_server, client, service_description)
            else:
                if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client:
                    BaseController.log_info(
                        "Skipping add service description for client: '%s', no service description defined" %
                        ClientController().get_client_conf_id(client))

    @staticmethod
    def remote_add_service_description(ss_api_config, security_server_conf, client_conf, service_description_conf):
        code = service_description_conf['rest_service_code'] if \
            ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_REST_SERVICE_CODE in service_description_conf else None
        description_add = ServiceDescriptionAdd(url=service_description_conf['url'],
                                                rest_service_code=code,
                                                ignore_warnings=True,
                                                type=service_description_conf['type'])
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                try:
                    response = clients_api.add_client_service_description(client.id, body=description_add)
                    if response:
                        BaseController.log_info(
                            "Added service description for client '" + client.id + "' with type '" + response.type + "' and url '" + response.url +
                            "' (got full id " + response.id + ")")
                except ApiException as err:
                    if err.status == 409:
                        BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client_controller.partial_client_id(client_conf) +
                                                "' with url '" + description_add.url +
                                                "' and type '" + description_add.type + "' already exists.")
                    else:
                        BaseController.log_api_error('ClientsApi->add_client_service_description', err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def remote_enable_service_description(self, ss_api_config, security_server_conf, client_conf, service_description_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                try:
                    service_description = self.get_client_service_description(clients_api, client, service_description_conf)
                    if service_description:
                        try:
                            service_descriptions_api.enable_service_description(service_description.id)
                            BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client_controller.partial_client_id(client_conf) +
                                                    "'" + ServiceController.WITH_ID + "'" + service_description.id + "' enabled successfully.")
                        except ApiException as err:
                            if err.status == 409:
                                BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client_controller.partial_client_id(client_conf) +
                                                        "'" + ServiceController.WITH_ID + "'" + service_description.id + "' already enabled.")
                            else:
                                BaseController.log_api_error('ServiceDescriptionsApi->enable_service_description', err)
                except ApiException as find_err:
                    BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION, find_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def add_client_service_access_rights(self, ss_api_config, security_server):
        for client in security_server["clients"]:
            if "service_descriptions" in client:
                for service_description in client["service_descriptions"]:
                    if self.has_service_access(service_description):
                        self.remote_add_access_rights(ss_api_config, security_server, client, service_description)
                    else:
                        BaseController.log_info(
                            "Skipping add service access rights for client: '%s', service '%s', no access rights defined" %
                            (ClientController().get_client_conf_id(client),
                             service_description["url"]))

    def remote_add_access_rights(self, ss_api_config, security_server_conf, client_conf, service_description_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                try:
                    service_description = self.get_client_service_description(clients_api, client, service_description_conf)
                    if service_description:
                        for service in service_description.services:
                            self.remote_add_access_rights_for_service(ss_api_config,
                                                                      service_description_conf,
                                                                      client_controller,
                                                                      clients_api,
                                                                      client,
                                                                      service)
                except ApiException as find_err:
                    BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION, find_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def remote_add_access_rights_for_service(self,
                                             ss_api_config,
                                             service_description_conf,
                                             client_controller,
                                             clients_api,
                                             client,
                                             service):
        try:
            services_api = ServicesApi(ApiClient(ss_api_config))
            access_list = service_description_conf["access"] if "access" in service_description_conf else []
            configurable_services = service_description_conf["services"] if "services" in service_description_conf else []
            for configurable_service in configurable_services:
                if service.service_code == configurable_service["service_code"]:
                    service_access_list = configurable_service["access"] if "access" in configurable_service else []
                    access_list = service_access_list if len(service_access_list) > 0 else access_list

            self.remote_add_access_from_access_list(client_controller,
                                                    clients_api,
                                                    services_api,
                                                    client,
                                                    service,
                                                    access_list)
        except ApiException as err:
            if err.status == 409:
                BaseController.log_info("Access rights for client '" + client.id + "' using service '" + service.id + "' already added")
            else:
                BaseController.log_api_error('ServicesApi->add_service_service_clients', err)

    @staticmethod
    def remote_add_access_from_access_list(client_controller,
                                           clients_api,
                                           services_api,
                                           client,
                                           service,
                                           access_list):
        if len(access_list) > 0:
            service_clients_candidates = client_controller.get_clients_service_client_candidates(clients_api, client.id, access_list)
            if len(service_clients_candidates) == 0:
                BaseController.log_info("Could not add access rights for client '" + client.id +
                                        "' for using service '"
                                        + service.id + "',service clients candidates not found)")
            else:
                response = services_api.add_service_service_clients(service.id,
                                                                    body=ServiceClients(items=service_clients_candidates))
                if response:
                    for service_clients in service_clients_candidates:
                        BaseController.log_info("Added access rights for client '" + service_clients.id +
                                                "' to use service '" + service.id + "' (full id " + response[0].id + ")")

    def update_client_service_parameters(self, ss_api_config, security_server):
        for client in security_server["clients"]:
            if "service_descriptions" in client:
                for service_description in client["service_descriptions"]:
                    if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES in service_description:
                        self.remote_update_service_parameters(ss_api_config, security_server, client, service_description)
                    else:
                        BaseController.log_info(
                            "Skipping update service parameters for client %s, service %s, no services defined" %
                            (ClientController().get_client_conf_id(client),
                             service_description["url"]))

    def list_service_descriptions(self, config, client):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_service_descriptions(ss_api_config, security_server, client)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_service_description_services(self, config, client, description):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_services(ss_api_config, security_server, client, description)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_service_descriptions(self, config, client, description):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_delete_service_descriptions(ss_api_config, client, description)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_update_service_parameters(self, ss_api_config, security_server_conf, client_conf, service_description_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                try:
                    service_description = self.get_client_service_description(clients_api, client, service_description_conf)
                    if service_description:
                        for service in service_description.services:
                            self.remote_update_service_parameter(ss_api_config, service_description_conf, service)
                except ApiException as find_err:
                    BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION, find_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    @staticmethod
    def remote_update_service_parameter(ss_api_config, service_description_conf, service):
        try:
            services_api = ServicesApi(ApiClient(ss_api_config))
            for configurable_service in service_description_conf["services"]:
                if service.service_code == configurable_service["service_code"]:
                    timeout = int(configurable_service["timeout"])
                    timeout_all = bool(service_description_conf["timeout_all"])
                    ssl_auth = bool(configurable_service["ssl_auth"])
                    ssl_auth_all = bool(service_description_conf["ssl_auth_all"])
                    url = configurable_service["url"]
                    url_all = bool(service_description_conf["url_all"])

                    service_update = ServiceUpdate(url=url,
                                                   timeout=timeout,
                                                   ssl_auth=ssl_auth,
                                                   url_all=url_all,
                                                   timeout_all=timeout_all,
                                                   ssl_auth_all=ssl_auth_all)
                    response = services_api.update_service(service.id, body=service_update)
                    if response:
                        BaseController.log_info("Updated service parameters for service '" + service.id +
                                                "' (got full id " + response.id + ")")
        except ApiException as err:
            BaseController.log_api_error('ServicesApi->update_service', err)

    def remote_list_service_descriptions(self, ss_api_config, security_server, client):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions_list = []
            render_data = []
            client_ids = parse_argument_list(client)
            for client_id in client_ids:
                service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
                for service_description in service_descriptions:
                    service_descriptions_list.append({'security_server': security_server["name"],
                                                      'client_id': client_id,
                                                      'description_id': service_description.id,
                                                      'url': service_description.url,
                                                      'type': service_description.type,
                                                      'disabled': service_description.disabled,
                                                      'services': len(service_description.services) if service_description.services else 0})
            if self.is_output_tabulated():
                render_data = [ServiceDescriptionListMapper.headers()]
                render_data.extend(map(ServiceDescriptionListMapper.as_list, service_descriptions_list))
            else:
                render_data.extend(map(ServiceDescriptionListMapper.as_object, service_descriptions_list))
            self.render(render_data)
            return service_descriptions_list
        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    def remote_list_services(self, ss_api_config, security_server, client, description):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            services_list = []
            render_data = []
            description_ids = parse_argument_list(description)
            service_descriptions = clients_api.get_client_service_descriptions(id=client)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    for service in service_description.services:
                        services_list.append({'security_server': security_server["name"],
                                              'client_id': client,
                                              'description_id': service_description.id,
                                              'service_id': service.id,
                                              'service_code': service.service_code,
                                              'timeout': service.timeout,
                                              'url': service.url})
            if self.is_output_tabulated():
                render_data = [ServiceListMapper.headers()]
                render_data.extend(map(ServiceListMapper.as_list, services_list))
            else:
                render_data.extend(map(ServiceListMapper.as_object, services_list))
            self.render(render_data)
            return services_list
        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    @staticmethod
    def remote_delete_service_descriptions(ss_api_config, client, description):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            description_ids = parse_argument_list(description)
            service_descriptions = clients_api.get_client_service_descriptions(id=client)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    try:
                        service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
                        service_descriptions_api.delete_service_description(id=service_description.id)
                        BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client +
                                                "'" + ServiceController.WITH_ID + "'" + service_description.id + "' deleted successfully.")
                    except ApiException as err:
                        BaseController.log_api_error('ServiceDescriptionsApi->delete_service_description', err)

        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    @staticmethod
    def get_client_service_description(clients_api, client, service_description_conf):
        url = service_description_conf['url']
        service_type = service_description_conf['type']
        service_descriptions = clients_api.get_client_service_descriptions(client.id)
        for service_description in service_descriptions:
            if service_description.url == url and service_description.type == service_type:
                return service_description

    @staticmethod
    def has_service_access(service_desc_conf):
        has_access = False
        if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS in service_desc_conf:
            if service_desc_conf[ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS] is not None:
                has_access = True
        else:
            if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES in service_desc_conf:
                for service in service_desc_conf[ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_SERVICES]:
                    if ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS in service and \
                            service[ConfKeysSecServerClientServiceDesc.CONF_KEY_SS_CLIENT_SERVICE_DESC_CLIENT_ACCESS] is not None:
                        has_access = True
        return has_access
