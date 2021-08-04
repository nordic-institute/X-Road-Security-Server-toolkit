from cement import ex
from xrdsst.api import LocalGroupsApi, ClientsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.client import ClientController
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts
from xrdsst.core.conf_keys import ConfKeysSecServerClientLocalGroups, ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.models import LocalGroupAdd, Members
from xrdsst.core.util import parse_argument_list, convert_list_to_string


class LocalGroupListMapper:
    @staticmethod
    def headers():
        return ['ID', 'CODE', 'DESCRIPTION', 'MEMBERS']

    @staticmethod
    def as_list(local_group):
        members_ids = []
        for member in local_group.members:
            members_ids.append(member.id)
        return [local_group.id,
                local_group.code,
                local_group.description,
                convert_list_to_string(members_ids)]

    @staticmethod
    def as_object(local_group):
        members_ids = []
        for member in local_group.members:
            members_ids.append(member.id)

        return {
            'id': local_group.id,
            'code': local_group.code,
            'description': local_group.description,
            'members': convert_list_to_string(members_ids)
        }


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
    def add_member(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)
        self.add_local_group_members(active_config)

    @ex(help="List local groups", arguments=[(['--ss'], {'help': 'Security Server name', 'dest': 'ss'}),
                                             (['--client'], {'help': 'Client id', 'dest': 'client'})])
    def list(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.client is None:
            missing_parameters.append('client')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for listing local groups: %s' % missing_parameters)
            return

        self.list_local_groups(active_config, self.app.pargs.ss, self.app.pargs.client)

    @ex(help="Delete local group(s)", arguments=[(['--ss'], {'help': 'Security Server name', 'dest': 'ss'}),
                                                 (['--local-group'],
                                                  {'help': 'Local group id(s)', 'dest': 'local_group'})])
    def delete(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.local_group is None:
            missing_parameters.append('local-group')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for deleting local groups: %s' % missing_parameters)
            return

        self.delete_local_group(active_config, self.app.pargs.ss, parse_argument_list(self.app.pargs.local_group))

    @ex(help="Delete local group member(s)", arguments=[(['--ss'], {'help': 'Security Server name', 'dest': 'ss'}),
                                                        (['--local-group'],
                                                         {'help': 'Local group id(s)', 'dest': 'local_group'}),
                                                        (['--member'],
                                                         {'help': 'Local group member(s) id', 'dest': 'member'})])
    def delete_member(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.local_group is None:
            missing_parameters.append('local_group')
        if self.app.pargs.member is None:
            missing_parameters.append('member')
        if len(missing_parameters) > 0:
            BaseController.log_info(
                'The following parameters missing for deleting local groups members: %s' % missing_parameters)
            return

        self.delete_local_group_member(active_config, self.app.pargs.ss,
                                       parse_argument_list(self.app.pargs.local_group),
                                       parse_argument_list(self.app.pargs.member))

    def add_local_group(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting adding local groups to client: ' + security_server['name'])
            if ConfKeysSecurityServer.CONF_KEY_CLIENTS in security_server:
                for local_group_dic in self.get_local_groups(security_server, 'creation'):
                    self.remote_add_local_group(ss_api_config, security_server,
                                                local_group_dic["client"], local_group_dic["local_group"])
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    @staticmethod
    def get_local_groups(security_server, action):
        for client in security_server[ConfKeysSecurityServer.CONF_KEY_CLIENTS]:
            if ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS in client:
                if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE not in client:
                    BaseController.log_info(
                        "Skipping local group %s for client: '%s', security server: '%s',"
                        "local groups can not be added to members"
                        % (action, ClientController().get_client_conf_id(client), security_server["name"]))
                else:
                    for local_group in client[ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS]:
                        yield {'local_group': local_group, 'client': client}

    def add_local_group_members(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting adding local groups to client: ' + security_server['name'])
            if ConfKeysSecurityServer.CONF_KEY_CLIENTS in security_server:
                for local_group_dic in self.get_local_groups(security_server, 'add member'):
                    if local_group_dic["local_group"].get(
                            ConfKeysSecServerClientLocalGroups.CONF_KEY_SS_CLIENT_LOCAL_GROUP_MEMBERS):
                        self.remote_add_local_group_member(ss_api_config, security_server, local_group_dic["client"],
                                                           local_group_dic["local_group"])
                    else:
                        BaseController.log_info(
                            "Skipping adding members for local group: '%s', "
                            "client: '%s', security server: '%s'"
                            % (local_group_dic["local_group"]
                               [ConfKeysSecServerClientLocalGroups.CONF_KEY_SS_CLIENT_LOCAL_GROUP_CODE],
                               ClientController().get_client_conf_id(local_group_dic["client"]), security_server["name"]))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def list_local_groups(self, config, ss_name, client_id):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_list_local_groups(ss_api_config, client_id)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_local_group(self, config, ss_name, local_group_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_delete_local_group(ss_api_config, local_group_ids)
        else:
            BaseController.log_info("Security server: '%s' not found" % ss_name)
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_local_group_member(self, config, ss_name, local_groups_id, members_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_delete_local_group_member(ss_api_config, local_groups_id, members_ids)
        else:
            BaseController.log_info("Security server: '%s' not found" % ss_name)
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    @staticmethod
    def remote_add_local_group(ss_api_config, security_server_conf, client_conf, local_group_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        client_controller = ClientController()
        try:
            client = client_controller.find_client(clients_api, client_conf)
            if client:
                try:
                    local_group = LocalGroupAdd(code=local_group_conf["code"],
                                                description=local_group_conf["description"])
                    clients_api.add_client_local_group(client.id, body=local_group)
                    BaseController.log_info("Added local group: '%s' for client '%s' security server: '%s'"
                                            % (local_group_conf["code"], client.id, security_server_conf["name"]))
                except ApiException as add_err:
                    if add_err.status == 409:
                        BaseController.log_info("Local group: '%s' for client '%s' security server: '%s', already added"
                                                % (local_group_conf["code"], client.id, security_server_conf["name"]))
                    else:
                        BaseController.log_api_error('ClientsApi->add_client_local_group', add_err)
            else:
                BaseController.log_info("Client: '%s', security server: '%s', client not found" %
                                        (client_controller.get_client_conf_id(client_conf),
                                         security_server_conf["name"]))
        except ApiException as find_err:
            BaseController.log_api_error(ClientController.CLIENTS_API_FIND_CLIENTS, find_err)

    def remote_add_local_group_member(self, ss_api_config, security_server_conf, client_conf, local_group_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        local_group_api = LocalGroupsApi(ApiClient(ss_api_config))
        client = ClientController().find_client(clients_api, client_conf)
        local_groups_members_add_dic = self.get_local_groups_members_for_add(ss_api_config, security_server_conf,
                                                                             client_conf, local_group_conf)

        if local_groups_members_add_dic and len(local_groups_members_add_dic["members_for_add"]) > 0:
            try:
                local_group_api.add_local_group_member(local_groups_members_add_dic["local_group"].id,
                                                       body=Members(local_groups_members_add_dic["members_for_add"]))
                BaseController.log_info("Added member(s): '%s', local group: '%s', client '%s',security server: '%s'"
                                        % (local_groups_members_add_dic["members_for_add"], local_group_conf["code"], client.id, security_server_conf["name"]))
            except ApiException as err:
                if err.status == 409:
                    BaseController.log_info("Members '%s', Local group: '%s', client '%s' security server: '%s', already added"
                                            % (
                                                local_groups_members_add_dic["members_for_add"], local_group_conf["code"], client.id,
                                                security_server_conf["name"]))
                else:
                    BaseController.log_api_error('ClientsApi->add_local_group_member', err)

    def get_local_groups_members_for_add(self, ss_api_config, security_server_conf, client_conf, local_group_conf):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        client_controller = ClientController()
        client = ClientController().find_client(clients_api, client_conf)
        local_groups_members_add = []
        try:
            local_groups = self.get_client_local_groups(clients_api, client.id, local_group_conf["code"])
            if len(local_groups) > 0:
                all_clients = client_controller.find_all_clients(clients_api, show_members=False, internal_search=False)

                for local_group_member in local_group_conf[ConfKeysSecServerClientLocalGroups.CONF_KEY_SS_CLIENT_LOCAL_GROUP_MEMBERS]:
                    member_client = list(filter(lambda c: c.id == local_group_member, all_clients))
                    if len(member_client) > 0:
                        local_groups_members_add.append(member_client[0].id)
                    else:
                        BaseController.log_info(
                            "Error adding member: '%s', local group: '%s', client '%s',security server: '%s',"
                            " member not found"
                            % (local_group_member, local_group_conf["code"], client.id, security_server_conf["name"]))

                return {'local_group': local_groups[0], 'members_for_add': local_groups_members_add}

            else:
                BaseController.log_info(
                    "Error adding members to local group: '%s', client '%s', security server: '%s',"
                    " local group not found"
                    % (local_group_conf["code"], client.id, security_server_conf["name"]))
                return None
        except ApiException as find_err:
            BaseController.log_api_error(client_controller.CLIENTS_API_FIND_CLIENTS, find_err)

    @staticmethod
    def get_client_local_groups(clients_api, client_id, local_group_code=None):
        try:
            local_groups = clients_api.get_client_local_groups(client_id)
            if local_group_code:
                return list(filter(lambda lg: lg.code == local_group_code, local_groups))
            return local_groups
        except ApiException:
            BaseController.log_info("Local groups not found for client '%s'" % client_id)

    def remote_list_local_groups(self, ss_api_config, client_id):
        clients_api = ClientsApi(ApiClient(ss_api_config))
        local_groups_list = self.get_client_local_groups(clients_api, client_id)
        render_data = []
        if local_groups_list:
            if self.is_output_tabulated():
                render_data = [LocalGroupListMapper.headers()]
                render_data.extend(map(LocalGroupListMapper.as_list, local_groups_list))
            else:
                render_data.extend(map(LocalGroupListMapper.as_object, local_groups_list))
            self.render(render_data)
        return local_groups_list

    @staticmethod
    def remote_delete_local_group(ss_api_config, local_group_ids):
        local_group_api = LocalGroupsApi(ApiClient(ss_api_config))
        for local_group_id in local_group_ids:
            try:
                local_group_api.delete_local_group(local_group_id)
                BaseController.log_info("Deleted local group with id: '%s'" % local_group_id)
            except ApiException as find_err:
                BaseController.log_api_error("LocalGroupsApi=>delete_local_group", find_err)

    @staticmethod
    def remote_delete_local_group_member(ss_api_config, local_groups_ids, members_ids):
        local_group_api = LocalGroupsApi(ApiClient(ss_api_config))
        for local_group_id in local_groups_ids:
            local_group = local_group_api.get_local_group(local_group_id)
            members_for_delete = list(filter(lambda member: member.id in members_ids, local_group.members))
            if len(members_for_delete) > 0:
                id_members_for_delete = [m.id for m in members_for_delete]
                try:
                    local_group_api.delete_local_group_member(local_group_id, body=Members(id_members_for_delete))
                    BaseController.log_info("Deleted local group member(s): '%s' for local group: '%s'" % (
                        id_members_for_delete, local_group_id))
                except ApiException as find_err:
                    BaseController.log_api_error("LocalGroupsApi=>delete_local_group", find_err)
