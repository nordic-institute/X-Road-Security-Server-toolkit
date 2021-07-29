from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.rest.rest import ApiException
from xrdsst.api_client.api_client import ApiClient
from xrdsst.api.tokens_api import TokensApi
from xrdsst.api.keys_api import KeysApi
from xrdsst.resources.texts import texts
from xrdsst.core.util import parse_argument_list, convert_list_to_string, cut_big_string
from xrdsst.models.key_name import KeyName

class KeyListMapper:
    @staticmethod
    def headers():
        return ['ID', 'LABEL', 'NAME', 'USAGE', 'POSSIBLE ACTIONS', 'Nº CERTS']

    @staticmethod
    def as_list(key):
        return [key.get('id'),
                key.get('label'),
                key.get('name'),
                key.get('usage'),
                key.get('possible_actions'),
                key.get('certificate_count')]

    @staticmethod
    def as_object(key):
        return {
            'id': key.get('id'),
            'label': key.get('label'),
            'name': key.get('name'),
            'usage': key.get('usage'),
            'possible_actions': key.get('possible_actions'),
            'certificate_count': key.get('certificate_count')
        }


class KeyController(BaseController):
    class Meta:
        label = 'key'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['key.controller.description']

    @ex(help="List keys",
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
            BaseController.log_info('The following parameters missing for listing keys: %s' % missing_parameters)
            return

        tokens = parse_argument_list(self.app.pargs.token)

        self.list_keys(active_config, self.app.pargs.ss, tokens)

    @ex(help="Delete keys",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'}),
            (['--key'], {'help': 'Key id(s)', 'dest': 'key'})
        ]
        )
    def delete(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.key is None:
            missing_parameters.append('key')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for deleting keys: %s' % missing_parameters)
            return

        keys = parse_argument_list(self.app.pargs.key)

        self.delete_keys(active_config, self.app.pargs.ss, keys)

    @ex(help="Update key",
        arguments=[
            (['--ss'], {'help': 'security server', 'dest': 'ss'}),
            (['--key'], {'help': 'Key id', 'dest': 'key'}),
            (['--name'], {'help': 'Key friendly name', 'dest': 'name'})
        ]
        )
    def update(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.key is None:
            missing_parameters.append('key')
        if self.app.pargs.name is None:
            missing_parameters.append('name')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for updating keys: %s' % missing_parameters)
            return

        self.update_keys(active_config, self.app.pargs.ss, self.app.pargs.key, self.app.pargs.name)

    def list_keys(self, config, ss_name, tokens):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            return self.remote_list_keys(ss_api_config, tokens)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_keys(self, config, ss_name, key_ids):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_delete_keys(ss_api_config, ss_name, key_ids)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def update_keys(self, config, ss_name, key_id, friendly_name):
        ss_api_conf_tuple = list(zip(config["security_server"],
                                     map(lambda ss: self.create_api_config(ss, config), config["security_server"])))
        security_servers = list(filter(lambda ss: ss["name"] == ss_name, config["security_server"]))
        if len(security_servers) > 0:
            ss_api_config = self.create_api_config(security_servers[0], config)
            self.remote_update_key(ss_api_config, ss_name, key_id, friendly_name)
        else:
            BaseController.log_info(self.security_server_not_found_message(ss_name))

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_list_keys(self, ss_api_config, tokens):
        tokens_api = TokensApi(ApiClient(ss_api_config))
        render_list = []
        render_data = []
        for token in tokens:
            try:
                token = tokens_api.get_token(token)
                render_list.extend(self.parse_token_response_to_key_list(token))
            except ApiException as err:
                BaseController.log_api_error("TokensApi=>get_token", err)

        if len(render_list) > 0:
            if self.is_output_tabulated():
                render_data = [KeyListMapper.headers()]
                render_data.extend(map(KeyListMapper.as_list, render_list))
            else:
                render_data.extend(map(KeyListMapper.as_object, render_list))
            self.render(render_data)

        return render_list

    @staticmethod
    def remote_delete_keys(ss_api_config, ss_name, key_ids):
        keys_api = KeysApi(ApiClient(ss_api_config))
        for key_id in key_ids:
            try:
                keys_api.delete_key(key_id)
                BaseController.log_info("Deleted key with id: %s, security server: %s" % (key_id, ss_name))
            except ApiException as err:
                BaseController.log_api_error("KeysApi=>delete_key", err)

    @staticmethod
    def remote_update_key(ss_api_config, ss_name, key_id, friendly_name):
        keys_api = KeysApi(ApiClient(ss_api_config))
        try:
            key = keys_api.get_key(key_id)
            if key:
                keys_api.update_key(key_id, body=KeyName(friendly_name))
            BaseController.log_info("Updated key with id: %s, security server: %s, new name: %s" % (key_id, ss_name, friendly_name))
        except ApiException as err:
            BaseController.log_info("Could not update key with id: %s, security server: %s, key not found" % (key_id, ss_name))

    @staticmethod
    def security_server_not_found_message(ss_name):
        return "Security server: '%s' not found" % ss_name

    @staticmethod
    def parse_token_response_to_key_list(token):
        for key in token.keys:
            yield {
                'id': key.id,
                'label': cut_big_string(key.label, 40),
                'name': cut_big_string(key.name,40),
                'usage': key.usage,
                'possible_actions': convert_list_to_string(key.possible_actions),
                'certificate_count': len(key.certificates)
            }
