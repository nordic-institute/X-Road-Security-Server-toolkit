from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.api.xroad_instances_api import XroadInstancesApi
from xrdsst.resources.texts import texts
from xrdsst.core.util import parse_argument_list, convert_list_to_string, cut_big_string
from xrdsst.models.key_name import KeyName

class InstanceListMapper:
    @staticmethod
    def headers():
        return ['ID', 'LABEL', 'NAME', 'USAGE', 'POSSIBLE ACTIONS', 'CERTS']

    @staticmethod
    def as_list(key):
        return [key.get('id'),
                key.get('label'),
                key.get('name'),
                key.get('usage'),
                key.get('possible_actions'),
                key.get('certificate_count')]

    @staticmethod
    def as_object(key):
        return {
            'id': key.get('id'),
            'label': key.get('label'),
            'name': key.get('name'),
            'usage': key.get('usage'),
            'possible_actions': key.get('possible_actions'),
            'certificate_count': key.get('certificate_count')
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

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_instances(ss_api_config)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_list_instances(self, ss_api_config):
        xroad_instances_api = XroadInstancesApi(ApiClient(ss_api_config))
        try:
            instances = xroad_instances_api.get_xroad_instances()
            a = 1
        except ApiException as err:
            BaseController.log_api_error("XroadInstancesApi=>get_xroad_instances", err)
