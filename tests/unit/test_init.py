import unittest
from unittest.mock import patch
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import Init


class TestInit(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = Configuration()
        config.api_key['Authorization'] = 'apikey'
        config.host = "https://ss3:4000/api/v1"
        config.verify_ssl = False
        self._config = config

    @patch('xrdsst.api_client.api_client')
    def test_check_init_status(self, mock_requests):
        mock_requests.call_api.return_value = {'status': 400}
        init = Init()
        init.check_init_status(self._config)
