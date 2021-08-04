import cement.utils.fs
from cement import ex
from xrdsst.api import ClientsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.core.util import convert_swagger_enum, parse_argument_list
from xrdsst.models import ClientAdd, Client, ConnectionType, ClientStatus
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts
from xrdsst.controllers.token import TokenController


class ClientsListMapper:
    @staticmethod
    def headers():
        return ['ID', 'INSTANCE', 'MEMBER CLASS', 'MEMBER CODE', 'MEMBER NAME', 'SUBSYSTEM', 'OWNER', 'STATUS', 'HAS SIGN CERT']

    @staticmethod
    def as_list(client):
        return [client.id,
                client.instance_id,
                client.member_class,
                client.member_code,
                client.member_name,
                client.subsystem_code,
                client.owner,
                client.status,
                client.has_valid_local_sign_cert]

    @staticmethod
    def as_object(client):
        return {
            'id': client.id,
            'member_class': client.member_class,
            'member_code': client.member_code,
            'member_name': client.member_name,
            'subsystem_code': client.subsystem_code,
            'owner': client.owner,
            'status': client.status,
            'has_valid_local_sign_cert': client.has_valid_local_sign_cert
        }


class ClientController(BaseController):
    class Meta:
        label = 'client'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['client.controller.description']

    CLIENTS_API_FIND_CLIENTS = 'ClientsApi->find_clients'
    CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTION = 'ClientsApi->get_client_service_description'
    CLIENTS_API_GET_CLIENT_SERVICE_DESCRIPTIONS = 'ClientsApi->get_client_service_descriptions'

    @ex(help="Add client subsystem", arguments=[])
    def add(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.add_client(active_config)

    @ex(help="Register client", arguments=[])
    def register(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.register_client(active_config)

    @ex(help="Update client", arguments=[])
    def update(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.update_client(active_config)

    @ex(help="Import TLS certificates", arguments=[])
    def import_tls_certs(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.client_import_tls_cert(active_config)

    @ex(help="Unregister client(s)",
        arguments=[
            (['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
            (['--client'], {'help': 'Client(s) Id', 'dest': 'client'})
        ]
        )
    def unregister(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for unregister clients: %s' % missing_parameters)
            return

        self.unregister_client(active_config, self.app.pargs.ss, parse_argument_list(self.app.pargs.client))

    @ex(help="Delete client(s)",
        arguments=[
            (['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
            (['--client'], {'help': 'Client(s) Id', 'dest': 'client'})
        ])
    def delete(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for deleting clients: %s' % missing_parameters)
            return

        self.delete_client(active_config, self.app.pargs.ss, parse_argument_list(self.app.pargs.client))

    @ex(help="Make owner",
        arguments=[
            (['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
            (['--member'], {'help': 'Member Id', 'dest': 'member'})
        ])
    def make_owner(self):
        active_config = self.load_config()
        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.member is None:
            missing_parameters.append('member')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for make member owner: %s' % missing_parameters)
            return

        self.make_member_owner(active_config, self.app.pargs.ss, self.app.pargs.member)

    @ex(help="List clients",
        arguments=[
            (['--ss'], {'help': 'Security server name', 'dest': 'ss'})
        ])
    def list(self):
        active_config = self.load_config()
        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing listing clients: %s' % missing_parameters)
            return

        self.list_clients(active_config, self.app.pargs.ss)

    # This operation can (at least sometimes) also be performed when global status is FAIL.
    def add_client(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting client add process for security server: ' + security_server['name'])
            if "clients" in security_server:  # Guards both against empty section (->None) & complete lack of section
                for client in security_server["clients"]:
                    self.remote_add_client(ss_api_config, client)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    # This operation fails when global status is not up to date.
    def register_client(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting client registrations for security server: ' + security_server['name'])
            if "clients" in security_server:
                for client in security_server["clients"]:
                    self.remote_register_client(ss_api_config, security_server, client)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def update_client(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting client registrations for security server: ' + security_server['name'])
            if "clients" in security_server:
                for client in security_server["clients"]:
                    self.remote_update_client(ss_api_config, security_server, client)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def client_import_tls_cert(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting internal TLS certificate import for security server: ' + security_server['name'])
            if ConfKeysSecurityServer.CONF_KEY_TLS_CERTS in security_server:
                client_conf = {
                    "member_name": security_server["owner_dn_org"],
                    "member_code": security_server["owner_member_code"],
                    "member_class": security_server["owner_member_class"]
                }
                self.remote_import_tls_certificate(ss_api_config, security_server[ConfKeysSecurityServer.CONF_KEY_TLS_CERTS], client_conf)

            if "clients" in security_server:
                for client_conf in security_server["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES in client_conf:
                        self.remote_import_tls_certificate(ss_api_config, client_conf[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_TLS_CERTIFICATES],
                                                           client_conf)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def unregister_client(self, config, security_server_name, clients_id):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        security_server = list(filter(lambda ss_server: ss_server["name"] == security_server_name, config["security_server"]))
        if len(security_server) == 0:
            BaseController.log_info("Security server with name: %s not found in config file" % security_server_name)
        else:
            ss_api_config = self.create_api_config(security_server[0], config)
            BaseController.log_debug('Starting client unregistration for security server: ' + security_server[0]['name'])
            self.remote_unregister_client(ss_api_config, security_server_name, clients_id)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_client(self, config, security_server_name, client_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        security_server = list(filter(lambda ss_server: ss_server["name"] == security_server_name, config["security_server"]))
        if len(security_server) == 0:
            BaseController.log_info("Security server with name: %s not found in config file" % security_server_name)
        else:
            ss_api_config = self.create_api_config(security_server[0], config)
            BaseController.log_debug('Starting client deletion for security server: ' + security_server[0]['name'])
            self.remote_delete_client(ss_api_config, security_server_name, client_ids)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def make_member_owner(self, config, ss_name, member_id):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) == 0:
            BaseController.log_info("Security server: '%s' not found" % ss_name)
        else:
            ss_api_config = self.create_api_config(security_servers[0], config)
            client = self.remote_make_member_owner(ss_api_config, ss_name, member_id)
            if client:
                self.create_auth_key_for_new_owner(ss_api_config, security_servers[0], client)
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_clients(self, config, ss_name):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        clients = []
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) == 0:
            BaseController.log_info("Security server: '%s' not found" % ss_name)
        else:
            ss_api_config = self.create_api_config(security_servers[0], config)
            clients = self.remote_list_clients(ss_api_config)
        BaseController.log_keyless_servers(ss_api_conf_tuple)
        return clients

    def remote_add_client(self, ss_api_config, client_conf):
        conn_type = convert_swagger_enum(ConnectionType, client_conf['connection_type'])
        client = Client(member_class=client_conf['member_class'],
                        member_code=client_conf['member_code'],
                        connection_type=conn_type,
                        member_name=client_conf['member_name'],
                        subsystem_code=client_conf['subsystem_code'] if 'subsystem_code' in client_conf else None,
                        owner=False,
                        has_valid_local_sign_cert=False)

        client_add = ClientAdd(client=client, ignore_warnings=True)
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            response = clients_api.add_client(body=client_add)
            BaseController.log_info("Added client subsystem " + self.partial_client_id(client_conf) + " (got full id " + response.id + ")")
            return response
        except ApiException as err:
            if err.status == 409:
                BaseController.log_info("Client for '" + self.partial_client_id(client_conf) + "' already exists.")
            else:
                BaseController.log_api_error('ClientsApi->add_client', err)

    def remote_register_client(self, ss_api_config, security_server_conf, client_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client = self.find_client(clients_api, client_conf)
            if client:
                if ClientStatus.SAVED != client.status:
                    BaseController.log_info(
                        security_server_conf['name'] + ": " + self.partial_client_id(client_conf) + " already registered."
                    )
                    return

                try:
                    clients_api.register_client(id=client.id)
                    BaseController.log_info("Registered client " + self.partial_client_id(client_conf))
                except ApiException as reg_err:
                    BaseController.log_api_error('ClientsApi->register_client', reg_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def remote_update_client(self, ss_api_config, security_server_conf, client_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client = self.find_client(clients_api, client_conf)
            if client:
                if client.status not in [ClientStatus.SAVED, ClientStatus.REGISTERED, ClientStatus.REGISTRATION_IN_PROGRESS]:
                    BaseController.log_info(
                        security_server_conf['name'] + ": " + self.partial_client_id(client_conf) + " not added/registered yet."
                    )
                    return

                try:
                    client.connection_type = convert_swagger_enum(ConnectionType, client_conf['connection_type'])
                    response = clients_api.update_client(client.id, body=client)
                    BaseController.log_info("Updated client " + self.partial_client_id(client_conf) + " connection type")
                    return response
                except ApiException as reg_err:
                    BaseController.log_api_error('ClientsApi->update_client', reg_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def remote_import_tls_certificate(self, ss_api_config, tls_certs, client_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client = self.find_client(clients_api, client_conf)
            if client:
                for tls_cert in tls_certs:
                    self.remote_add_client_tls_certificate(tls_cert, clients_api, client)
        except ApiException as find_err:
            BaseController.log_api_error("ClientsApi->find_client", find_err)

    @staticmethod
    def remote_delete_client(ss_api_config, security_server_name, client_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        for client_id in client_ids:
            try:
                clients_api.delete_client(client_id)
                BaseController.log_info("Deleted client: '%s' for security server: '%s'" % (client_id, security_server_name))
            except ApiException as err:
                if err.status == 404:
                    BaseController.log_info("Error deleting client: '%s' for security server: '%s', not found" % (client_id, security_server_name))
                else:
                    BaseController.log_api_error("ClientsApi->delete_client", err)

    @staticmethod
    def remote_unregister_client(ss_api_config, security_server, client_ids):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        for client_id in client_ids:
            try:
                clients_api.unregister_client(client_id)
                BaseController.log_info("Unregister client: '%s' for security server: '%s'" % (client_id, security_server))
            except ApiException as err:
                if err.status == 409:
                    BaseController.log_info("Client: '%s' for security server: '%s', already unregistered" % (client_id, security_server))
                else:
                    BaseController.log_api_error("ClientsApi->unregister_client", err)

    @staticmethod
    def remote_add_client_tls_certificate(tls_cert, clients_api, client):
        try:
            location = cement.utils.fs.join_exists(tls_cert)
            if not location[1]:
                BaseController.log_info("Import TLS certificate '%s' for client %s does not exist" % (location[0], client.id))
            else:
                cert_file_loc = location[0]
                cert_file = open(cert_file_loc, "rb")
                cert_data = cert_file.read()
                cert_file.close()
                response = clients_api.add_client_tls_certificate(client.id, body=cert_data)
                BaseController.log_info(
                    "Import TLS certificate '%s' for client '%s'" % (tls_cert, client.id))
                return response
        except ApiException as err:
            if err.status == 409:
                BaseController.log_info(
                    "TLS certificate '%s' for client %s already exists" % (tls_cert, client.id))
            else:
                BaseController.log_api_error('ClientsApi->import_tls_certificate', err)

    @staticmethod
    def create_auth_key_for_new_owner(ss_api_config, security_server_conf, client):
        token_controller = TokenController()

        token_controller.remote_token_add_auth_key_with_csrs(ss_api_config, security_server_conf, client.member_class,
                                                             client.member_code, client.member_name)

    @staticmethod
    def remote_make_member_owner(ss_api_config, ss_name, member_id):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client = clients_api.get_client(member_id)
            if client.subsystem_code:
                BaseController.log_info("It's not possible to make owner to subsystems: %s for security server: '%s'"
                                        % (member_id, ss_name))
            else:
                try:
                    clients_api.change_owner(member_id)
                    BaseController.log_info("Change owner request submitted: "
                                            "'%s' for security server: '%s'" % (member_id, ss_name))
                    return client
                except ApiException as err:
                    if err.body.count('member_already_owner'):
                        BaseController.log_info("Member: '%s' for security server: '%s', already owner"
                                                % (member_id, ss_name))
                    else:
                        BaseController.log_api_error("ClientsApi->change_owner", err)
        except ApiException as err:
            BaseController.log_api_error("ClientsApi->remote_make_member_owner", err)

    def remote_list_clients(self, ss_api_config):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        clients = self.find_all_clients(clients_api, show_members=True, internal_search=True)
        render_data =[]
        if self.is_output_tabulated():
            render_data = [ClientsListMapper.headers()]
            render_data.extend(map(ClientsListMapper.as_list, clients))
        else:
            render_data.extend(map(ClientsListMapper.as_object, clients))
        self.render(render_data)
        return clients

    def find_client(self, clients_api, client_conf):
        if 'subsystem_code' in client_conf:
            found_clients = clients_api.find_clients(
                member_class=client_conf['member_class'],
                member_code=client_conf['member_code'],
                subsystem_code=client_conf["subsystem_code"]
            )
        else:
            all_clients = clients_api.find_clients(
                member_class=client_conf['member_class'],
                member_code=str(client_conf['member_code']),
                name=client_conf["member_name"]
            )
            found_clients = list(found_client for found_client in all_clients if found_client.subsystem_code is None)
        if not found_clients:
            BaseController.log_info(
                client_conf["member_name"] + ": Client matching " + self.partial_client_id(client_conf) + " not found")
            return None

        if len(found_clients) > 1:
            BaseController.log_info(
                client_conf["member_name"] + ": Error, multiple matching clients found for " + self.partial_client_id(client_conf)
            )
            return None
        return found_clients[0]

    @staticmethod
    def find_all_clients(clients_api, show_members=False, internal_search=False):
        try:
            return clients_api.find_clients(show_members=show_members, internal_search=internal_search)
        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_clients', find_err)

    @staticmethod
    def partial_client_id(client_conf):
        client_id = str(client_conf['member_class']) + ":" + str(client_conf['member_code'])
        if 'subsystem_code' in client_conf and client_conf['subsystem_code'] is not None:
            client_id = client_id + ":" + client_conf['subsystem_code']
        return client_id

    @staticmethod
    def get_clients_service_client_candidates(clients_api, client_id, candidates_ids):
        try:
            candidates = clients_api.find_service_client_candidates(client_id)

            if candidates_ids is None or len(candidates_ids) == 0:
                return candidates
            else:
                return [x for x in candidates if x.id in candidates_ids]

        except ApiException as find_err:
            BaseController.log_api_error('ClientsApi->find_service_client_candidates', find_err)

    @staticmethod
    def is_client_base_member(client_conf, security_server_conf):
        return client_conf["member_class"] == security_server_conf["owner_member_class"] and client_conf["member_code"] == security_server_conf[
            "owner_member_code"]

    @staticmethod
    def get_client_conf_id(client_conf):
        client_id = "%s/%s/%s" % (client_conf["member_class"], client_conf["member_code"], client_conf["member_name"])
        if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client_conf:
            client_id = client_id + "/" + client_conf[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE]

        return client_id


