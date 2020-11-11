"""
PyTest Fixtures.
"""

import pytest


@pytest.fixture(scope="function")
def single_ss_config_for_init():
    config = {
        'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
        'security-server':
            [{'name': 'ss3',
              'url': 'https://ss3:4000/api/v1',
              'api_key': 'X-Road-apikey token=a2e9dea1-de53-4ebc-a750-6be6461d91f0',
              'configuration_anchor': '/etc/xroad/configuration-anchor.xml',
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS3',
              'software_token_pin': '1234'}]}
    return config
