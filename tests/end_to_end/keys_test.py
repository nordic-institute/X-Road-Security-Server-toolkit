from tests.util.test_util import get_token
from xrdsst.main import XRDSSTTest
from xrdsst.controllers.key import KeyController, KeyListMapper
from xrdsst.controllers.token import TokenController
from xrdsst.core.conf_keys import ConfKeysSecurityServer


class KeysTest:
    KEY_LABEL_AUTH = "Test_key_label_auth"
    KEY_LABEL_SIGN = "Test_key_label_sign"

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_create_test_csr(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.test.config)
                member_class = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CLASS]
                member_code = security_server[ConfKeysSecurityServer.CONF_KEY_MEMBER_CODE]
                member_name = security_server[ConfKeysSecurityServer.CONF_KEY_DN_ORG]

                token_controller.remote_token_add_all_keys_with_csrs(configuration,
                                                                     security_server,
                                                                     member_class,
                                                                     member_code,
                                                                     member_name,
                                                                     self.KEY_LABEL_AUTH,
                                                                     self.sign_key_label)

    def step_key_list(self):
        list_key_dic = []
        with XRDSSTTest() as app:
            key_controller = KeyController()
            key_controller.app = app
            key_controller.load_config = (lambda: self.test.config)
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = key_controller.create_api_config(security_server, self.test.config)
                token = get_token(self.test.config, "0", ssn)
                keys_count = len(token["keys"])

                key_list = key_controller.remote_list_keys(configuration, "0")
                for header in KeyListMapper.headers():
                    assert header in key_controller.app._last_rendered[0][0]

                assert len(key_controller.app._last_rendered[0]) == (keys_count + 1)

                list_key_dic.append({
                    'ss_name': security_server["name"],
                    'keys': key_list
                })
                ssn = ssn + 1

        return list_key_dic

    def step_key_update(self, key_list_dic):
        with XRDSSTTest() as app:
            key_controller = KeyController()
            key_controller.app = app
            key_controller.load_config = (lambda: self.test.config)
            new_key_name = "Test key name"
            for security_server in self.test.config["security_server"]:
                key_list = list(filter(lambda k: k["ss_name"] == security_server["name"], key_list_dic))[0]["keys"]
                key_to_update = key_list[0]
                configuration = key_controller.create_api_config(security_server, self.test.config)
                key_controller.remote_update_key(configuration, security_server["name"], key_to_update["id"], new_key_name)
                key_list_after = key_controller.remote_list_keys(configuration, "0")
                key_after_update = list(filter(lambda k: k["id"] == key_to_update["id"], key_list_after))[0]

                assert key_after_update["name"] == new_key_name

    def step_key_delete(self, key_list_dic):
        with XRDSSTTest() as app:
            key_controller = KeyController()
            key_controller.app = app
            key_controller.load_config = (lambda: self.test.config)
            for security_server in self.test.config["security_server"]:
                configuration = key_controller.create_api_config(security_server, self.test.config)
                key_list = list(filter(lambda k: k["ss_name"] == security_server["name"], key_list_dic))[0]["keys"]
                keys_to_delete = list(filter(lambda k: k["label"] == self.KEY_LABEL_AUTH or k["label"] == self.KEY_LABEL_SIGN, key_list))
                id_keys_to_delete = (k["id"] for k in keys_to_delete)
                key_controller.remote_delete_keys(configuration, security_server["name"], id_keys_to_delete)
                key_list_after = key_controller.remote_list_keys(configuration, "0")

                print("-----------------------------Len list 1: %s" + len(key_list))
                print("-----------------------------Len list after: %s" + len(key_list_after))

                # assert len(key_list_after) == (len(key_list) - 2)

    def test_run_configuration(self):
        key_list_dic = self.step_key_list()
        self.step_create_test_csr()
        self.step_key_update(key_list_dic)
        self.step_key_delete(key_list_dic)
