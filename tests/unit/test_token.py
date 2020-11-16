import unittest
import urllib3
from xrdsst.controllers.token import TokenController

class TestToken(unittest.TestCase):
    ss_config = {
        'logging': [{'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'}],
        'security-server':
            [{'name': 'ssX',
              'url': 'https://192.168.1.1:8999/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'configuration_anchor': '/tmp/configuration-anchor.xml',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122'}]}

    def test_token_list(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.ss_config)
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: token_controller.list())

    def test_token_login(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.ss_config)
        self.assertRaises(urllib3.exceptions.MaxRetryError, lambda: token_controller.login())