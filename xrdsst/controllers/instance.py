from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.xroad_instances_api import XroadInstancesApi
from xrdsst.resources.texts import texts
from xrdsst.core.util import parse_argument_list, convert_list_to_string, cut_big_string

class InstanceListMapper:
    @staticmethod
    def headers():
        return ['SECURITY SERVER', 'INSTANCES']

    @staticmethod
    def as_list(item):
        return [item.get('ss_name'),
                item.get('instance')]

    @staticmethod
    def as_object(key):
        return {
            'ss_name': key.get('ss_name'),
            'instance': key.get('instance')
        }


class InstanceController(BaseController):
    class Meta:
        label = 'instance'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['instance.controller.description']

    @ex(help="List instances", arguments=[])
    def list(self):
        active_config = self.load_config()
        self.list_instances(active_config)

    def list_instances(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        render_data = []
        instances = []
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            instances.append(self.remote_list_instances(ss_api_config, security_server["name"]))
        BaseController.log_keyless_servers(ss_api_conf_tuple)

        if self.is_output_tabulated():
            render_data = [InstanceListMapper.headers()]
            render_data.extend(map(InstanceListMapper.as_list, instances))
        else:
            render_data.extend(map(InstanceListMapper.as_object, instances))
        self.render(render_data)

    @staticmethod
    def remote_list_instances(ss_api_config, ss_name):
        xroad_instances_api = XroadInstancesApi(ApiClient(ss_api_config))
        try:
            instances = xroad_instances_api.get_xroad_instances()
            return {
                'ss_name': ss_name,
                'instance': convert_list_to_string(instances)
            }
        except ApiException as err:
            BaseController.log_api_error("XroadInstancesApi=>get_xroad_instances", err)
