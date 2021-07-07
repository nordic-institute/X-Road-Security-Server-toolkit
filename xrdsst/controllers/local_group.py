from cement import ex
from xrdsst.api import ClientsApi, EndpointsApi, ServicesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.client import ClientController
from xrdsst.models import Endpoint, ServiceType, ServiceClients
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts


class LocalGroupController(BaseController):
    class Meta:
        label = 'local_group'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['local_group.controller.description']


    @ex(help="create", arguments=[])
    def add(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, unconfigured_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, unconfigured_servers)
        self.add_service_endpoints(active_config)