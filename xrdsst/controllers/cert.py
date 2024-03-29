import os

import cement.utils.fs
from cement import ex
from xrdsst.api import KeysApi
from xrdsst.api.token_certificates_api import TokenCertificatesApi
from xrdsst.api.tokens_api import TokensApi
from xrdsst.controllers.base import BaseController
from xrdsst.core.api_util import remote_get_token
from xrdsst.core.util import default_auth_key_label, default_sign_key_label, default_member_sign_key_label, parse_argument_list
from xrdsst.models import SecurityServerAddress, CsrFormat
from xrdsst.api_client.api_client import ApiClient
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException
from xrdsst.core.conf_keys import ConfKeysSecurityServer, ConfKeysSecServerClients
from xrdsst.models.key_usage_type import KeyUsageType


class DownloadedCsr:
    def __init__(self, csr_id, key_id, key_type, fs_loc):
        self.csr_id = csr_id
        self.key_id = key_id
        self.key_type = key_type
        self.fs_loc = fs_loc


class CertOperations:
    @staticmethod
    def disable(token_cert_api):
        return {
            "method": token_cert_api.disable_certificate,
            "message": "Disable"
        }

    @staticmethod
    def unregister(token_cert_api):
        return {
            "method": token_cert_api.unregister_auth_certificate,
            "message": "Unregister"
        }

    @staticmethod
    def delete(token_cert_api):
        return {
            "method": token_cert_api.delete_certificate,
            "message": "Delete"
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

    @ex(help="List certificates with status information.", arguments=[])
    def list(self):
        active_config = self.load_config()
        certificates_list = self.list_certificates(active_config)

        if len(certificates_list) > 0:
            render_data = []
            headers = [*certificates_list[0]]
            render_data.append(headers)
            for item in certificates_list:
                render_data.append([*item.values()])

            self.render(render_data)
            return certificates_list

    @ex(help="Disable certificate(s)",
        arguments=[
            (['--hash'], {'help': 'certificate hash', 'dest': 'hash'})
        ]
        )
    def disable(self):
        active_config = self.load_config()

        if self.app.pargs.hash is None:
            self.log_info('Certificate hash parameter is required for disable certificates')
            return

        self.cert_operation(active_config, CertOperations.disable, parse_argument_list(self.app.pargs.hash))

    @ex(help="Unregister certificate(s)",
        arguments=[
            (['--hash'], {'help': 'certificate hash', 'dest': 'hash'})
        ]
        )
    def unregister(self):
        active_config = self.load_config()

        if self.app.pargs.hash is None:
            self.log_info('Certificate hash parameter is required for unregister certificates')
            return

        self.cert_operation(active_config, CertOperations.unregister, parse_argument_list(self.app.pargs.hash))

    @ex(help="Delete certificate(s)",
        arguments=[
            (['--hash'], {'help': 'certificate hash', 'dest': 'hash'})
        ]
        )
    def delete(self):
        active_config = self.load_config()

        if self.app.pargs.hash is None:
            self.log_info('Certificate hash parameter is required for delete certificates')
            return

        self.cert_operation(active_config, CertOperations.delete, parse_argument_list(self.app.pargs.hash))

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

    def list_certificates(self, config):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        certificates_list = []
        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            certificates = self.remote_list_certificates(ss_api_config, security_server["name"])
            if len(certificates) > 0:
                certificates_list.extend(certificates)
            else:
                BaseController.log_info("No certificates found for security server: %s" % security_server["name"])
        BaseController.log_keyless_servers(ss_api_conf_tuple)
        return certificates_list

    def cert_operation(self, config, operation, hashes):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            BaseController.log_debug(
                'Starting certificate operation process for security server: ' + security_server['name'])
            ss_api_config = self.create_api_config(security_server, config)
            for certificate_hash in hashes:
                self.remote_cert_operation(ss_api_config, security_server, certificate_hash, operation)
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
    def remote_cert_operation(ss_api_config, security_server, hash_value, operation):
        token_cert_api = TokenCertificatesApi(ApiClient(ss_api_config))
        try:
            operation_dict = operation(token_cert_api)
            token_certificate = token_cert_api.get_certificate(hash_value)

            if token_certificate:
                try:
                    operation_dict["method"](hash_value)
                    BaseController.log_info("%s certificate with hash: '%s', subject: '%s', exoiration date: '%s' for security server '%s'"
                                            % (operation_dict["message"], token_certificate.certificate_details.hash,
                                               token_certificate.certificate_details.subject_distinguished_name,
                                               token_certificate.certificate_details.not_after.strftime("%Y/%m/%d"), security_server["name"]))
                except ApiException as err:
                    if err.status == 409 and err.body.count("action_not_possible"):
                        BaseController.log_info("%s certificate with hash: '%s' for security server: '%s', already %s"
                                                % (operation_dict["message"], hash_value, security_server["name"], operation_dict["message"].lower()))
                    else:
                        BaseController.log_api_error('TokenCertificatesApi->disable_certificate', err)
            else:
                BaseController.log_info("Could not find any certificate with hash; '%s' for security server: '%s'" % (hash_value, security_server["name"]))
        except ApiException:
            BaseController.log_info("Could not find certificate with hash: '%s' for security server: '%s'" % (hash_value, security_server["name"]))

    def remote_download_csrs(self, ss_api_config, security_server):
        token = remote_get_token(ss_api_config, security_server)
        auth_keys = list(filter(lambda key: key.usage == KeyUsageType.AUTHENTICATION, token.keys))
        sign_keys = list(filter(lambda key: key.usage == KeyUsageType.SIGNING, token.keys))

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

    @staticmethod
    def remote_list_certificates(ss_api_config, ss_name):
        tokens_api = TokensApi(ApiClient(ss_api_config))
        try:
            tokens = tokens_api.get_tokens()
            return parse_tokens_into_cert_table(tokens, ss_name)
        except ApiException as err:
            BaseController.log_api_error('TokensApi->get_tokens', err)

    @staticmethod
    def find_actionable_auth_certificate(ss_api_config, security_server, cert_action):
        token = remote_get_token(ss_api_config, security_server)
        # Find the authentication certificate by conventional name
        auth_key_label = default_auth_key_label(security_server)
        auth_keys = list(filter(lambda key: auth_key_label in key.label, token.keys))
        found_auth_key_count = len(auth_keys)
        if found_auth_key_count == 0:
            BaseController.log_info("Did not found authentication key labelled '" + auth_key_label + "'.")
            return None

        actionable_certs = []
        # So far so good, are there actual certificates attached to key?
        for auth_key in auth_keys:
            if not auth_key.certificates:
                BaseController.log_info("No certificates available for authentication key labelled '" + auth_key_label + "'.")
                return None

            # Find actionable certs
            actionable_certs.extend(list(filter(lambda c: cert_action in c.possible_actions, auth_key.certificates)))
            if len(actionable_certs) == 0:
                BaseController.log_info("No certificates to '" + cert_action + "' for key labelled '" + auth_key_label + "'.")

        return actionable_certs

    @staticmethod
    def get_key_labels(security_server):
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


def parse_tokens_into_cert_table(tokens, ss_name):
    certificates_table = []
    for token in tokens:
        for key in token.keys:
            for certificate in key.certificates:
                certificates_table.append({
                    'ss': ss_name,
                    'label': key.label,
                    'type': key.usage,
                    'hash': certificate.certificate_details.hash,
                    'active': certificate.active,
                    'expiration': certificate.certificate_details.not_after.strftime("%Y/%m/%d"),
                    'ocsp_status': certificate.ocsp_status,
                    'status': certificate.status,
                    'subject': get_serial_number(certificate.certificate_details.subject_distinguished_name)
                })
    return certificates_table


def get_serial_number(subject):
    return subject.split(',')[0].split('=')[1] if subject else ''
