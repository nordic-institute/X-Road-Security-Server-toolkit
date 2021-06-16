import os

import cement.utils.fs

from cement import ex

from xrdsst.api import KeysApi, SystemApi
from xrdsst.api.token_certificates_api import TokenCertificatesApi
from xrdsst.controllers.base import BaseController
from xrdsst.core.api_util import remote_get_token
from xrdsst.core.util import default_auth_key_label, default_sign_key_label, default_member_sign_key_label
from xrdsst.models import SecurityServerAddress, CsrFormat
from xrdsst.api_client.api_client import ApiClient
from xrdsst.resources.texts import texts

from xrdsst.rest.rest import ApiException
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients

class DownloadedCsr:
    def __init__(self, csr_id, key_id, key_type, fs_loc):
        self.csr_id = csr_id
        self.key_id = key_id
        self.key_type = key_type
        self.fs_loc = fs_loc


class DownloadedTLS:
    def __init__(self, security_server, fs_loc):
        self.security_server = security_server
        self.fs_loc = fs_loc

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

class DownloadedCsrListMapper:
    @staticmethod
    def headers():
        return ['CSR ID', 'KEY ID', 'TYPE', 'LOCATION']

    @staticmethod
    def as_list(dwn_csr):
        return [dwn_csr.csr_id, dwn_csr.key_id, dwn_csr.key_type, dwn_csr.fs_loc]

    @staticmethod
    def as_object(dwn_csr):
        return {
            'csr_id': dwn_csr.csr_id,
            'key_id': dwn_csr.key_id,
            'key_type': dwn_csr.key_type,
            'fs_location': dwn_csr.fs_loc
        }


