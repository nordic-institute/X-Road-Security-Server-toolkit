from cement import ex
from xrdsst.api import ClientsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.core.conf_keys import ConfKeysSecurityServer
from xrdsst.core.util import convert_swagger_enum
from xrdsst.models import ClientAdd, Client, ConnectionType, ClientStatus
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts


class ClientController(BaseController):
    class Meta:
        label = 'client'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['client.controller.description']

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

    def remote_add_client(self, ss_api_config, client_conf):
        conn_type = convert_swagger_enum(ConnectionType, client_conf['connection_type'])
        client = Client(member_class=client_conf['member_class'],
                        member_code=client_conf['member_code'],
                        subsystem_code=client_conf['subsystem_code'],
                        connection_type=conn_type)

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
            client = self.find_client(clients_api, security_server_conf, client_conf)
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
            BaseController.log_api_error('ClientsApi->find_clients', find_err)

    def find_client(self, clients_api, security_server_conf, client_conf):
        found_clients = clients_api.find_clients(
            member_class=client_conf['member_class'],
            member_code=client_conf['member_code'],
            subsystem_code=client_conf['subsystem_code']
        )

        if not found_clients:
            BaseController.log_info(
                security_server_conf[ConfKeysSecurityServer.CONF_KEY_NAME] + ": Client matching " + self.partial_client_id(client_conf) + " not found")
            return None

        if len(found_clients) > 1:
            BaseController.log_info(
                security_server_conf[ConfKeysSecurityServer.CONF_KEY_NAME] + ": Error, multiple matching clients found for " + self.partial_client_id(client_conf)
            )
            return None

        return found_clients[0]

    @staticmethod
    def partial_client_id(client_conf):
        return str(client_conf['member_class']) + ":" + str(client_conf['member_code']) + ":" + str(client_conf['subsystem_code'])

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