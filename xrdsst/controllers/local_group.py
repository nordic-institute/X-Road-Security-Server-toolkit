from cement import ex
from xrdsst.api import LocalGroupsApi, ClientsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts
from xrdsst.core.conf_keys import ConfKeysSecServerClientLocalGroups, ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.models import LocalGroupAdd

class LocalGroupController(BaseController):
    class Meta:
        label = 'local_group'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['local_group.controller.description']


    @ex(help="add", arguments=[])
    def add(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)

        self.add_local_group(active_config)

    @ex(help="add members", arguments=[])
    def add_members(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)
        self.add_local_group_members(active_config)

    def add_local_group(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting adding local groups to client: ' + security_server['name'])
            if ConfKeysSecurityServer.CONF_KEY_CLIENTS in security_server:
                for client in security_server[ConfKeysSecurityServer.CONF_KEY_CLIENTS]:
                    if ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS in client:
                        if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE not in client:
                            BaseController.log_info(
                                "Skipping local group creation for client: '%s', security server: '%s',"
                                "local groups can not be added to members"
                                % (ClientController().get_client_conf_id(client), security_server["name"]))
                        else:
                            for local_group in client[ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS]:
                                self.remote_add_local_group(ss_api_config, security_server, client, local_group)
                    else:
                        BaseController.log_info("Skipping local group creation for client: '%s', security server: '%s'"
                                                % (ClientController().get_client_conf_id(client), security_server["name"]))
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def add_local_group_members(self, config):
        a=1


    @staticmethod
    def remote_add_local_group(ss_api_config, security_server_conf, client_conf, local_group_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        try:
            client = ClientController().find_client(clients_api, client_conf)
            try:
                local_group = LocalGroupAdd(code=local_group_conf["code"], description=local_group_conf["description"])
                clients_api.add_client_local_group(client.id, body=local_group)
                BaseController.log_info("Added local group: '%s' for client '%s' security server: '%s'"
                                        % (local_group_conf["code"], client.id, security_server_conf["name"]))
            except ApiException as add_err:
                if add_err.status == 409:
                    BaseController.log_info("Local group: '%s' for client '%s' security server: '%s', already added"
                                            % (local_group_conf["code"], client.id, security_server_conf["name"]))
                else:
                    BaseController.log_api_error('ClientsApi->add_client_local_group', add_err)
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)