import pytest
import urllib3
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.init import Init


@pytest.mark.usefixtures("single_ss_config_for_init")
def test_init_single_ss(single_ss_config_for_init):
    # TODO: security server configuration has to be reset before running this test
    configuration = init_configuration(single_ss_config_for_init)
    configuration_check = Init.check_init_status(configuration)
    init = Init()
    assert configuration_check.is_anchor_imported is False
    assert configuration_check.is_server_code_initialized is False
    Init.initialize_server(init, single_ss_config_for_init)
    assert configuration_check.is_anchor_imported is True
    assert configuration_check.is_server_code_initialized is True


def init_configuration(config_file):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    configuration = Configuration()
    configuration.api_key['Authorization'] = config_file["security-server"][0]["api_key"]
    configuration.host = config_file["security-server"][0]["url"]
    configuration.verify_ssl = False
    return configuration
