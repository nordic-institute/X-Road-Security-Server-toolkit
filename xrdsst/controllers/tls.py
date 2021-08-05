import os

import cement.utils.fs
from cement import ex
from xrdsst.api import SystemApi
from xrdsst.controllers.base import BaseController
from xrdsst.core.util import  parse_argument_list
from xrdsst.api_client.api_client import ApiClient
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException


class DownloadedTLSListMapper:
    @staticmethod
    def headers():
        return ['SECURITY SERVER', 'LOCATION']

    @staticmethod
    def as_list(dwn_tls):
        return [dwn_tls.security_server, dwn_tls.fs_loc]

    @staticmethod
    def as_object(dwn_tls):
        return {
            'security_server': dwn_tls.security_server,
            'fs_loc': dwn_tls.fs_loc
        }


class DownloadedTLS:
    def __init__(self, security_server, fs_loc):
        self.security_server = security_server
        self.fs_loc = fs_loc


class TlsController(BaseController):
    class Meta:
        label = 'tls'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['tls.controller.description']

    @ex(help="Download internal TLS certificate, if any.", arguments=[])
    def download_tls(self):
        active_config = self.load_config()

        return self.download_internal_tls(active_config)

    @ex(help="Generate new tls",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'})
        ]
        )
    def generate_key(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for listing keys: %s' % missing_parameters)
            return

        tokens = parse_argument_list(self.app.pargs.token)

        self.list_keys(active_config, self.app.pargs.ss, tokens)

    def download_internal_tls(self, config):
        downloaded_internal = []
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_info('Starting TLS internal cert download from security server: ' + security_server['name'])
            downloaded_internal.extend(self.remote_download_internal_tls(ss_api_config, security_server))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

        return downloaded_internal

    def generate_tls_keys(self, config, ss_name):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_generate_tls_keys(ss_api_config, ss_name)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_download_internal_tls(self, ss_api_config, security_server):
        system_api = SystemApi(ApiClient(ss_api_config))
        downloaded_internal = []

        # Impossible to get valid byte array via generated client API conversion, resort to HTTP response.
        try:
            with cement.utils.fs.Tmp(
                    prefix=security_server["name"] + "_certs_",
                    suffix='.tar.gz',
                    cleanup=False
            ) as tmp:
                http_response = system_api.download_system_certificate(_preload_content=False)
                if 200 == http_response.status:
                    with open(tmp.file, 'wb') as file:
                        file.write(http_response.data)
                        downloaded_internal.append(DownloadedTLS(security_server["name"], file.name))
                else:
                    BaseController.log_info(
                        "Failed to download TLS internal certificate for security server '" + security_server[
                            "name"] + "' (HTTP " + http_response.status + ", " + http_response.reason + ")"
                    )

                # Remove empty folder that fs.Tmp creates and that would remain with auto-clean off
                os.rmdir(tmp.dir)
        except ApiException as err:
            BaseController.log_api_error("Failed to download the TLS internal cert", err)

        render_data = []
        if self.is_output_tabulated():
            render_data = [DownloadedTLSListMapper.headers()]
            render_data.extend(map(DownloadedTLSListMapper.as_list, downloaded_internal))
        else:
            render_data.extend(map(DownloadedTLSListMapper.as_object, downloaded_internal))

        self.render(render_data)
        return downloaded_internal

    @staticmethod
    def remote_generate_tls_keys(ss_api_config, ss_name):
        system_api = SystemApi(ApiClient(ss_api_config))
        try:
            result = system_api.generate_system_tls_key_and_certificate()
            BaseController.log_info("Generated TLS key and certificate for security server: '%s'" % ss_name)
        except:
            BaseController.log_api_error("SystemApi=>generate_system_tls_key_and_certificate")

