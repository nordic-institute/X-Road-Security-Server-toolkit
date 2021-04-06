from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.models import InitialServerConf
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.initialization_api import InitializationApi
from xrdsst.api.system_api import SystemApi
from xrdsst.resources.texts import texts


class InitServerController(BaseController):
    class Meta:
        label = 'init'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['init.controller.description']

    @ex(help='Initialize security server', hide=True)
    def _default(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():  # Even though this operation is very likely to remain first ... forever
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.initialize_server(active_config)

    def initialize_server(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1]]:
            self.log_debug('Starting initialization process for security server: ' + security_server['name'])
            configuration_check = self.check_init_status(ss_api_config)
            if configuration_check.is_anchor_imported:
                self.log_info('Configuration anchor for \"' + security_server['name'] + '\" already imported')
            else:
                self.upload_anchor(ss_api_config, security_server)
            if configuration_check.is_server_code_initialized:
                self.log_info('Security server \"' + security_server['name'] + '\" already initialized')
            else:
                self.init_security_server(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def check_init_status(self, ss_api_config):
        try:
            initialization_api = InitializationApi(ApiClient(ss_api_config))
            response = initialization_api.get_initialization_status()
            return response
        except ApiException as err:
            self.log_api_error('InitializationApi->get_initialization_status', err)

    def upload_anchor(self, ss_api_config, security_server):
        try:
            self.log_info('Uploading configuration anchor for security server: ' + security_server['name'])
            system_api = SystemApi(ApiClient(ss_api_config))
            anchor = open(security_server["configuration_anchor"], "r")
            response = system_api.upload_initial_anchor(body=anchor.read())
            self.log_info('Upload of configuration anchor from \"' + security_server["configuration_anchor"] +
                          '\" successful')
            return response
        except ApiException as err:
            self.log_api_error('SystemApi->upload_initial_anchor', err)

    def init_security_server(self, ss_api_config, security_server):
        try:
            self.log_info('Initializing security server: ' + security_server['name'])
            initialization_api = InitializationApi(ApiClient(ss_api_config))
            response = initialization_api.init_security_server(body=InitialServerConf(
                owner_member_class=security_server["owner_member_class"],
                owner_member_code=security_server["owner_member_code"],
                security_server_code=security_server["security_server_code"],
                software_token_pin=security_server["software_token_pin"],
                ignore_warnings=True))
            self.log_info('Security server \"' + security_server["name"] + '\" initialized')
            return response
        except ApiException as err:
            self.log_api_error('InitializationApi->init_security_server', err)
