from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.api.keys_api import KeysApi
from xrdsst.resources.texts import texts
from xrdsst.core.util import parse_argument_list, convert_list_to_string


class CsrListMapper:
    @staticmethod
    def headers():
        return ['TOKEN', 'KEY ID', 'CSR ID', 'OWNER', 'USAGE', 'POSSIBLE ACTIONS']

    @staticmethod
    def as_list(key):
        return [key.get('token'),
                key.get('key_id'),
                key.get('csr_id'),
                key.get('owner'),
                key.get('usage'),
                key.get('possible_actions')]

    @staticmethod
    def as_object(key):
        return {
            'token': key.get('token'),
            'key_id': key.get('key_id'),
            'csr_id': key.get('csr_id'),
            'owner': key.get('owner'),
            'possible_actions': key.get('possible_actions'),
            'usage': key.get('usage')
        }


class CsrController(BaseController):
    class Meta:
        label = 'csr'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['csr.controller.description']

    @ex(help="List CSR",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'}),
            (['--token'], {'help': 'Token id(s)', 'dest': 'token'})
        ]
        )
    def list(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.token is None:
            missing_parameters.append('token')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for listing csr: %s' % missing_parameters)
            return

        tokens = parse_argument_list(self.app.pargs.token)

        self.list_csr(active_config, self.app.pargs.ss, tokens)

    @ex(help="Delete CSR",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'}),
            (['--key'], {'help': 'Key id(s)', 'dest': 'key'}),
            (['--csr'], {'help': 'CSR id(s)', 'dest': 'csr'})
        ]
        )
    def delete(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.key is None:
            missing_parameters.append('key')
        if self.app.pargs.csr is None:
            missing_parameters.append('csr')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for deleting csr: %s' % missing_parameters)
            return

        csrs = parse_argument_list(self.app.pargs.csr)

        self.delete_csr(active_config, self.app.pargs.ss, self.app.pargs.key, csrs)

    def list_csr(self, config, ss_name, tokens):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            return self.remote_list_csr(ss_api_config, tokens)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_csr(self, config, ss_name, key_id, csr_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            return self.remote_delete_csr(ss_api_config, security_servers[0]["name"], key_id, csr_ids)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_list_csr(self, ss_api_config, tokens):
        tokens_api = TokensApi(ApiClient(ss_api_config))
        render_list = []
        render_data = []
        for token_id in tokens:
            try:
                token = tokens_api.get_token(token_id)
                for key in token.keys:
                    render_list.extend(self.parse_key_response_to_csr(key, token_id))
            except ApiException as err:
                BaseController.log_api_error("TokensApi=>get_token", err)

        if len(render_list) > 0:
            if self.is_output_tabulated():
                render_data = [CsrListMapper.headers()]
                render_data.extend(map(CsrListMapper.as_list, render_list))
            else:
                render_data.extend(map(CsrListMapper.as_object, render_list))
            self.render(render_data)

        return render_list

    @staticmethod
    def remote_delete_csr(ss_api_config, ss_name, key_id, csr_ids):
        keys_api = KeysApi(ApiClient(ss_api_config))
        key = None
        try:
            key = keys_api.get_key(key_id)
        except ApiException:
            BaseController.log_info("Could not found key with id: '%s' for security server: '%s'" % (key_id, ss_name))
        if key:
            for csr_id in csr_ids:
                try:
                    keys_api.delete_csr(key_id, csr_id)
                    BaseController.log_info("Deleted CSR id: '%s', key id: '%s', security server: '%s'" % (csr_id, key_id, ss_name))
                except ApiException as err:
                    BaseController.log_api_error("KeysApi=>delete_key", err)

    @staticmethod
    def parse_key_response_to_csr(key, token):
        for csr in key.certificate_signing_requests:
            yield {
                'token': token,
                'key_id': key.id,
                'csr_id': csr.id,
                'owner': csr.owner_id if csr.owner_id else '',
                'usage': key.usage,
                'possible_actions': convert_list_to_string(csr.possible_actions),
            }

    @staticmethod
    def security_server_not_found_message(ss_name):
        return "Security server: '%s' not found" % ss_name
