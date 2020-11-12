import pytest
import urllib3
from xrdsst.configuration.configuration import Configuration


@pytest.mark.usefixtures("single_ss_config_for_init")
def test_init_single_ss(single_ss_config_for_init):
    # TODO: security server configuration has to be reset before running this test
    configuration = init_configuration(single_ss_config_for_init)
    pass


def init_configuration(config_file):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    configuration = Configuration()
    configuration.api_key['Authorization'] = config_file["security-server"][0]["api_key"]
    configuration.host = config_file["security-server"][0]["url"]
    configuration.verify_ssl = False
    return configuration
