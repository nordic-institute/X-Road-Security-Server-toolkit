import sys
import unittest
from unittest import mock

import pytest

from xrdsst.controllers.service import ServiceController
from xrdsst.models import Client, ConnectionType, ClientStatus, ServiceDescription, ServiceType
from xrdsst.main import XRDSSTTest
from xrdsst.rest.rest import ApiException


class ServiceTestData:
    add_description_response = ServiceDescription(
        id='DEV:GOV:9876:SUB1',
        url='https://openapi3',
        type=ServiceType.OPENAPI3,
        disabled=True,
        disabled_notice='',
        refreshed_at='2021-01-01T09:10:00',
        services=[],
        client_id='DEV:GOV:9876:SUB1'
    )


class TestService(unittest.TestCase):
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

    def test_service_description_add(self):
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
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_service_description',
                                return_value=ServiceTestData.add_description_response):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.add_description()

                    out, err = self.capsys.readouterr()
                    assert out.count("Added service description with type") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_description_add_client_not_found(self):
        class ClientNotFound:
            status = 404
            data = '{"status":404,"error":{"code":"service_description_client_not_foubd"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                            side_effect=ApiException(http_resp=ClientNotFound())):
                service_controller = ServiceController()
                service_controller.app = app
                service_controller.load_config = (lambda: self.ss_config)
                service_controller.add_description()

                out, err = self.capsys.readouterr()
                assert out.count("ClientsApi->find_clients") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_service_description_add_already_existing(self):
        class AlreadyExistingResponse:
            status = 409
            data = '{"status":409,"error":{"code":"service_description_already_exists"}}'
            reason = None

            def getheaders(self): return None

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
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_service_description',
                                side_effect=ApiException(http_resp=AlreadyExistingResponse())):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.add_description()

                    out, err = self.capsys.readouterr()
                    assert out.count("already exists") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_description_add_other_exception(self):
        class PermissionDeniedResponse:
            status = 403
            data = '{"status":409,"error":{"code":"service_description_permission_denied"}}'
            reason = None

            def getheaders(self): return None

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
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_service_description',
                                side_effect=ApiException(http_resp=PermissionDeniedResponse())):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.add_description()

                    out, err = self.capsys.readouterr()
                    assert out.count("ClientsApi->add_client_service_description") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_description_enable(self):
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
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.enable_service_description',
                                    return_value=None):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.enable_description()

                        out, err = self.capsys.readouterr()
                        assert out.count("enabled successfully") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_service_description_enable_already_enabled(self):
        class AlreadyEnabledResponse:
            status = 409
            data = '{"status":409,"error":{"code":"service_description_already_enabled"}}'
            reason = None

            def getheaders(self): return None

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
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.enable_service_description',
                                    side_effect=ApiException(http_resp=AlreadyEnabledResponse())):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.enable_description()

                        out, err = self.capsys.readouterr()
                        assert out.count("already enabled") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)
