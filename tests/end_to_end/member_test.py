from xrdsst.controllers.base import BaseController
from xrdsst.controllers.member import MemberController
from xrdsst.main import XRDSSTTest


class MemberTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_member_find(self):
        with XRDSSTTest() as app:
            base = BaseController()
            member_controller = MemberController()
            member_controller.app = app

            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = member_controller.remote_find_name(configuration,
                                                              security_server,
                                                              security_server["owner_member_class"],
                                                              security_server["owner_member_code"])
                assert response.member_name == security_server["owner_dn_org"]

    def step_member_list_classes(self):
        with XRDSSTTest() as app:
            base = BaseController()
            member_controller = MemberController()
            member_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = member_controller.remote_list_classes(configuration, security_server, 'DEV')
                assert response == ['COM', 'PRIVATE-FOR-DEV', 'ORG', 'GOV']

    def test_run_configuration(self):
        self.step_member_find()
        self.step_member_list_classes()
