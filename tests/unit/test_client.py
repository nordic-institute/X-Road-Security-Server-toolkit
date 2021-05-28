import sys
import unittest
import copy
from unittest import mock

import pytest
from urllib3._collections import HTTPHeaderDict

from tests.util.test_util import StatusTestData
from xrdsst.controllers.client import ClientController
from xrdsst.models import Client, ConnectionType, ClientStatus
from xrdsst.main import XRDSSTTest
from xrdsst.resources.texts import server_error_map, ascii_art
from xrdsst.rest.rest import ApiException


class ClientTestData:
    add_response = Client(
        id='DEV:GOV:9876:SUB1',
        connection_type=ConnectionType.HTTP,
        has_valid_local_sign_cert=True,
        instance_id='DEV',
        member_class='GOV',
        member_code='9876',
        subsystem_code='SUB1',
        member_name='TEST',
        owner=False,
        status=ClientStatus.SAVED
    )

    update_response = Client(
        id='DEV:GOV:9876:SUB1',
        connection_type=ConnectionType.HTTPS,
        has_valid_local_sign_cert=True,
        instance_id='DEV',
        member_class='GOV',
        member_code='9876',
        subsystem_code='SUB1',
        member_name='MAME',
        owner=False,
        status=ClientStatus.REGISTERED
    )


class TestClient(unittest.TestCase):
    ss_config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'logging': {'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'},
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'TOOLKIT_SS1_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_member_class': 'GOV',
              'owner_member_code': '9876',
              'clients': [
                  {
                      'member_class': 'GOV',
                      'member_code': '9876',
                      'member_name': 'TEST',
                      'subsystem_code': 'SUB1',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://openapi3',
                          'rest_service_code': 'RestService',
                          'type': 'OPENAPI3'
                      },
                          {
                              'url': 'https://wsdl',
                              'rest_service_code': '',
                              'type': 'WSDL'
                          }
                      ]
                  }
              ]},
             {'name': 'ssY',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'TOOLKIT_SS2_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'owner_member_class': 'GOV',
              'owner_member_code': '9876',
              'clients': [
                  {
                      'member_class': 'GOV',
                      'member_code': '9876',
                      'member_name': 'TEST',
                      'subsystem_code': 'SUB1',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://openapi3',
                          'rest_service_code': 'RestService',
                          'type': 'OPENAPI3'
                      },
                          {
                              'url': 'https://wsdl',
                              'rest_service_code': '',
                              'type': 'WSDL'
                          }
                      ]
                  }
              ]}
             ]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_subsystem_add(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client',
                            return_value=ClientTestData.add_response):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                client_controller.add()

                out, err = self.capsys.readouterr()
                assert out.count("Added client") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_add_already_existing(self):
        class AlreadyExistingResponse:
            status = 409
            data = '{"status":409,"error":{"code":"certificate_already_exists"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client',
                            side_effect=ApiException(http_resp=AlreadyExistingResponse())):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                client_controller.add()

                out, err = self.capsys.readouterr()
                assert out.count("already exists") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_register_not_found(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[]):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                client_controller.register()

                out, err = self.capsys.readouterr()
                assert out.count("not found") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_register_found(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_class='GOV',
                    member_code='9876',
                    member_name='TEST',
                    subsystem_code='SUB1',
                    connection_type=ConnectionType.HTTP,
                    status=ClientStatus.SAVED,
                    owner=True,
                    has_valid_local_sign_cert=True
            )]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.register_client', return_value=None):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config)
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.register()

                    out, err = self.capsys.readouterr()
                    assert out.count("Registered client") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_client_register_already_registered(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_class='GOV',
                    member_code='9876',
                    member_name='TEST',
                    subsystem_code='SUB1',
                    connection_type=ConnectionType.HTTP,
                    status=ClientStatus.REGISTERED,
                    owner=True,
                    has_valid_local_sign_cert=True
            )]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.register_client', return_value=None):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config)
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.register()

                    out, err = self.capsys.readouterr()
                    assert out.count("already registered") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    @mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', lambda x, **kx: [ClientTestData.add_response])
    def test_registration_disabled_at_management_services_provider(self):
        class ServerProxyHasServiceDisabledResponse:
            status = 500
            data = '{"status":500,"error":{"code":"core.Server.ServerProxy.ServiceDisabled","metadata":["Service SERVICE:DEV/GOV/9876/MANAGEMENT/clientReg is disabled: BOFH"]}}'
            reason = ''

            def getheaders(self):
                headers = HTTPHeaderDict()
                headers.add('x-road-ui-correlation-id', 'ddddaaaa0011ffff')
                headers.add('Content-Type', 'application/json')

                return headers

            @staticmethod
            def as_extended_exception():
                api_ex = ApiException(http_resp=ServerProxyHasServiceDisabledResponse())
                api_ex.api_call = {
                    'method': 'PUT',
                    'resource_path': '/clients/{id}/register',
                    'path_params': 'GOV:9876:SUB1',
                    'query_params': '',
                    'header_params': '',
                    'controller_func': 'client.py#remote_register_client',
                    'module_func': 'clients_api.py#register_client'
                }

                return api_ex

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.register_client',
                            side_effect=ServerProxyHasServiceDisabledResponse.as_extended_exception()):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                client_controller.register()

                out, err = self.capsys.readouterr()
                assert err.count("FAILED") > 0
                assert err.count("PUT /clients/{id}/register @ clients_api.py#register_client <- client.py#remote_register_client") == 2
                assert err.count("INTERNAL_SERVER_ERROR (500)") == 2
                assert err.count("error_code 'core.Server.ServerProxy.ServiceDisabled'") == 2
                assert err.count("Service SERVICE:DEV/GOV/9876/MANAGEMENT/clientReg is disabled: BOFH") == 2
                assert err.count(server_error_map.get('core.Server.ServerProxy.ServiceDisabled')) == 2

                assert err.count(ascii_art['message_flow'][2]) == 2
                assert err.count(ascii_art['message_flow'][3]) == 2
                assert err.count(ascii_art['message_flow'][4]) == 2

    def test_client_add_new_member(self):
        with XRDSSTTest() as app:
            new_config = copy.deepcopy(self.ss_config)
            new_config["security_server"][0]["clients"].append(
                  {
                      'member_class': 'NEW_GOV',
                      'member_code': '1111',
                      'member_name': 'NEW_TEST',
                      'connection_type': 'HTTPS'
                  })

            with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client',
                            return_value=ClientTestData.add_response):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: new_config)
                client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                client_controller.add()

                out, err = self.capsys.readouterr()
                assert out.count("Added client") > 0
                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_subsystem_update(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_class='GOV',
                    member_code='9876',
                    subsystem_code='SUB1',
                    connection_type=ConnectionType.HTTP,
                    status=ClientStatus.REGISTERED,
                    owner=True,
                    has_valid_local_sign_cert=True
            )]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.update_client', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_class='GOV',
                    member_code='9876',
                    subsystem_code='SUB1',
                    connection_type=ConnectionType.HTTPS,
                    status=ClientStatus.REGISTERED,
                    owner=True,
                    has_valid_local_sign_cert=True
                )]):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config)
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.update()

                    out, err = self.capsys.readouterr()
                    assert out.count("Updated client") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)
