from cement import ex
from xrdsst.api import ClientsApi, EndpointsApi, ServicesApi, ServiceDescriptionsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.client import ClientController
from xrdsst.models import Endpoint, ServiceType, ServiceClients, EndpointUpdate
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts
from xrdsst.core.util import parse_argument_list, cut_big_string


class EndpointListMapper:
    @staticmethod
    def headers():
        return ['ENDPOINT ID', 'PATH', 'METHOD', 'SERVICE CODE', 'CLIENT', 'SERVICE DESCRIPTION', 'TYPE', 'GENERATED']

    @staticmethod
    def as_list(endpoint):
        return [endpoint.get('endpoint_id'),
                endpoint.get('endpoint_method'),
                endpoint.get('endpoint_path'),
                endpoint.get('service_code'),
                endpoint.get('client'),
                endpoint.get('service_description'),
                endpoint.get('description_type'),
                endpoint.get('generated')]

    @staticmethod
    def as_object(endpoint):
        return {
            'endpoint_id': endpoint.get('endpoint_id'),
            'endpoint_method': endpoint.get('endpoint_method'),
            'endpoint_path': endpoint.get('endpoint_path'),
            'service_code': endpoint.get('service_code'),
            'client': endpoint.get('client'),
            'service_description': endpoint.get('service_description'),
            'description_type': endpoint.get('description_type'),
            'generated': endpoint.get('generated')
        }


class EndpointAccessListMapper:
    @staticmethod
    def headers():
        return ['ENDPOINT ID', 'ENDPOINT', 'SERVICE CODE', 'ACCESS RIGHTS']

    @staticmethod
    def as_list(endpoint):
        return [endpoint.get('endpoint_id'),
                endpoint.get('endpoint'),
                endpoint.get('service_code'),
                endpoint.get('access')]

    @staticmethod
    def as_object(endpoint):
        return {
            'endpoint_id': endpoint.get('endpoint_id'),
            'endpoint': endpoint.get('endpoint'),
            'service_code': endpoint.get('service_code'),
            'access': endpoint.get('access')
        }


