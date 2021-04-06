from cement import ex

from xrdsst.controllers.base import BaseController
from xrdsst.core.api_util import ServerStatus, status_server, StatusRoles
from xrdsst.resources.texts import texts


class StatusListMapper:
    @staticmethod
    def iso_datetime_str(dt):
        return dt.strftime(dt.isoformat()) if dt else None

    @staticmethod
    def server_id(server_init_status):
        return server_init_status.id_ if (server_init_status.has_server_code and server_init_status.has_server_owner) else None

    @staticmethod
    def headers():
        return ['GLOBAL', 'SERVER', 'ROLES', 'INIT', 'TSAS', 'TOKEN', 'KEYS', 'CSRS', 'CERTS']

    @staticmethod
    def as_list(server_status: ServerStatus):
        if not server_status.roles_status.permitted:
            result = ['' for _ in range(7)]
            result.insert(1, server_status.security_server_name)
            result.insert(2, server_status.roles_status.to_status_str())
            return result
        return [
            server_status.global_status.to_status_str(),
            server_status.security_server_name + '\n' +
            server_status.version_status.to_status_str() + '\n' +
            next((sid for sid in [StatusListMapper.server_id(server_status.server_init_status)] if sid is not None), ''),
            server_status.roles_status.to_status_str(),
            server_status.server_init_status.to_status_str(),
            '\n'.join(map(lambda tss: tss.name, server_status.timestamping_status)),
            server_status.token_status.to_status_str(),
            server_status.status_keys.to_status_str(),
            server_status.status_csrs.to_status_str(),
            server_status.status_certs.to_status_str()
        ]

    @staticmethod
    def as_object(server_status):
        return {
            'security_server': {
                'name': server_status.security_server_name,
                'version': server_status.version_status.version,
                'id': next((sid for sid in [StatusListMapper.server_id(server_status.server_init_status)] if sid is not None), ''),
                'global_status': {
                    'class': server_status.global_status.class_,
                    'code': server_status.global_status.code,
                    'updated': StatusListMapper.iso_datetime_str(server_status.global_status.updated),
                    'refresh': StatusListMapper.iso_datetime_str(server_status.global_status.refresh)
                },
                'roles': server_status.roles_status.roles,
                'initialization': {
                    'has_anchor': server_status.server_init_status.has_anchor,
                    'has_server_code': server_status.server_init_status.has_server_code,
                    'server_code': server_status.server_init_status.server_code,
                    'has_server_owner': server_status.server_init_status.has_server_owner,
                    'server_owner': server_status.server_init_status.server_owner,
                    'token_init_status': server_status.server_init_status.token_init_status
                },
                'tsa_list': list(map(lambda x: {'name': x.name, 'url': x.url}, server_status.timestamping_status)),
                'token': {
                    'id': server_status.token_status.id,
                    'name': server_status.token_status.name,
                    'status': server_status.token_status.status,
                    'logged_in': server_status.token_status.logged_in
                },
                'keys': {
                    'key_count': server_status.status_keys.key_count,
                    'sign_key_count': server_status.status_keys.sign_key_count,
                    'auth_key_count': server_status.status_keys.auth_key_count,
                    'has_sign_key': server_status.status_keys.has_sign_key,
                    'has_toolkit_sign_key': server_status.status_keys.has_toolkit_sign_key,
                    'toolkit_sign_key_id': server_status.status_keys.toolkit_sign_key_id,
                    'has_auth_key': server_status.status_keys.has_auth_key,
                    'has_toolkit_auth_key': server_status.status_keys.has_toolkit_auth_key,
                    'toolkit_auth_key_id': server_status.status_keys.toolkit_auth_key_id,
                },
                'csrs': {
                    'sign_csr_count': server_status.status_csrs.sign_csr_count,
                    'auth_csr_count': server_status.status_csrs.auth_csr_count,
                    'has_toolkit_sign_csr': server_status.status_csrs.has_toolkit_sign_csr,
                    'has_sign_csr': server_status.status_csrs.has_sign_csr,
                    'has_toolkit_auth_csr': server_status.status_csrs.has_toolkit_auth_csr,
                    'has_auth_csr': server_status.status_csrs.has_auth_csr
                },
                'certificates': {
                    'has_toolkit_sign_cert': server_status.status_certs.has_toolkit_sign_cert,
                    'toolkit_sign_cert_hash': server_status.status_certs.toolkit_sign_cert_hash,
                    'has_sign_cert': server_status.status_certs.has_sign_cert,
                    'has_toolkit_auth_cert': server_status.status_certs.has_toolkit_auth_cert,
                    'toolkit_auth_cert_hash': server_status.status_certs.toolkit_auth_cert_hash,
                    'has_auth_cert': server_status.status_certs.has_auth_cert,
                    'has_registered_auth_cert': server_status.status_certs.has_registered_auth_cert
                }
            }
        }


class StatusController(BaseController):
    class Meta:
        label = 'status'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['status.controller.description']

    @ex(help='status', hide=True)
    def _default(self):
        return self._status(self.load_config())  # Returned for status comparisons in tests only

    def _status(self, config):
        render_data = []
        servers = []
        if config.get("security_server"):
            ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

            for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1]]:
                servers.append(self.remote_status(ss_api_config, security_server))

            # Ensure that servers that are missing API KEY still show up in the list (name, no access).
            for security_server, ss_api_config in [t for t in ss_api_conf_tuple if t[1] is None]:
                servers.append(ServerStatus(
                    security_server_name=security_server['name'],
                    roles_status=StatusRoles()
                ))

        if self.is_output_tabulated():
            render_data = [StatusListMapper.headers()]
            render_data.extend(map(StatusListMapper.as_list, servers))
        else:
            render_data.extend(map(StatusListMapper.as_object, servers))

        self.render(render_data)
        if self.is_output_tabulated() and not config.get("security_server"):
            print(texts['message.config.serverless'])

        return servers

    @staticmethod
    def remote_status(ss_configuration, security_server):
        return status_server(ss_configuration, security_server)