class CertController(BaseController):
    class Meta:
        label = 'cert'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['cert.controller.description']

    @ex(help="Import certificate(s)", label="import", arguments=[])
    def import_(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.import_certificates(active_config)

    @ex(help="Register authentication certificate(s)", arguments=[])
    def register(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.register_certificate(active_config)

    @ex(help="Activate registered centrally approved authentication certificate", arguments=[])
    def activate(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.activate_certificate(active_config)

    @ex(help="Download certificate requests for sign and auth keys, if any.", arguments=[])
    def download_csrs(self):
        active_config = self.load_config()

        return self._download_csrs(active_config)

    @ex(help="Download internal TLS certificate, if any.", arguments=[])
    def download_tls(self):
        active_config = self.load_config()

        return self._download_internal_tls(active_config)

    @ex(help="Disable certificate(s)", arguments=[])
    def disable(self):
        active_config = self.load_config()
        full_op_path = self.op_path()

        active_config, invalid_conf_servers = self.validate_op_config(active_config)
        self.log_skipped_op_conf_invalid(invalid_conf_servers)

        if not self.is_autoconfig():
            active_config, insufficient_state_servers = self.regroup_server_ops(active_config, full_op_path)
            self.log_skipped_op_deps_unmet(full_op_path, insufficient_state_servers)

        self.disable_certificate(active_config)

    def import_certificates(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting certificate import process for security server: ' + security_server['name'])
            self.remote_import_certificates(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def register_certificate(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting certificate registration process for security server: ' + security_server['name'])
            self.remote_register_certificate(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def activate_certificate(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_debug('Starting certificate activation for security server: ' + security_server['name'])
            self.remote_activate_certificate(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def _download_csrs(self, config):
        downloaded_csrs = []
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_info('Starting CSR download from security server: ' + security_server['name'])
            downloaded_csrs.extend(self.remote_download_csrs(ss_api_config, security_server))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

        return downloaded_csrs

    def _download_internal_tls(self, config):
        downloaded_internal = []
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            BaseController.log_info('Starting TLS internal cert download from security server: ' + security_server['name'])
            downloaded_internal.extend(self.remote_download_internal_tls(ss_api_config, security_server))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

        return downloaded_internal

    def disable_certificate(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if "certificate_operations_hash" in security_server:
                BaseController.log_debug(
                    'Starting certificate disable process for security server: ' + security_server['name'])
                for certificate_hash in security_server["certificate_operations_hash"]:
                    ss_api_config = self.create_api_config(security_server, config)
                    self.remote_disable_certificate(ss_api_config, security_server, certificate_hash)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    # requires token to be logged in
    @staticmethod
    def remote_import_certificates(ss_api_config, security_server):
        token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
        imported_certs = []
        for cert in security_server["certificates"]:
            location = cement.utils.fs.join_exists(cert)
            if not location[1]:
                BaseController.log_info("Certificate '" + location[0] + "' does not exist")
            else:
                cert_file_loc = location[0]
                try:
                    cert_file = open(cert_file_loc, "rb")
                    cert_data = cert_file.read()
                    cert_file.close()
                    response = token_cert_api.import_certificate(body=cert_data)
                    BaseController.log_info("Imported certificate '" + cert_file_loc + "'")
                    imported_certs.append(response)
                except ApiException as err:
                    if err.status == 409 and err.body.count("certificate_already_exists"):
                        BaseController.log_info("Certificate '" + cert_file_loc + "' already imported.")
                    else:
                        BaseController.log_api_error('TokenCertificatesApi->import_certificate', err)
        return imported_certs

    @staticmethod
    def remote_register_certificate(ss_api_config, security_server):
        registrable_certs = CertController.find_actionable_auth_certificate(ss_api_config, security_server, 'REGISTER')
        if registrable_certs:
            for registrable_cert in registrable_certs:
                token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
                ss_address = SecurityServerAddress(BaseController.security_server_address(security_server))
                try:
                    token_cert_api.register_certificate(registrable_cert.certificate_details.hash, body=ss_address)
                    BaseController.log_info("Registered certificate " + registrable_cert.certificate_details.hash + " for address '" + str(ss_address) + "'")
                except ApiException as err:
                    BaseController.log_api_error('TokenCertificatesApi->import_certificate', err)

    @staticmethod
    def remote_activate_certificate(ss_api_config, security_server):
        activatable_certs = CertController.find_actionable_auth_certificate(ss_api_config, security_server, 'ACTIVATE')
        cert_actions = []
        if activatable_certs:
            for activatable_cert in activatable_certs:
                token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
                token_cert_api.activate_certificate(activatable_cert.certificate_details.hash)  # responseless PUT
                cert_actions.append(token_cert_api.get_possible_actions_for_certificate(activatable_cert.certificate_details.hash))
                if 'ACTIVATE' not in cert_actions:
                    BaseController.log_info("Activated certificate " + activatable_cert.certificate_details.hash)
                else:
                    BaseController.log_info("Could not activate certificate " + activatable_cert.certificate_details.hash)
            return cert_actions

    @staticmethod
    def remote_disable_certificate(ss_api_config, security_server, hash):

        token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
        ss_address = SecurityServerAddress(BaseController.security_server_address(security_server))
        try:
            token_cert_api.disable_certificate(hash)
            BaseController.log_info(
                "Registered certificate " + registrable_cert.certificate_details.hash + " for address '" + str(
                    ss_address) + "'")
        except ApiException as err:
            BaseController.log_api_error('TokenCertificatesApi->import_certificate', err)

    def remote_download_csrs(self, ss_api_config, security_server):

        key_labels = self.get_key_labels(security_server)

        token = remote_get_token(ss_api_config, security_server)
        auth_keys = list(filter(lambda key: key.label in key_labels['auth'], token.keys))
        sign_keys = list(filter(lambda key: key.label in key_labels['sign'], token.keys))

        if not (auth_keys or sign_keys):
            return []

        keys_api = KeysApi(ApiClient(ss_api_config))
        downloaded_csrs = []

        for keytype in [(sign_keys, 'sign'), (auth_keys, 'auth')]:
            for key in keytype[0]:
                for csr in key.certificate_signing_requests:
                    with cement.utils.fs.Tmp(
                            prefix=csr_file_prefix(keytype[1], key, csr),
                            suffix='.der',
                            cleanup=False
                    ) as tmp:
                        # Impossible to get valid byte array via generated client API conversion, resort to HTTP response.
                        http_response = keys_api.download_csr(key.id, csr.id, csr_format=CsrFormat.DER, _preload_content=False)
                        if 200 == http_response.status:
                            with open(tmp.file, 'wb') as file:
                                file.write(http_response.data)
                                downloaded_csrs.append(DownloadedCsr(csr.id, key.id, keytype[1].upper(), file.name))
                        else:
                            BaseController.log_info(
                                "Failed to download key '" + key.id + "' CSR '" + csr.id + "' (HTTP " + http_response.status + ", " + http_response.reason + ")"
                            )
                        # Remove empty folder that fs.Tmp creates and that would remain with auto-clean off
                        os.rmdir(tmp.dir)

        render_data = []
        if self.is_output_tabulated():
            render_data = [DownloadedCsrListMapper.headers()]
            render_data.extend(map(DownloadedCsrListMapper.as_list, downloaded_csrs))
        else:
            render_data.extend(map(DownloadedCsrListMapper.as_object, downloaded_csrs))

        self.render(render_data)
        return downloaded_csrs

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
                        "Failed to download TLS internal certifucate for security server '" + security_server["name"] + "' (HTTP " + http_response.status + ", " + http_response.reason + ")"
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
    def find_actionable_auth_certificate(ss_api_config, security_server, cert_action):
        token = remote_get_token(ss_api_config, security_server)
        # Find the authentication certificate by conventional name
        auth_key_label = default_auth_key_label(security_server)
        auth_keys = list(filter(lambda key: key.label == auth_key_label, token.keys))
        found_auth_key_count = len(auth_keys)
        if found_auth_key_count == 0:
            BaseController.log_info("Did not found authentication key labelled '" + auth_key_label + "'.")
            return None
        if found_auth_key_count > 1:
            BaseController.log_info("Found multiple authentication keys labelled '" + auth_key_label + "', skipping registration.")
            return None

        # So far so good, are there actual certificates attached to key?
        auth_key = auth_keys[0]
        if not auth_key.certificates:
            BaseController.log_info("No certificates available for authentication key labelled '" + auth_key_label + "'.")
            return None

        # Find actionable certs
        actionable_certs = list(filter(lambda c: cert_action in c.possible_actions, auth_key.certificates))
        if len(actionable_certs) == 0:
            BaseController.log_info("No certificates to '" + cert_action + "' for key labelled '" + auth_key_label + "'.")
            return None

        return actionable_certs

    def get_key_labels(self, security_server):
        key_labels = {
            'auth': [default_auth_key_label(security_server)],
            'sign': [default_sign_key_label(security_server)]
        }
        if "clients" in security_server:
            for client in security_server["clients"]:
                if client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CLASS] != security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS] \
                        or client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CODE] != security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE]:
                    key_label = default_member_sign_key_label(security_server, client)
                    if key_label not in key_labels["sign"]:
                        key_labels["sign"].append(key_label)

        return key_labels


def csr_file_prefix(_type, key, csr):
    return key.name + '-' + _type + "-CSR-" + csr.id + "-"





