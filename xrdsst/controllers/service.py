from cement import ex
from xrdsst.api import ClientsApi, ServiceDescriptionsApi, ServicesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.core.util import parse_argument_list, cut_big_string
from xrdsst.models import ServiceDescriptionAdd, ServiceClients, ServiceUpdate, ServiceDescriptionUpdate, ServiceType, ServiceDescriptionDisabledNotice, \
    ServiceClient
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
                cut_big_string(description.get('url'), 50),
                description.get('type'),
                description.get('disabled'),
                description.get('services')]

    @staticmethod
    def as_object(description):
        return {
            'security_server': description.get('security_server'),
            'client_id': description.get('client_id'),
            'description_id': description.get('description_id'),
            'url': cut_big_string(description.get('url'), 50),
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


class ServiceAccessListMapper:
    @staticmethod
    def headers():
        return ['SS', 'CLIENT', 'DESCRIPTION', 'SERVICE', 'SERVICE_CLIENT', 'NAME', 'RIGHTS_GIVEN', 'TYPE']

    @staticmethod
    def as_list(service):
        return [service.get('security_server'),
                service.get('client_id'),
                service.get('description_id'),
                service.get('service_id'),
                service.get('service_client_id'),
                service.get('name'),
                service.get('rights_given'),
                service.get('type')]

    @staticmethod
    def as_object(service):
        return {
            'security_server': service.get('security_server'),
            'client_id': service.get('client_id'),
            'description_id': service.get('description_id'),
            'service_id': service.get('service_id'),
            'service_client_id': service.get('service_client_id'),
            'name': service.get('name'),
            'rights_given': service.get('rights_given'),
            'type': service.get('type')
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
            BaseController.log_info('Client parameter is required for listing client service descriptions')
            return

        client_ids = parse_argument_list(self.app.pargs.client)

        self.list_service_descriptions(active_config, client_ids)

    @ex(help="List services", arguments=[(['--client'], {'help': 'Client id', 'dest': 'client'}),
                                         (['--description'], {'help': 'Service description id', 'dest': 'description'})])
    def list_services(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for listing service description services: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.list_service_description_services(active_config, self.app.pargs.client, description_ids)

    @ex(help="Delete service descriptions", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                       (['--client'], {'help': 'Client id', 'dest': 'client'}),
                                                       (['--description'], {'help': 'Service description id', 'dest': 'description'})])
    def delete_descriptions(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for deleting service descriptions: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.delete_service_descriptions(active_config, self.app.pargs.ss, self.app.pargs.client, description_ids)

    @ex(help="Update service descriptions", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                       (['--client'], {'help': 'Client id', 'dest': 'client'}),
                                                       (['--description'], {'help': 'Service description id', 'dest': 'description'}),
                                                       (['--code'], {'help': 'REST service code', 'dest': 'code'}),
                                                       (['--url'], {'help': 'Service description url', 'dest': 'url'})])
    def update_descriptions(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if self.app.pargs.code is None and self.app.pargs.url is None:
            missing_parameters.append('code' if self.app.pargs.code is None else 'url')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for updating service descriptions: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.update_service_descriptions(active_config,
                                         self.app.pargs.ss,
                                         self.app.pargs.client,
                                         description_ids,
                                         self.app.pargs.code,
                                         self.app.pargs.url)

    @ex(help="Refresh service descriptions", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                        (['--client'], {'help': 'Client id', 'dest': 'client'}),
                                                        (['--description'], {'help': 'Service description id', 'dest': 'description'})])
    def refresh_descriptions(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for refreshing service descriptions: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.refresh_service_descriptions(active_config,
                                          self.app.pargs.ss,
                                          self.app.pargs.client,
                                          description_ids)

    @ex(help="Disable service descriptions", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                        (['--client'], {'help': 'Client id', 'dest': 'client'}),
                                                        (['--description'], {'help': 'Service description id', 'dest': 'description'}),
                                                        (['--notice'], {'help': 'Disable notice', 'dest': 'notice'})])
    def disable_descriptions(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if self.app.pargs.notice is None:
            missing_parameters.append('notice')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for disabling service descriptions: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.disable_service_descriptions(active_config,
                                          self.app.pargs.ss,
                                          self.app.pargs.client,
                                          description_ids,
                                          self.app.pargs.notice)

    @ex(help="List service access", arguments=[(['--client'], {'help': 'Client id', 'dest': 'client'}),
                                               (['--description'], {'help': 'Service description id', 'dest': 'description'})])
    def list_access(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for listing access rights for services: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.list_access_rights(active_config, self.app.pargs.client, description_ids)

    @ex(help="Delete service access", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                 (['--client'], {'help': 'Client id', 'dest': 'client'}),
                                                 (['--description'], {'help': 'Service description id', 'dest': 'description'}),
                                                 (['--service'], {'help': 'Service id', 'dest': 'service'}),
                                                 (['--sclient'], {'help': 'Service client id', 'dest': 'sclient'})])
    def delete_access(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if self.app.pargs.service is None:
            missing_parameters.append('service')
        if self.app.pargs.sclient is None:
            missing_parameters.append('sclient')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for deleting access rights for services: %s' % missing_parameters)
            return

        service_client_ids = parse_argument_list(self.app.pargs.sclient)

        self.delete_access_rights(active_config,
                                  self.app.pargs.ss,
                                  self.app.pargs.client,
                                  self.app.pargs.description,
                                  self.app.pargs.service,
                                  service_client_ids)

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
                            self.remote_enable_service_description(ss_api_config, client, service_description)

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
                    self.remote_add_service_description(ss_api_config, client, service_description)
            else:
                if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client:
                    BaseController.log_info(
                        "Skipping add service description for client: '%s', no service description defined" %
                        ClientController().get_client_conf_id(client))

    @staticmethod
    def remote_add_service_description(ss_api_config, client_conf, service_description_conf):
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

    def remote_enable_service_description(self, ss_api_config, client_conf, service_description_conf):
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
                        self.remote_add_access_rights(ss_api_config, client, service_description)
                    else:
                        BaseController.log_info(
                            "Skipping add service access rights for client: '%s', service '%s', no access rights defined" %
                            (ClientController().get_client_conf_id(client),
                             service_description["url"]))

    def remote_add_access_rights(self, ss_api_config, client_conf, service_description_conf):
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
                        self.remote_update_service_parameters(ss_api_config, client, service_description)
                    else:
                        BaseController.log_info(
                            "Skipping update service parameters for client %s, service %s, no services defined" %
                            (ClientController().get_client_conf_id(client),
                             service_description["url"]))

    def list_service_descriptions(self, config, client_ids):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_service_descriptions(ss_api_config, security_server, client_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_service_description_services(self, config, client_id, description_ids):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_services(ss_api_config, security_server, client_id, description_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_service_descriptions(self, config, ss_name, client_id, description_ids):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_delete_service_descriptions(ss_api_config, client_id, description_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def update_service_descriptions(self, config, ss_name, client_id, description_ids, code, url):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_update_service_descriptions(ss_api_config, client_id, description_ids, code, url)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def refresh_service_descriptions(self, config, ss_name, client_id, description_ids):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_refresh_service_descriptions(ss_api_config, client_id, description_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def disable_service_descriptions(self, config, ss_name, client_id, description_ids, notice):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_disable_service_descriptions(ss_api_config, client_id, description_ids, notice)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_access_rights(self, config, client_id, description_ids):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_access_for_services(ss_api_config, security_server, client_id, description_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_access_rights(self, config, ss_name, client_id, description_id, service_id, service_client_ids):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_delete_access_for_services(ss_api_config,
                                                       security_server,
                                                       client_id,
                                                       description_id,
                                                       service_id,
                                                       service_client_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_update_service_parameters(self, ss_api_config, client_conf, service_description_conf):
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

    def remote_list_service_descriptions(self, ss_api_config, security_server, client_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions_list = []
            render_data = []
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

    def remote_list_services(self, ss_api_config, security_server, client_id, description_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            services_list = []
            render_data = []
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    for service in service_description.services:
                        services_list.append({'security_server': security_server["name"],
                                              'client_id': client_id,
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
    def remote_delete_service_descriptions(ss_api_config, client_id, description_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    try:
                        service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
                        service_descriptions_api.delete_service_description(id=service_description.id)
                        BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client_id +
                                                "'" + ServiceController.WITH_ID + "'" + service_description.id + "' deleted successfully.")
                    except ApiException as err:
                        BaseController.log_api_error('ServiceDescriptionsApi->delete_service_description', err)

        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    def remote_update_service_descriptions(self, ss_api_config, client_id, description_ids, new_code, new_url):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    response = self.remote_update_service_description(ss_api_config, service_description, new_url, new_code, client_id)
                    return response

        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    def remote_refresh_service_descriptions(self, ss_api_config, client_id, description_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    response = self.remote_refresh_service_description(ss_api_config, service_description, client_id)
                    return response

        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    def remote_disable_service_descriptions(self, ss_api_config, client_id, description_ids, notice):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    self.remote_disable_service_description(ss_api_config, service_description, client_id, notice)
        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    def remote_list_access_for_services(self, ss_api_config, security_server, client_id, description_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        access_list = []
        try:
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id in description_ids:
                    for service in service_description.services:
                        access_list.extend(self.remote_list_service_access(ss_api_config, security_server, service, client_id, service_description.id))
            return access_list
        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    def remote_delete_access_for_services(self,
                                          ss_api_config,
                                          security_server,
                                          client_id,
                                          description_id,
                                          service_id,
                                          service_client_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            service_descriptions = clients_api.get_client_service_descriptions(id=client_id)
            for service_description in service_descriptions:
                if service_description.id == description_id:
                    self.remote_delete_service_access(ss_api_config,
                                                      security_server,
                                                      service_id,
                                                      client_id,
                                                      description_id,
                                                      service_client_ids)
        except ApiException as err:
            BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS, err)

    @staticmethod
    def remote_update_service_description(ss_api_config, service_description, new_url, new_code, client):
        try:
            service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
            if service_description.type is not ServiceType.WSDL:
                service_description_update = ServiceDescriptionUpdate(url=new_url if new_url is not None else service_description.url,
                                                                      rest_service_code=service_description.services[0].service_code,
                                                                      new_rest_service_code=new_code,
                                                                      type=service_description.type,
                                                                      ignore_warnings=True)
            else:
                service_description_update = ServiceDescriptionUpdate(url=new_url if new_url is not None else service_description.url,
                                                                      type=service_description.type,
                                                                      ignore_warnings=True)
            response = service_descriptions_api.update_service_description(service_description.id, body=service_description_update)
            BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client +
                                    "'" + ServiceController.WITH_ID + "'" + service_description.id + "' updated successfully.")
            return response
        except ApiException as err:
            BaseController.log_api_error('ServiceDescriptionsApi->update_service_description', err)

    @staticmethod
    def remote_refresh_service_description(ss_api_config, service_description, client_id):
        try:
            service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
            response = service_descriptions_api.refresh_service_description(service_description.id)
            BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client_id +
                                    "'" + ServiceController.WITH_ID + "'" + service_description.id + "' refreshed successfully.")
            return response
        except ApiException as err:
            BaseController.log_api_error('ServiceDescriptionsApi->refresh_service_description', err)

    @staticmethod
    def remote_disable_service_description(ss_api_config, service_description, client_id, notice):
        try:
            service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
            service_description_disabled_notice = ServiceDescriptionDisabledNotice(disabled_notice=notice)
            service_descriptions_api.disable_service_description(service_description.id, body=service_description_disabled_notice)
            BaseController.log_info(ServiceController.SERVICE_DESCRIPTION_FOR + "'" + client_id +
                                    "'" + ServiceController.WITH_ID + "'" + service_description.id + "' disabled successfully.")
        except ApiException as err:
            BaseController.log_api_error('ServiceDescriptionsApi->disable_service_description', err)

    def remote_list_service_access(self, ss_api_config, security_server, service, client_id, description_id):
        services_api = ServicesApi(ApiClient(ss_api_config))
        try:
            client_ids = parse_argument_list(client_id)
            access_list = []
            render_data = []
            for client_id in client_ids:
                service_clients = services_api.get_service_service_clients(id=service.id)
                for service_client in service_clients:
                    access_list.append({'security_server': security_server["name"],
                                        'client_id': client_id,
                                        'description_id': description_id,
                                        'service_id': service.id,
                                        'service_client_id': service_client.id,
                                        'name': service_client.name,
                                        'rights_given': service_client.rights_given_at.strftime("%Y/%m/%d"),
                                        'type': service_client.service_client_type})
            if self.is_output_tabulated():
                render_data = [ServiceAccessListMapper.headers()]
                render_data.extend(map(ServiceAccessListMapper.as_list, access_list))
            else:
                render_data.extend(map(ServiceAccessListMapper.as_object, access_list))
            self.render(render_data)
            return access_list
        except ApiException as err:
            BaseController.log_api_error('ServicesApi->get_service_service_clients', err)

    @staticmethod
    def remote_delete_service_access(ss_api_config,
                                     security_server,
                                     service_id,
                                     client_id,
                                     description_id,
                                     service_client_ids):
        for service_client_id in service_client_ids:
            try:
                services_api = ServicesApi(ApiClient(ss_api_config))
                service_clients = services_api.get_service_service_clients(id=service_id)
                if service_clients is None or len(service_clients) == 0:
                    BaseController.log_info("Service client '" + service_client_id + "' not found")
                for service_client in service_clients:
                    if service_client_id == service_client.id:
                        sc = ServiceClient(id=service_client.id,
                                           name=service_client.name,
                                           local_group_code=service_client.local_group_code,
                                           service_client_type=service_client.service_client_type,
                                           rights_given_at=service_client.rights_given_at)
                        services_api.delete_service_service_clients(id=service_id, body=ServiceClients(items=[sc]))
                        BaseController.log_info("Service client '" + service_client_id + "' for security server '" +
                                                security_server["name"] + "'" + " client '" + client_id + "' service description '" +
                                                description_id + "'" + " service '" + service_id + "' deleted successfully")
            except ApiException as err:
                BaseController.log_api_error('ServicesApi->delete_service_service_clients', err)

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
