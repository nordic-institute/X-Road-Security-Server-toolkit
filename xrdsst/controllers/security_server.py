from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.security_servers_api import SecurityServersApi
from xrdsst.api.system_api import SystemApi
from xrdsst.resources.texts import texts


class SecurityServerListMapper:
    @staticmethod
    def headers():
        return ['ID', 'CODE', 'ADDRESS', 'INSTANCE', 'MEMBER CLASS', 'MEMBER CODE']

    @staticmethod
    def as_list(ss):
        return [ss.get('id'),
                ss.get('code'),
                ss.get('address'),
                ss.get('instance'),
                ss.get('member_class'),
                ss.get('member_code')]

    @staticmethod
    def as_object(ss):
        return {
            'id': ss.get('id'),
            'code': ss.get('code'),
            'address': ss.get('address'),
            'instance': ss.get('instance'),
            'member_class': ss.get('member_class'),
            'member_code': ss.get('member_code')
        }


class SecurityServerVersionMapper:
    @staticmethod
    def headers():
        return ['SECURITY SERVER', 'VERSION']

    @staticmethod
    def as_list(ss):
        return [ss.get('security_server'),
                ss.get('version')]

    @staticmethod
    def as_object(ss):
        return {
            'security_server': ss.get('security_server'),
            'version': ss.get('version')
        }


class SecurityServerController(BaseController):
    class Meta:
        label = 'security_server'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['security_server.controller.description']

    @ex(help="List security servers", arguments=[])
    def list(self):
        active_config = self.load_config()
        self.list_security_servers(active_config)

    @ex(help="List security server versions", arguments=[])
    def version(self):
        active_config = self.load_config()
        self.list_security_servers_version(active_config)

    def list_security_servers(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        render_data = []
        render_list = []
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            ss_list = self.remote_list_security_servers(ss_api_config)
            if ss_list:
                render_list = self.union_security_server_lists(render_list, ss_list)
        if len(render_list) > 0:
            if self.is_output_tabulated():
                render_data = [SecurityServerListMapper.headers()]
                render_data.extend(map(SecurityServerListMapper.as_list, render_list))
            else:
                render_data.extend(map(SecurityServerListMapper.as_object, render_list))
            self.render(render_data)
        BaseController.log_keyless_servers(ss_api_conf_tuple)
        return render_list

    def list_security_servers_version(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        render_data = []
        render_list = []
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            version = self.remote_list_security_server_version(ss_api_config)
            if version:
                render_list.append({
                    'security_server': security_server["name"],
                    'version': version
                })
        if len(render_list) > 0:
            if self.is_output_tabulated():
                render_data = [SecurityServerVersionMapper.headers()]
                render_data.extend(map(SecurityServerVersionMapper.as_list, render_list))
            else:
                render_data.extend(map(SecurityServerVersionMapper.as_object, render_list))
            self.render(render_data)
        BaseController.log_keyless_servers(ss_api_conf_tuple)
        return render_list

    def remote_list_security_servers(self, ss_api_config):
        security_servers_api = SecurityServersApi(ApiClient(ss_api_config))
        try:
            security_servers = self.parse_security_server_response(security_servers_api.get_security_servers())
            return list(security_servers)
        except ApiException as err:
            BaseController.log_api_error("SecurityServersApi=>security_servers_api", err)

    @staticmethod
    def remote_list_security_server_version(ss_api_config):
        system_api = SystemApi(ApiClient(ss_api_config))
        try:
            version = system_api.system_version()
            return version.info
        except ApiException as err:
            BaseController.log_api_error("SystemApi=>system_version", err)

    @staticmethod
    def parse_security_server_response(security_servers):
        for security_server in security_servers:
            yield {
                'id': security_server.id,
                'code': security_server.server_code,
                'address': security_server.server_address,
                'instance': security_server.instance_id,
                'member_class': security_server.member_class,
                'member_code': security_server.member_code
            }

    @staticmethod
    def union_security_server_lists(ss_list1, ss_list2):
        if len(ss_list1) == 0:
            return ss_list2
        else:
            for ss in ss_list2:
                is_repeated = len(list(filter(lambda s: s["id"] == ss["id"], ss_list1))) > 0
                if not is_repeated:
                    ss_list1.append(ss)
            return ss_list1
