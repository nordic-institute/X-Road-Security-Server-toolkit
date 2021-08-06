from tests.util.test_util import get_token
from xrdsst.main import XRDSSTTest
from xrdsst.controllers.csr import CsrController, CsrListMapper
from xrdsst.controllers.token import TokenController
from xrdsst.core.conf_keys import ConfKeysSecurityServer


class CsrTest:

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

                auth_key_label = security_server["name"] + "_test_auth_key"
                sign_key_label = security_server["name"] + "_test_sign_key"
                token_controller.remote_token_add_all_keys_with_csrs(configuration,
                                                                     security_server,
                                                                     member_class,
                                                                     member_code,
                                                                     member_name,
                                                                     auth_key_label,
                                                                     sign_key_label)

    def step_csr_list(self):
        list_csr_dic = []
        with XRDSSTTest() as app:
            csr_controller = CsrController()
            csr_controller.app = app
            csr_controller.load_config = (lambda: self.test.config)
            ssn = 0
            for security_server in self.test.config["security_server"]:
                configuration = csr_controller.create_api_config(security_server, self.test.config)
                token = get_token(self.test.config, "0", ssn)
                csr_count = 0
                for key in token["keys"]:
                    csr_count = csr_count + len(key["certificate_signing_requests"])

                csr_list = csr_controller.remote_list_csr(configuration, ["0"])
                for header in CsrListMapper.headers():
                    assert header in csr_controller.app._last_rendered[0][0]

                assert len(csr_controller.app._last_rendered[0]) == (csr_count + 1)

                list_csr_dic.append({
                    'ss_name': security_server["name"],
                    'csrs': csr_list
                })
                ssn = ssn + 1

        return list_csr_dic

    def step_csr_delete(self, csr_list_dic):
        with XRDSSTTest() as app:
            csr_controller = CsrController()
            csr_controller.app = app
            csr_controller.load_config = (lambda: self.test.config)
            for security_server in self.test.config["security_server"]:
                configuration = csr_controller.create_api_config(security_server, self.test.config)
                csr_list = list(filter(lambda k: k["ss_name"] == security_server["name"], csr_list_dic))[0]["csrs"]

                for csr_to_delete in csr_list:
                    csr_controller.remote_delete_csr(configuration, security_server["name"], csr_to_delete["key_id"], [csr_to_delete["csr_id"]])

                csr_list_after = csr_controller.remote_list_csr(configuration, "0")

                assert len(csr_list_after) == 0

    def test_run_configuration(self):
        self.step_create_test_csr()
        list_csr_dic = self.step_csr_list()
        self.step_csr_delete(list_csr_dic)
