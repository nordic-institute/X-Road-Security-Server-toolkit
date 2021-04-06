import logging

from cement import ex
from xrdsst.api_client.api_client import ApiClient
from xrdsst.resources.texts import texts
from xrdsst.api.system_api import SystemApi
from .base import BaseController
from ..api import TimestampingServicesApi
from ..models import TimestampingService
from ..rest.rest import ApiException


class TimestampServiceListMapper:
    @staticmethod
    def headers():
        return ['NAME', 'URL']

    @staticmethod
    def as_list(timestamping_service):
        return [timestamping_service.name, timestamping_service.url]

    @staticmethod
    def as_object(timestamping_service):
        return {
            'name': timestamping_service.name,
            'url': timestamping_service.url
        }


class TimestampController(BaseController):
    class Meta:
        label = 'timestamp'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['timestamp.controller.description']

    # Possible listing approaches for later:
    #   merged, with approval/configuration flags
    #   separate, separate subcommands
    #   merged, with separate command line filtering (--approved, ... etc)

    # Protobonus: approved timestamp services list
    @ex(label='list-approved', help='List approved timestamping services.', arguments=[])
    def list_approved(self):
        active_config = self.load_config()
        self.timestamp_service_list_approved(active_config)

    # Protobonus: configured timestamp services list
    @ex(label='list-configured', help='List configured timestamping services', arguments=[])
    def list_configured(self):
        active_config = self.load_config()
        self.timestamp_service_list(active_config)

    @ex(help='Select and activate single approved timestamping service.', arguments=[])
    def init(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.timestamp_service_init(active_config)

    def timestamp_service_list(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1]]:
            self.remote_timestamp_service_list(ss_api_config)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def timestamp_service_list_approved(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1]]:
            self.remote_timestamp_service_list_approved(ss_api_config)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def render_timestamping_services(self, ts_list):
        render_data = []
        if self.is_output_tabulated():
            render_data = [TimestampServiceListMapper.headers()]
            render_data.extend(map(TimestampServiceListMapper.as_list, ts_list))
        else:
            render_data.extend(map(TimestampServiceListMapper.as_object, ts_list))
        self.render(render_data)

    # Helper for timestamping services listing via TimestampingServices & System APIs.
    def remote_ts_list(self, apicall):
        try:
            ts_list_response = apicall()
            self.render_timestamping_services(ts_list_response)
        except ApiException as e:
            print("Exception when listing timestamping services: %s\n", e)

    @staticmethod
    def get_approved_timestamping_services(ss_api_config):
        timestamping_api = TimestampingServicesApi(ApiClient(ss_api_config))
        return timestamping_api.get_approved_timestamping_services()

    def remote_timestamp_service_list_approved(self, ss_api_config):
        self.remote_ts_list(lambda: self.get_approved_timestamping_services(ss_api_config))

    def remote_timestamp_service_list(self, ss_api_config):
        system_api = SystemApi(ApiClient(ss_api_config))
        self.remote_ts_list(lambda: system_api.get_configured_timestamping_services())

    @staticmethod
    def remote_get_configured(ss_api_config):
        try:
            system_api = SystemApi(ApiClient(ss_api_config))
            ts_list_response = system_api.get_configured_timestamping_services()
            return ts_list_response
        except ApiException as e:
            print("Exception when listing timestamping services: %s\n", e)

    def timestamp_service_init(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1]]:
            self.remote_timestamp_service_init(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_timestamp_service_init(self, ss_api_config, security_server):
        try:
            approved_ts = self.get_approved_timestamping_services(ss_api_config)
            if approved_ts:
                system_api = SystemApi(ApiClient(ss_api_config))
                ts_init_response = system_api.add_configured_timestamping_service(
                    body=TimestampingService(name=approved_ts[0].name, url=approved_ts[0].url)
                )
                if ts_init_response:  # single timestamping service added is also returned
                    print(security_server['name'])
                    self.render_timestamping_services([ts_init_response])
        except ApiException as excn:
            if 409 == excn.status:
                print(security_server['name'], "Timestamping service already configured.")
            else:
                tsiferr_msg = "Timestamping service initialization configuration failure"
                print(security_server['name'], tsiferr_msg, excn)
                logging.error(security_server['name'] + ' ' + tsiferr_msg, excn)
