from datetime import datetime
import os
import cement.utils.fs
from cement import ex
from xrdsst.api import SystemApi
from xrdsst.controllers.base import BaseController
from xrdsst.api_client.api_client import ApiClient
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException
from xrdsst.models.distinguished_name import DistinguishedName


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


class InternalTlsController(BaseController):
    class Meta:
        label = 'internal_tls'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['internal_tls.controller.description']

    @ex(help="Download internal TLS certificate, if any.", arguments=[])
    def download(self):
        active_config = self.load_config()

        return self.download_internal_tls(active_config)

    @ex(help="Generate new tls",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'})
        ])
    def generate_key(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for generating new key: %s' % missing_parameters)
            return

        self.generate_tls_keys(active_config, self.app.pargs.ss)

    @ex(help="Generate csr",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'}),
            (['--name'], {'help': 'Distinguished name', 'dest': 'name'})
        ])
    def generate_csr(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.name is None:
            missing_parameters.append('name')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for generating new csr: %s' % missing_parameters)
            return

        return self.generate_tls_csr(active_config, self.app.pargs.ss, self.app.pargs.name)

    @ex(help="Import TLS certificate", label="import",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'}),
            (['--cert'], {'help': 'TLS certificate path', 'dest': 'cert'})
        ])
    def import_(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.cert is None:
            missing_parameters.append('cert')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for generating new csr: %s' % missing_parameters)
            return

        self.import_tls_certificate(active_config, self.app.pargs.ss, self.app.pargs.cert)

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

    def generate_tls_csr(self, config, ss_name, name):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            return self.remote_generate_tls_csr(ss_api_config, ss_name, name)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def import_tls_certificate(self, config, ss_name, path):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_import_tls_certificate(ss_api_config, ss_name, path)
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
            system_api.generate_system_tls_key_and_certificate()
            BaseController.log_info("Generated TLS key and certificate for security server: '%s'" % ss_name)
        except ApiException as err:
            BaseController.log_api_error("SystemApi=>generate_system_tls_key_and_certificate", err)

    @staticmethod
    def remote_generate_tls_csr(ss_api_config, ss_name, name):
        system_api = SystemApi(ApiClient(ss_api_config))
        try:
            result = system_api.generate_system_certificate_request(body=DistinguishedName(name=name))
            if result:
                file_path = "/tmp/internal_tls_cert_request_%s.p10" % datetime.today().strftime('%Y%m%d%s')
                text_file = open(file_path, "wt")
                text_file.write(result)
                text_file.close()
                BaseController.log_info("Generated TLS CSR for security server: '%s', file saved into '%s'" % (ss_name, file_path))
            return result
        except ApiException as err:
            BaseController.log_api_error("SystemApi=>generate_system_certificate_request", err)

    @staticmethod
    def remote_import_tls_certificate(ss_api_config, ss_name, cert_path):
        system_api = SystemApi(ApiClient(ss_api_config))
        try:
            with open(cert_path, "r") as text_file:
                file_content = text_file.read()
                text_file.close()
                try:
                    cert_details = system_api.import_system_certificate(body=file_content)
                    BaseController.log_info("Imported TLS certificate: '%s', for security server: '%s'" % (cert_path, ss_name))
                    return cert_details
                except ApiException as err:
                    BaseController.log_info("Invalid certificate: '%s'" % cert_path)
                    BaseController.log_api_error("SystemApi=>generate_system_certificate_request", err)
        except IOError as err:
            BaseController.log_info("Could not read file: '%s'. %s" % (cert_path, err))

    @staticmethod
    def security_server_not_found_message(ss_name):
        return "Security server: '%s' not found" % ss_name