class EndpointController(BaseController):
    class Meta:
        label = 'endpoint'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['endpoint.controller.description']

    FOR_SERVICE = 'for service'

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

    @ex(help="List endpoints", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                          (['--description'], {'help': 'Service description ids', 'dest': 'description'})
                                          ])
    def list(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.description is None:
            missing_parameters.append('description')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for listing endpoints: %s' % missing_parameters)
            return

        description_ids = parse_argument_list(self.app.pargs.description)

        self.list_endpoints(active_config, self.app.pargs.ss, description_ids)

    @ex(help="Update endpoints", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                            (['--endpoint'], {'help': 'Endpoint id', 'dest': 'endpoint'}),
                                            (['--method'], {'help': 'Endpoint method', 'dest': 'method'}),
                                            (['--path'], {'help': 'Endpoint path', 'dest': 'path'})
                                            ])
    def update(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.endpoint is None:
            missing_parameters.append('endpoint')
        if self.app.pargs.method is None:
            missing_parameters.append('method')
        if self.app.pargs.path is None:
            missing_parameters.append('path')

        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for updating endpoints: %s' % missing_parameters)
            return

        self.update_endpoint(active_config, self.app.pargs.ss, self.app.pargs.endpoint, self.app.pargs.method, self.app.pargs.path)

    @ex(help="Delete endpoints", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                            (['--endpoint'], {'help': 'Endpoint id', 'dest': 'endpoint'})
                                            ])
    def delete(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.endpoint is None:
            missing_parameters.append('endpoint')

        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for deleting endpoints: %s' % missing_parameters)
            return

        self.delete_endpoint(active_config, self.app.pargs.ss, self.app.pargs.endpoint)

    @ex(help="List endpoints access", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                 (['--endpoint'], {'help': 'Endpoint id(s)', 'dest': 'endpoint'})
                                                 ])
    def list_access(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.endpoint is None:
            missing_parameters.append('endpoint')

        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for listing endpoints access: %s' % missing_parameters)
            return
        endpoint_ids = parse_argument_list(self.app.pargs.endpoint)

        self.list_endpoints_access(active_config, self.app.pargs.ss, endpoint_ids)

    @ex(help="Delete endpoints access rights", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                                          (['--endpoint'], {'help': 'Endpoint id(s)', 'dest': 'endpoint'}),
                                                          (['--access'], {'help': 'Endpoint id(s)', 'dest': 'access'})
                                                          ])
    def delete_access(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.endpoint is None:
            missing_parameters.append('endpoint')
        if self.app.pargs.access is None:
            missing_parameters.append('access')

        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for deleting endpoints access: %s' % missing_parameters)
            return
        endpoint_ids = parse_argument_list(self.app.pargs.endpoint)
        access_rights = parse_argument_list(self.app.pargs.access)

        self.delete_endpoints_access(active_config, self.app.pargs.ss, endpoint_ids, access_rights)

    def add_service_endpoints(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for service_description_dic in self.get_services_description(config):
            if "endpoints" in service_description_dic["service_description"]:
                for endpoint_conf in service_description_dic["service_description"]["endpoints"]:
                    self.remote_add_service_endpoints(service_description_dic["ss_api_config"],
                                                      service_description_dic["client"],
                                                      service_description_dic["service_description"],
                                                      endpoint_conf)
            else:
                if service_description_dic["service_description"]["type"] != ServiceType().WSDL:
                    BaseController.log_info(
                        "Skipping endpoint creation for client '%s', service '%s', no endpoints defined" %
                        (ClientController().get_client_conf_id(service_description_dic["client"]),
                         service_description_dic["service_description"]["rest_service_code"]))
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def add_endpoint_access(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        for service_description_dic in self.get_services_description(config):
            if "endpoints" in service_description_dic["service_description"]:
                self.remote_add_endpoints_access(service_description_dic["ss_api_config"],
                                                 service_description_dic["client"],
                                                 service_description_dic["service_description"])
            else:
                if service_description_dic["service_description"]["type"] != ServiceType().WSDL:
                    BaseController.log_info(
                        "Skipping add access to endpoint for client %s, service %s, no endpoints defined" %
                        (ClientController().get_client_conf_id(service_description_dic["client"]),
                         service_description_dic["service_description"]["rest_service_code"]))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_endpoints(self, config, ss_name, service_description_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_list_endpoints(ss_api_config, ss_name, service_description_ids)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def update_endpoint(self, config, ss_name, endpoint_id, endpoint_method, endpoint_path):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_update_endpoint(ss_api_config, ss_name, endpoint_id, endpoint_method, endpoint_path)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_endpoint(self, config, ss_name, endpoint_id):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_delete_endpoint(ss_api_config, ss_name, endpoint_id)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_endpoints_access(self, config, ss_name, endpoints_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_list_endpoint_access(ss_api_config, ss_name, endpoints_ids)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_endpoints_access(self, config, ss_name, endpoints_ids, access_rights):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_delete_endpoint_access(ss_api_config, ss_name, endpoints_ids, access_rights)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_add_service_endpoints(self,
                                     ss_api_config,
                                     client_conf,
                                     service_description_conf,
                                     endpoint_conf):
        try:
            clients_api = ClientsApi(ApiClient(ss_api_config))
            client_controller = ClientController()
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                try:
                    service_description = ServiceController().get_client_service_description(clients_api, client,
                                                                                             service_description_conf)
                    if service_description:
                        if service_description.type == ServiceType().WSDL:
                            BaseController.log_info("Wrong service description, endpoints for WSDL services are not"
                                                    " allowed, skipped endpoint creation " + EndpointController.FOR_SERVICE
                                                    + "'" + service_description.url + "'")
                        else:
                            self.remote_add_endpoint(ss_api_config, service_description, service_description_conf,
                                                     endpoint_conf)
                except ApiException as find_err:
                    BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION, find_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    @staticmethod
    def remote_add_endpoint(ss_api_config, service_description, service_description_conf, endpoint_conf):
        endpoint = Endpoint(id=None, service_code=service_description_conf["rest_service_code"],
                            method=endpoint_conf["method"], path=endpoint_conf["path"],
                            generated=None)
        try:
            services_api = ServicesApi(ApiClient(ss_api_config))
            response = services_api.add_endpoint(id=service_description.services[0].id, body=endpoint)
            if response:
                BaseController.log_info(
                    "Added service endpoint '" + endpoint.method + " " + endpoint.path + "'" + EndpointController.FOR_SERVICE + "'" +
                    service_description.services[0].id + "'")
        except ApiException as err:
            if err.status == 409:
                BaseController.log_info(
                    "Service endpoint '" + endpoint.method + " " + endpoint.path + "'" + EndpointController.FOR_SERVICE + "'" +
                    service_description.services[
                        0].id + "' already added")
            else:
                BaseController.log_api_error('ServicesApi->add_endpoint', err)

    def remote_add_endpoints_access(self, ss_api_config, client_conf, service_description_conf):
        try:
            client_controller = ClientController()
            clients_api = ClientsApi(ApiClient(ss_api_config))
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                service_clients_candidates = client_controller.get_clients_service_client_candidates(clients_api,
                                                                                                     client.id, [])
                try:
                    service_controller = ServiceController()
                    clients_api = ClientsApi(ApiClient(ss_api_config))
                    service_description = service_controller.get_client_service_description(clients_api, client,
                                                                                            service_description_conf)
                    if service_description.type != ServiceType().WSDL:
                        self.remote_add_endpoint_access(ss_api_config, service_description, service_description_conf,
                                                        service_clients_candidates)
                except ApiException as find_err:
                    BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION, find_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def remote_add_endpoint_access(self, ss_api_config, service_description, service_description_conf,
                                   service_clients_candidates):
        for endpoint_conf in service_description_conf["endpoints"]:
            try:
                access_list = endpoint_conf["access"] if "access" in endpoint_conf else []
                if len(access_list) > 0:
                    self.add_access_from_list(ss_api_config, service_description, service_clients_candidates,
                                              endpoint_conf, access_list)
                else:
                    BaseController.log_info(
                        "Skipping endpoint add access for service '%s', endpoint %s-%s no endpoints defined" %
                        (service_description_conf["rest_service_code"], endpoint_conf["method"], endpoint_conf["path"]))
            except ApiException as find_err:
                BaseController.log_api_error(ClientController.CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION, find_err)

    @staticmethod
    def remote_update_endpoint(ss_api_config, ss_name, endpoint_id, endpoint_method, endpoint_path):
        endpoints_api = EndpointsApi(ApiClient(ss_api_config))
        try:
            endpoint = endpoints_api.get_endpoint(endpoint_id)
            if endpoint:
                if not endpoint.generated:
                    endpoint_update = EndpointUpdate(method=endpoint_method, path=endpoint_path)
                    try:
                        endpoints_api.update_endpoint(endpoint_id, body=endpoint_update)
                        BaseController.log_info("Updated endpoint with id: '%s', method: '%s', path: '%s', security server: '%s'"
                                                % (endpoint_id, endpoint_method, endpoint_path, ss_name))
                    except ApiException as err:
                        BaseController.log_api_error('EndpointsApi->update_endpoint', err)
                else:
                    BaseController.log_info("Error updating endpoint with id: '%s', security server: '%s', could not update generated endpoints")
        except ApiException:
            BaseController.log_info("Could not find an endpoint with id: '%s' for security server: '%s'" % (endpoint_id, ss_name))

    def remote_delete_endpoint(self, ss_api_config, ss_name, endpoint_id):
        endpoints_api = EndpointsApi(ApiClient(ss_api_config))
        try:
            endpoint = endpoints_api.get_endpoint(endpoint_id)
            if endpoint:
                if not endpoint.generated:
                    try:
                        endpoints_api.delete_endpoint(endpoint_id)
                        BaseController.log_info("Deleted endpoint with id: '%s', security server: '%s'"
                                                % (endpoint_id, ss_name))
                    except ApiException as err:
                        BaseController.log_api_error('EndpointsApi->delete_endpoint', err)
                else:
                    BaseController.log_info("Error deleting endpoint with id: '%s', security server: '%s', could not delete generated endpoints")
        except ApiException:
            BaseController.log_info(self.endpoint_not_found_message(endpoint_id, ss_name))

    def add_access_from_list(self, ss_api_config, service_description, service_clients_candidates, endpoint_conf,
                             access_list):
        for access in access_list:
            candidate = [c for c in service_clients_candidates if c.id == access]
            if len(candidate) == 0:
                BaseController.log_info("Error adding client access rights '" + access + "' for the endpoint '"
                                        + endpoint_conf["method"] + " " + endpoint_conf["path"]
                                        + "'" + EndpointController.FOR_SERVICE + "'" + service_description.id
                                        + "', no valid candidate found")
            else:
                self.add_access_based_on_service_client_candidate(ss_api_config, service_description, endpoint_conf,
                                                                  access, candidate)

    @staticmethod
    def add_access_based_on_service_client_candidate(ss_api_config, service_description, endpoint_conf, access,
                                                     candidate):
        endpoint = [e for e in service_description.services[0].endpoints if e.method == endpoint_conf["method"]
                    and e.path == endpoint_conf["path"]]
        if len(endpoint) == 0:
            BaseController.log_info(
                "Error adding client access rights '" + access + "' for the endpoint '"
                + endpoint_conf["method"] + " " + endpoint_conf["path"] + "'"
                + EndpointController.FOR_SERVICE + "'" + service_description.id
                + "', endpoint not found")
        else:
            try:
                endpoints_api = EndpointsApi(ApiClient(ss_api_config))
                response = endpoints_api.add_endpoint_service_clients(endpoint[0].id,
                                                                      body=ServiceClients(items=candidate))
                if response:
                    BaseController.log_info("Added client access rights: '" + candidate[0].id + "' for endpoint '"
                                            + endpoint[0].method + "' '" + endpoint[0].path
                                            + "' in service '"
                                            + service_description.services[0].id + "'")
            except ApiException as err:
                if err.status == 409:
                    BaseController.log_info(
                        "Added client access rights: '" + candidate[
                            0].id + "' for endpoint '" + endpoint[0].method +
                        "' '" + endpoint[0].path + "' in service '" +
                        service_description.services[0].id + "' already added")
                else:
                    BaseController.log_api_error('EndpointsApi->add_endpoint_service_clients', err)

    def get_services_description(self, config):
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug(
                'Starting service description access adding process for security server: ' + security_server['name'])
            if "clients" in security_server:
                for client in security_server["clients"]:
                    if "service_descriptions" in client:
                        for service_description in client["service_descriptions"]:
                            yield {'service_description': service_description,
                                   'client': client,
                                   'security_server': security_server,
                                   'ss_api_config': ss_api_config}

    def remote_list_endpoints(self, ss_api_config, ss_name, service_description_ids):
        service_descriptions_api = ServiceDescriptionsApi(ApiClient(ss_api_config))
        endpoints_list = []
        render_data = []
        for service_description_id in service_description_ids:
            try:
                service_description = service_descriptions_api.get_service_description(service_description_id)
                endpoints_list.extend(self.parse_service_description_to_endpoint_table(service_description))
            except ApiException:
                BaseController.log_info(
                    "The service description with id: '%s', security server: '%s', could not be found" %
                    (service_description_id, ss_name))

        if self.is_output_tabulated():
            render_data = [EndpointListMapper.headers()]
            render_data.extend(map(EndpointListMapper.as_list, endpoints_list))
        else:
            render_data.extend(map(EndpointListMapper.as_object, endpoints_list))
        self.render(render_data)
        return endpoints_list

    def remote_list_endpoint_access(self, ss_api_config, ss_name, endpoints_ids):
        endpoints_api = EndpointsApi(ApiClient(ss_api_config))
        render_list = []
        render_data = []
        for endpoint_id in endpoints_ids:
            try:
                endpoint = endpoints_api.get_endpoint(endpoint_id)
                if endpoint:
                    try:
                        access_rights = endpoints_api.get_endpoint_service_clients(endpoint_id)
                        render_list.extend(self.parse_endpoint_access_rights_response(endpoint, access_rights))
                    except ApiException as err:
                        BaseController.log_api_error('EndpointsApi->get_endpoint_service_clients', err)
            except ApiException:
                BaseController.log_info(self.endpoint_not_found_message(endpoint_id, ss_name))

        if len(render_list) > 0:
            if self.is_output_tabulated():
                render_data = [EndpointAccessListMapper.headers()]
                render_data.extend(map(EndpointAccessListMapper.as_list, render_list))
            else:
                render_data.extend(map(EndpointAccessListMapper.as_object, render_list))
            self.render(render_data)

        return render_list

    def remote_delete_endpoint_access(self, ss_api_config, ss_name, endpoints_ids, access_rights):
        endpoints_api = EndpointsApi(ApiClient(ss_api_config))
        for endpoint_id in endpoints_ids:
            try:
                endpoint = endpoints_api.get_endpoint(endpoint_id)
                if endpoint:
                    try:
                        access_rights_list = endpoints_api.get_endpoint_service_clients(endpoint_id)
                        access_rights_for_delete = list(filter(lambda a: a.id in access_rights, access_rights_list))
                        endpoints_api.delete_endpoint_service_clients(endpoint_id, body=ServiceClients(items=access_rights_for_delete))
                        BaseController.log_info("Deleted access rights: '%s', endpoint id: '%s', security server: '%s'" %
                                                ([a.id for a in access_rights_for_delete], endpoint_id, ss_name))
                    except ApiException as err:
                        BaseController.log_api_error('EndpointsApi->delete_endpoint_service_clients', err)
            except ApiException:
                BaseController.log_info(self.endpoint_not_found_message(endpoint_id, ss_name))

    @staticmethod
    def parse_service_description_to_endpoint_table(service_description):
        for service in service_description.services:
            for endpoint in service.endpoints:
                yield {
                    'endpoint_id': endpoint.id,
                    'endpoint_method': endpoint.method,
                    'endpoint_path': endpoint.path,
                    'service_code': endpoint.service_code,
                    'client': service_description.client_id,
                    'service_description': cut_big_string(service_description.url, 50),
                    'description_type': service_description.type,
                    'generated': endpoint.generated
                }

    @staticmethod
    def endpoint_not_found_message(endpoint_id, ss_name):
        return "Could not find an endpoint with id: '%s' for security server: '%s'" % (endpoint_id, ss_name)

    @staticmethod
    def security_server_not_found_message(ss_name):
        return "Security server: '%s' not found" % ss_name

    @staticmethod
    def parse_endpoint_access_rights_response(endpoint, access_rights):
        access = ''
        for access_right in access_rights:
            access = '%s%s, ' % (access, access_right.id)
        access = access[:-2]
        yield {
            'endpoint_id': endpoint.id,
            'endpoint': endpoint.method + " " + endpoint.path,
            'service_code': endpoint.service_code,
            'access': access
        }
