from cement import ex

from xrdsst.api import DiagnosticsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException


class GlobalConfigurationListMapper:
    @staticmethod
    def headers():
        return ['SECURITY_SERVER', 'STATUS_CLASS', 'STATUS_CODE', 'PREV_UPDATE', 'NEXT_UPDATE']

    @staticmethod
    def as_list(global_conf):
        return [global_conf.get('security_server'),
                global_conf.get('status_class'),
                global_conf.get('status_code'),
                global_conf.get('prev_update_at'),
                global_conf.get('next_update_at')]

    @staticmethod
    def as_object(global_conf):
        return {
            'security_server': global_conf.get('security_server'),
            'status_class': global_conf.get('status_class'),
            'status_code': global_conf.get('status_code'),
            'prev_update_at': global_conf.get('prev_update_at'),
            'next_update_at': global_conf.get('next_update_at')
        }


class OCSPListMapper:
    @staticmethod
    def headers():
        return ['SECURITY_SERVER', 'NAME', 'URL', 'STATUS_CLASS', 'STATUS_CODE', 'PREV_UPDATE', 'NEXT_UPDATE']

    @staticmethod
    def as_list(ocsp):
        return [ocsp.get('security_server'),
                ocsp.get('name'),
                ocsp.get('url'),
                ocsp.get('status_class'),
                ocsp.get('status_code'),
                ocsp.get('prev_update_at'),
                ocsp.get('next_update_at')]

    @staticmethod
    def as_object(ocsp):
        return {
            'security_server': ocsp.get('security_server'),
            'name': ocsp.get('name'),
            'url': ocsp.get('url'),
            'status_class': ocsp.get('status_class'),
            'status_code': ocsp.get('status_code'),
            'prev_update_at': ocsp.get('prev_update_at'),
            'next_update_at': ocsp.get('next_update_at')
        }


class TimestampingServicesListMapper:
    @staticmethod
    def headers():
        return ['SECURITY_SERVER', 'URL', 'STATUS_CLASS', 'STATUS_CODE', 'PREV_UPDATE']

    @staticmethod
    def as_list(timestamping):
        return [timestamping.get('security_server'),
                timestamping.get('url'),
                timestamping.get('status_class'),
                timestamping.get('status_code'),
                timestamping.get('prev_update_at')]

    @staticmethod
    def as_object(timestamping):
        return {
            'security_server': timestamping.get('security_server'),
            'url': timestamping.get('url'),
            'status_class': timestamping.get('status_class'),
            'status_code': timestamping.get('status_code'),
            'prev_update_at': timestamping.get('prev_update_at')
        }


