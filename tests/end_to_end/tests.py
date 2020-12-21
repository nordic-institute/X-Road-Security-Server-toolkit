import os
import sys
import unittest
import urllib3

from xrdsst.controllers.base import BaseController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest


class EndToEndTest(unittest.TestCase):
    config_file = None
    config = None

    def setUp(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        idx = 0
        for arg in sys.argv:
            idx += 1
            if arg == "-c":
                self.config_file = sys.argv[idx]

    def tearDown(self):
        if self.config_file is not None:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)

    def step_init(self):
        base = BaseController()
        init = InitServerController()
        self.config = base.load_config(baseconfig=self.config_file)
        for security_server in self.config["security_server"]:
            configuration = init.initialize_basic_config_values(security_server, self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is False and status.is_server_code_initialized is False
            init.initialize_server(self.config)
            status = init.check_init_status(configuration)
            assert status.is_anchor_imported is True and status.is_server_code_initialized is True

    def step_timestamp_init(self):
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            for security_server in self.config["security_server"]:
                configuration = timestamp_controller.initialize_basic_config_values(security_server, self.config)
                response = timestamp_controller.remote_get_configured(configuration)
                assert response == []
                timestamp_controller.remote_timestamp_service_init(configuration, security_server)
                response = timestamp_controller.remote_get_configured(configuration)
                assert len(response) > 0
                assert len(response[0].name) > 0
                assert len(response[0].url) > 0

    def step_token_login(self):
        token_controller = TokenController()
        for security_server in self.config["security_server"]:
            configuration = token_controller.initialize_basic_config_values(security_server, self.config)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert response[0].logged_in is False
            token_controller.remote_token_login(configuration, security_server)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert response[0].logged_in is True

    def step_token_init_keys(self):
        token_controller = TokenController()
        for security_server in self.config["security_server"]:
            configuration = token_controller.initialize_basic_config_values(security_server, self.config)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert len(response[0].keys) == 0
            token_controller.remote_token_add_keys_with_csrs(configuration, security_server)
            response = token_controller.remote_get_tokens(configuration)
            assert len(response) > 0
            assert len(response[0].keys) == 2
            auth_key_label = security_server['name'] + '-default-auth-key'
            sign_key_label = security_server['name'] + '-default-sign-key'
            assert str(response[0].keys[0].label) == auth_key_label
            assert str(response[0].keys[1].label) == sign_key_label

    def test_run_configuration(self):
        self.step_init()
        self.step_timestamp_init()
        self.step_token_login()
        self.step_token_init_keys()
