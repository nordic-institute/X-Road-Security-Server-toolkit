import os

from xrdsst.controllers.base import BaseController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.core.definitions import ROOT_DIR
from xrdsst.main import XRDSSTTest


class InitializationTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_upload_anchor_fail_file_missing(self):
        base = BaseController()
        init = InitServerController()
        configuration_anchor = []
        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.upload_anchor(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_upload_anchor_fail_file_bogus_content(self):
        base = BaseController()
        init = InitServerController()
        configuration_anchor = []

        ssn = 0
        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor-bogus.xml")
            init.upload_anchor(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            ssn = ssn + 1

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_owner_member_class_missing(self):
        base = BaseController()
        init = InitServerController()
        member_class = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.test.config["security_server"]:
            member_class.append(security_server["owner_member_class"])
            self.test.config["security_server"][ssn]["owner_member_class"] = ''
            ssn = ssn + 1

        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["owner_member_class"] = member_class[ssn]
            self.test.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_owner_member_code_missing(self):
        base = BaseController()
        init = InitServerController()
        member_code = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.test.config["security_server"]:
            member_code.append(security_server["owner_member_code"])
            self.test.config["security_server"][ssn]["owner_member_code"] = ''
            ssn = ssn + 1

        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["owner_member_code"] = member_code[ssn]
            self.test.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_server_code_missing(self):
        base = BaseController()
        init = InitServerController()
        server_code = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.test.config["security_server"]:
            server_code.append(security_server["security_server_code"])
            self.test.config["security_server"][ssn]["security_server_code"] = ''
            ssn = ssn + 1

        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["security_server_code"] = server_code[ssn]
            self.test.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_initialize_server_token_pin_missing(self):
        base = BaseController()
        init = InitServerController()
        token_pin = []
        configuration_anchor = []

        ssn = 0
        for security_server in self.test.config["security_server"]:
            token_pin.append(security_server["software_token_pin"])
            self.test.config["security_server"][ssn]["software_token_pin"] = ''
            ssn = ssn + 1

        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False
            configuration_anchor.append(security_server["configuration_anchor"])
            security_server["configuration_anchor"] = ''
            init.init_security_server(configuration, security_server)
            status = init.check_init_status(configuration)
            assert status.is_server_code_initialized is False

        for ssn in range(0, len(self.test.config["security_server"])):
            self.test.config["security_server"][ssn]["software_token_pin"] = token_pin[ssn]
            self.test.config["security_server"][ssn]["configuration_anchor"] = configuration_anchor[ssn]

    def step_init(self):
        base = BaseController()
        init = InitServerController()
        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False
            assert status.is_server_code_initialized is False

        init.initialize_server(self.test.config)

        for security_server in self.test.config["security_server"]:
            configuration = base.create_api_config(security_server, self.test.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is True
            assert status.is_server_code_initialized is True

    def step_timestamp_init(self):
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = timestamp_controller.create_api_config(security_server, self.test.config)
                response = timestamp_controller.remote_get_configured(configuration)
                assert response == []
                timestamp_controller.remote_timestamp_service_init(configuration, security_server)
                response = timestamp_controller.remote_get_configured(configuration)
                assert len(response) > 0
                assert len(response[0].name) > 0
                assert len(response[0].url) > 0

    def step_token_login(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.test.config)
                token_controller.remote_token_login(configuration, security_server)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True

    def step_token_login_already_logged_in(self):
        with XRDSSTTest() as app:
            token_controller = TokenController()
            token_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = token_controller.create_api_config(security_server, self.test.config)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True
                assert 'LOGOUT' in response[0].possible_actions
                token_controller.remote_token_login(configuration, security_server)
                response = token_controller.remote_get_tokens(configuration)
                assert len(response) > 0
                assert response[0].logged_in is True
                assert 'LOGOUT' in response[0].possible_actions

    def test_run_configuration(self):
        self.step_upload_anchor_fail_file_missing()
        self.step_upload_anchor_fail_file_bogus_content()
        self.step_initialize_server_owner_member_class_missing()
        self.step_initialize_server_owner_member_code_missing()
        self.step_initialize_server_server_code_missing()
        self.step_initialize_server_token_pin_missing()
        self.step_init()
        self.step_timestamp_init()
        self.step_token_login()
        self.step_token_login_already_logged_in()