class DiagnosticsController(BaseController):
    class Meta:
        label = 'diagnostics'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['diagnostics.controller.description']

    GLOBAL_CONFIGURATION = 'global-configuration'
    OCSP_RESPONDERS = 'ocsp-responders'
    TIMESTAMPING_SERVICES = 'timestamping-services'

    @ex(help="List global configuration diagnostics", arguments=[])
    def global_configuration(self):
        active_config = self.load_config()
        self.list_diagnostics(active_config, operation=self.GLOBAL_CONFIGURATION)

    @ex(help="List OCSP diagnostics", arguments=[])
    def ocsp_responders(self):
        active_config = self.load_config()
        self.list_diagnostics(active_config, operation=self.OCSP_RESPONDERS)

    @ex(help="List timestamping services diagnostics", arguments=[])
    def timestamping_services(self):
        active_config = self.load_config()
        self.list_diagnostics(active_config, operation=self.TIMESTAMPING_SERVICES)

    @ex(help="List all diagnostics", arguments=[])
    def all(self):
        active_config = self.load_config()
        self.list_diagnostics(active_config, operation=self.GLOBAL_CONFIGURATION)
        self.list_diagnostics(active_config, operation=self.OCSP_RESPONDERS)
        self.list_diagnostics(active_config, operation=self.TIMESTAMPING_SERVICES)

    def list_diagnostics(self, config, operation):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            if operation == self.GLOBAL_CONFIGURATION:
                self.remote_list_global_configuration(ss_api_config, security_server)
            elif operation == self.OCSP_RESPONDERS:
                self.remote_list_ocsp_responders(ss_api_config, security_server)
            elif operation == self.TIMESTAMPING_SERVICES:
                self.remote_list_timestamping_services(ss_api_config, security_server)
            else:
                BaseController.log_info('Diagnostics operation is not provided')
        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_list_global_configuration(self, ss_api_config, security_server):
        diagnostics_api = DiagnosticsApi(ApiClient(ss_api_config))
        try:
            global_configuration_list = []
            global_conf_diagnostics = diagnostics_api.get_global_conf_diagnostics()
            if global_conf_diagnostics is not None:
                global_configuration_list.append({'security_server': security_server["name"],
                                                  'status_class': global_conf_diagnostics.status_class,
                                                  'status_code': global_conf_diagnostics.status_code,
                                                  'prev_update_at': global_conf_diagnostics.prev_update_at.strftime(
                                                      "%Y/%m/%d %H:%M:%S") if global_conf_diagnostics.prev_update_at else None,
                                                  'next_update_at': global_conf_diagnostics.next_update_at.strftime(
                                                      "%Y/%m/%d %H:%M:%S") if global_conf_diagnostics.next_update_at else None
                                                  })
            render_data = []
            if self.is_output_tabulated():
                render_data = [GlobalConfigurationListMapper.headers()]
                render_data.extend(map(GlobalConfigurationListMapper.as_list, global_configuration_list))
            else:
                render_data.extend(map(GlobalConfigurationListMapper.as_object, global_configuration_list))
            self.render(render_data)
            return global_configuration_list
        except ApiException as err:
            BaseController.log_api_error('DiagnosticsApi->get_global_conf_diagnostics', err)

    def remote_list_ocsp_responders(self, ss_api_config, security_server):
        diagnostics_api = DiagnosticsApi(ApiClient(ss_api_config))
        try:
            ocsp_list = []
            ocsp_diagnostics_list = diagnostics_api.get_ocsp_responders_diagnostics()
            for ocsp_diagnostics in ocsp_diagnostics_list:
                for ocsp_responder in ocsp_diagnostics.ocsp_responders:
                    ocsp_list.append({'security_server': security_server["name"],
                                      'name': ocsp_diagnostics.distinguished_name,
                                      'url': ocsp_responder.url,
                                      'status_class': ocsp_responder.status_class,
                                      'status_code': ocsp_responder.status_code,
                                      'prev_update_at': ocsp_responder.prev_update_at.strftime("%Y/%m/%d %H:%M:%S") if ocsp_responder.prev_update_at else None,
                                      'next_update_at': ocsp_responder.next_update_at.strftime("%Y/%m/%d %H:%M:%S") if ocsp_responder.next_update_at else None
                                      })
            render_data = []
            if self.is_output_tabulated():
                render_data = [OCSPListMapper.headers()]
                render_data.extend(map(OCSPListMapper.as_list, ocsp_list))
            else:
                render_data.extend(map(OCSPListMapper.as_object, ocsp_list))
            self.render(render_data)
            return ocsp_list
        except ApiException as err:
            BaseController.log_api_error('DiagnosticsApi->get_ocsp_responders_diagnostics', err)

    def remote_list_timestamping_services(self, ss_api_config, security_server):
        diagnostics_api = DiagnosticsApi(ApiClient(ss_api_config))
        try:
            timestamping_list = []
            timestamping_services_diagnostics_list = diagnostics_api.get_timestamping_services_diagnostics()
            for timestamping_services_diagnostics in timestamping_services_diagnostics_list:
                timestamping_list.append({'security_server': security_server["name"],
                                          'url': timestamping_services_diagnostics.url,
                                          'status_class': timestamping_services_diagnostics.status_class,
                                          'status_code': timestamping_services_diagnostics.status_code,
                                          'prev_update_at': timestamping_services_diagnostics.prev_update_at.strftime("%Y/%m/%d %H:%M:%S") if timestamping_services_diagnostics.prev_update_at else None
                                          })
            render_data = []
            if self.is_output_tabulated():
                render_data = [TimestampingServicesListMapper.headers()]
                render_data.extend(map(TimestampingServicesListMapper.as_list, timestamping_list))
            else:
                render_data.extend(map(TimestampingServicesListMapper.as_object, timestamping_list))
            self.render(render_data)
            return timestamping_list
        except ApiException as err:
            BaseController.log_api_error('DiagnosticsApi->get_timestamping_services_diagnostics', err)
