from datetime import datetime
import sys
import unittest
from unittest import mock

import pytest

from tests.util.test_util import StatusTestData
from xrdsst.controllers.service import ServiceController
from xrdsst.models import Client, ConnectionType, ClientStatus, ServiceDescription, ServiceType, ServiceClient, ServiceClientType, Service
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
        services=[Service(id='DEV:GOV:9876:SUB1:Petstore',
                          full_service_code='DEV:GOV:9876:SUB1:Petstore',
                          service_code='Petstore',
                          timeout=60,
                          title='title',
                          ssl_auth=False,
                          subjects_count=0,
                          url='url',
                          endpoints=[])],
        client_id='DEV:GOV:9876:SUB1'
    )


class TestService(unittest.TestCase):
    ss_config = {
        'admin_credentials': 'user:pass',
        'logging': {'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'},
        'ssh_access': {'user': 'user', 'private_key': 'key'},
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': '33333333-3000-4000-b000-939393939393',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'clients': [
                  {
                      'member_class': 'GOV',
                      'member_code': '9876',
                      'subsystem_code': 'SUB1',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://openapi3',
                          'rest_service_code': 'RestService',
                          'type': 'OPENAPI3',
                          'access': ['SUB1'],
                          'url_all': False,
                          'timeout_all': 60,
                          'ssl_auth_all': False,
                          'services': [
                              {
                                  'service_code': 'Petstore',
                                  'access': ['SUB1'],
                                  'timeout': 120,
                                  'ssl_auth': True,
                                  'url': 'http://petstore.swagger.io/v1'
                              }
                          ]
                      },
                          {
                              'url': 'https://wsdl',
                              'rest_service_code': '',
                              'type': 'WSDL',
                              'access': ['SUB1'],
                              'url_all': False,
                              'timeout_all': 60,
                              'ssl_auth_all': False,
                              'services': [
                                  {
                                      'service_code': 'service',
                                      'access': ['SUB1'],
                                      'timeout': 120,
                                      'ssl_auth': True,
                                      'url': 'https://wsdl'
                                  }
                              ]
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
                    service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    service_controller.add_description()

                    out, err = self.capsys.readouterr()
                    assert out.count("Added service description with type") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_description_add_client_not_found(self):
        class ClientNotFound:
            status = 404
            data = '{"status":404,"error":{"code":"service_description_client_not_found"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                            side_effect=ApiException(http_resp=ClientNotFound())):
                service_controller = ServiceController()
                service_controller.app = app
                service_controller.load_config = (lambda: self.ss_config)
                service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                service_controller.add_description()

                out, err = self.capsys.readouterr()
                assert err.count("service_description_client_not_found") > 0

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
                    service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    service_controller.add_description()

                    out, err = self.capsys.readouterr()
                    assert out.count("already exists") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_description_add_other_exception(self):
        class PermissionDeniedResponse:
            status = 403
            data = '{"status":403,"error":{"code":"service_description_permission_denied"}}'
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
                    service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    service_controller.add_description()

                    out, err = self.capsys.readouterr()
                    assert err.count("service_description_permission_denied") > 0

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
                        service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
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
                        service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        service_controller.enable_description()

                        out, err = self.capsys.readouterr()
                        assert out.count("already enabled") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_service_add_access(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_name='ACME',
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
                    with mock.patch('xrdsst.api.services_api.ServicesApi.add_service_service_clients',
                                    return_value=[ServiceClient(
                                        id='DEV:GOV:9876:SUB1',
                                        name='ACME',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.SUBSYSTEM,
                                        rights_given_at=datetime.now().isoformat())]):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        service_controller.add_access()

                        out, err = self.capsys.readouterr()
                        assert out.count("Added access rights") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_service_add_access_already_added(self):
        class AlreadyAddedResponse:
            status = 409
            data = '{"status":409,"error":{"code":"duplicate_accessright"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_name='ACME',
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
                    with mock.patch('xrdsst.api.services_api.ServicesApi.add_service_service_clients',
                                    side_effect=ApiException(http_resp=AlreadyAddedResponse())):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        service_controller.add_access()

                        out, err = self.capsys.readouterr()
                        assert out.count("already added") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_service_update_parameters(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_name='ACME',
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
                    with mock.patch('xrdsst.api.services_api.ServicesApi.update_service',
                                    return_value=Service(
                                        id='DEV:GOV:9876:SUB1:Petstore',
                                        full_service_code='DEV:GOV:9876:SUB1:Petstore',
                                        service_code='Petstore',
                                        timeout=120,
                                        title='title',
                                        ssl_auth=False,
                                        subjects_count=0,
                                        url='url',
                                        endpoints=[])):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        service_controller.update_parameters()

                        out, err = self.capsys.readouterr()
                        assert out.count("Updated service parameters") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)
