import os

from xrdsst.controllers.base import BaseController
from xrdsst.core.excplanation import http_status_code_to_text
from xrdsst.core.util import default_sign_key_label, default_auth_key_label, get_admin_credentials, get_ssh_user, get_ssh_key
from xrdsst.main import opdep_init


def test_opdep_init_adds_app_opdep():
    class JustObject:
        pass

    mock_app = JustObject
    opdep_init(mock_app)
    assert mock_app.OP_GRAPH
    assert mock_app.OP_DEPENDENCY_LIST
    assert mock_app.OP_GRAPH.number_of_nodes() == len(mock_app.OP_DEPENDENCY_LIST)

def test_admin_credentials_from_root_level_when_empty_at_security_server_section():
    os.environ['TOOLKIT_ADMIN_CREDENTIALS'] = 'admin:pass'
    config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'admin_credentials': 'another_admin',
              'ssh_user': 'ssh_user',
              'ssh_private_key': 'private_key'}]}
    security_server = {
            'admin_credentials': '',
            'ssh_user': '',
            'ssh_private_key': ''}
    assert 'admin:pass' == get_admin_credentials(security_server, config)

def test_admin_credentials_from_root_level_when_missing_at_security_server_section():
    os.environ['TOOLKIT_ADMIN_CREDENTIALS'] = 'admin:pass'
    config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'admin_credentials': 'another_admin',
              'ssh_user': 'ssh_user',
              'ssh_private_key': 'private_key'}]}
    security_server = {
            'ssh_user': '',
            'ssh_private_key': ''}
    assert 'admin:pass' == get_admin_credentials(security_server, config)

def test_admin_credentials_from_security_server_section_when_empty_at_root_level():
    os.environ['TOOLKIT_ADMIN_CREDENTIALS'] = 'another_admin:another_pass'
    config = {
        'admin_credentials': '',
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
              'ssh_user': 'ssh_user',
              'ssh_private_key': 'private_key'}]}
    security_server = {
            'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
            'ssh_user': '',
            'ssh_private_key': ''}
    assert 'another_admin:another_pass' == get_admin_credentials(security_server, config)

def test_ssh_values_from_root_level_when_empty_at_security_server_section():
    os.environ['TOOLKIT_SSH_USER'] = 'user'
    os.environ['TOOLKIT_SSH_PRIVATE_KEY'] = 'key'
    config = {
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'ssh_user': 'ssh_user',
              'ssh_private_key': 'private_key'}]}
    security_server = {
            'ssh_user': '',
            'ssh_private_key': ''}
    assert 'user' == get_ssh_user(security_server, config)
    assert 'key' == get_ssh_key(security_server, config)

def test_ssh_values_from_root_level_when_missing_at_security_server_section():
    os.environ['TOOLKIT_SSH_USER'] = 'user'
    os.environ['TOOLKIT_SSH_PRIVATE_KEY'] = 'key'
    config = {
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'ssh_user': 'ssh_user',
              'ssh_private_key': 'private_key'}]}
    security_server = {}
    assert 'user' == get_ssh_user(security_server, config)
    assert 'key' == get_ssh_key(security_server, config)

def test_ssh_values_from_security_server_section_when_missing_at_root_level():
    os.environ['TOOLKIT_SSH_USER'] = 'another_user'
    os.environ['TOOLKIT_SSH_PRIVATE_KEY'] = 'another_key'
    config = {
        'security_server':
            [{'ssh_user': 'ssh_user',
              'ssh_private_key': 'private_key'}]}
    security_server = {
            'ssh_user': 'TOOLKIT_SSH_USER',
            'ssh_private_key': 'TOOLKIT_SSH_PRIVATE_KEY'}
    assert 'another_user' == get_ssh_user(security_server, config)
    assert 'another_key' == get_ssh_key(security_server, config)

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


def test_http_status_code_to_text():
    assert http_status_code_to_text(None) == ''

    assert http_status_code_to_text(100) == 'CONTINUE'
    assert http_status_code_to_text(200) == 'ALL_OKAY'  # /requests/ has more than OK.
    assert http_status_code_to_text(307) == 'TEMPORARY_REDIRECT'
    assert http_status_code_to_text(400) == 'BAD_REQUEST'
    assert http_status_code_to_text(401) == 'UNAUTHORIZED'
    assert http_status_code_to_text(403) == 'FORBIDDEN'
    assert http_status_code_to_text(404) == 'NOT_FOUND'
    assert http_status_code_to_text(405) == 'METHOD_NOT_ALLOWED'
    assert http_status_code_to_text(409) == 'CONFLICT'
    assert http_status_code_to_text(429) == 'TOO_MANY_REQUESTS'
    assert http_status_code_to_text(451) == 'UNAVAILABLE_FOR_LEGAL_REASONS'
    assert http_status_code_to_text(500) == 'INTERNAL_SERVER_ERROR'
    assert http_status_code_to_text(501) == 'NOT_IMPLEMENTED'
    assert http_status_code_to_text(511) == 'NETWORK_AUTHENTICATION_REQUIRED'
