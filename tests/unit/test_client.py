import sys
import unittest
from unittest import mock

import pytest

from xrdsst.controllers.client import ClientController
from xrdsst.models import Client, ConnectionType, ClientStatus
from xrdsst.main import XRDSSTTest
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
        member_name='MAME',
        owner=False,
        status=ClientStatus.SAVED
    )


class TestClient(unittest.TestCase):
    ss_config = {
        'logging': [{'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'}],
        'api_key': [{'url': 'https://localhost:4000/api/v1/api-keys',
                     'key': 'private key',
                     'credentials': 'user:pass',
                     'roles': 'XROAD_SYSTEM_ADMINISTRATOR'}],
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'clients': [
                  {
                      'member_class': 'GOV',
                      'member_code': '9876',
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
              ]}]}

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
                    client_controller.register()

                    out, err = self.capsys.readouterr()
                    assert out.count("already registered") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)
