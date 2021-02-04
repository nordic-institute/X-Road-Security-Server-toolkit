from xrdsst.controllers.base import BaseController
from xrdsst.core.util import default_sign_key_label, default_auth_key_label
from xrdsst.main import opdep_init


def test_opdep_init_adds_app_opdep():
    class JustObject:
        pass

    mock_app = JustObject
    opdep_init(mock_app)
    assert mock_app.OP_GRAPH
    assert mock_app.OP_DEPENDENCY_LIST
    assert mock_app.OP_GRAPH.number_of_nodes() == len(mock_app.OP_DEPENDENCY_LIST)


def test_default_sign_key_label():
    security_server_config = {'name': 'ss-name1'}
    assert 'ss-name1-default-sign-key' == default_sign_key_label(security_server_config)


def test_default_auth_key_label():
    security_server_config = {'name': 'ss-name2'}
    assert 'ss-name2-default-auth-key' == default_auth_key_label(security_server_config)


def test_security_server_address_from_url():
    security_server_config = {'url': 'https://somehost:64000/api/v1'}
    assert 'somehost' == BaseController.security_server_address(security_server_config)
    security_server_config['url'] = 'http://otherhost/api/v1'
    assert 'otherhost' == BaseController.security_server_address(security_server_config)
    security_server_config['url'] = 'http://192.168.1.33:4000/api/v1'
    assert '192.168.1.33' == BaseController.security_server_address(security_server_config)
