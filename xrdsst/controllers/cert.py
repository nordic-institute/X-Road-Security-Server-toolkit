import os

import cement.utils.fs

from cement import ex

from xrdsst.api import KeysApi
from xrdsst.api.token_certificates_api import TokenCertificatesApi
from xrdsst.controllers.base import BaseController
from xrdsst.core.api_util import remote_get_token
from xrdsst.core.util import default_auth_key_label, default_sign_key_label
from xrdsst.models import SecurityServerAddress, CsrFormat
from xrdsst.api_client.api_client import ApiClient
from xrdsst.resources.texts import texts

from xrdsst.rest.rest import ApiException


class DownloadedCsr:
    def __init__(self, csr_id, key_id, key_type, fs_loc):
        self.csr_id = csr_id
        self.key_id = key_id
        self.key_type = key_type
        self.fs_loc = fs_loc


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

    # requires token to be logged in
    @staticmethod
    def remote_import_certificates(ss_api_config, security_server):
        token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
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
                    token_cert_api.import_certificate(body=cert_data)
                    BaseController.log_info("Imported certificate '" + cert_file_loc + "'")
                except ApiException as err:
                    if err.status == 409 and err.body.count("certificate_already_exists"):
                        BaseController.log_info("Certificate '" + cert_file_loc + "' already imported.")
                    else:
                        BaseController.log_api_error('TokenCertificatesApi->import_certificate', err)

    @staticmethod
    def remote_register_certificate(ss_api_config, security_server):
        registrable_cert = CertController.find_actionable_auth_certificate(ss_api_config, security_server, 'REGISTER')
        if not registrable_cert:
            return None

        token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
        ss_address = SecurityServerAddress(BaseController.security_server_address(security_server))
        try:
            response = token_cert_api.register_certificate(registrable_cert.certificate_details.hash, body=ss_address)
            BaseController.log_info("Registered certificate " + registrable_cert.certificate_details.hash + " for address '" + str(ss_address) + "'")
            return response
        except ApiException as err:
            BaseController.log_api_error('TokenCertificatesApi->import_certificate', err)

    @staticmethod
    def remote_activate_certificate(ss_api_config, security_server):
        activatable_cert = CertController.find_actionable_auth_certificate(ss_api_config, security_server, 'ACTIVATE')
        if not activatable_cert:
            return None

        token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
        token_cert_api.activate_certificate(activatable_cert.certificate_details.hash)  # responseless PUT
        cert_actions = token_cert_api.get_possible_actions_for_certificate(activatable_cert.certificate_details.hash)
        if 'ACTIVATE' not in cert_actions:
            BaseController.log_info("Activated certificate " + activatable_cert.certificate_details.hash)
        else:
            BaseController.log_info("Could not activate certificate " + activatable_cert.certificate_details.hash)
        return cert_actions

    def remote_download_csrs(self, ss_api_config, security_server):
        key_labels = {
            'auth': default_auth_key_label(security_server),
            'sign': default_sign_key_label(security_server)
        }

        token = remote_get_token(ss_api_config, security_server)
        auth_keys = list(filter(lambda key: key.label == key_labels['auth'], token.keys))
        sign_keys = list(filter(lambda key: key.label == key_labels['sign'], token.keys))

        if not (auth_keys or sign_keys):
            return []

        keys_api = KeysApi(ApiClient(ss_api_config))
        downloaded_csrs = []

        for keytype in [(sign_keys, 'sign'), (auth_keys, 'auth')]:
            for key in keytype[0]:
                for csr in key.certificate_signing_requests:
                    with cement.utils.fs.Tmp(
                            prefix=csr_file_prefix(keytype[1], csr, security_server),
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
        if len(actionable_certs) > 1:
            BaseController.log_info("Multiple certificates to '" + cert_action + "' for key labelled '" + auth_key_label + "'.")
            return None

        return actionable_certs[0]


def csr_file_prefix(_type, key, security_server):
    return security_server['name'] + '-' + _type + "-CSR-" + key.id + "-"
