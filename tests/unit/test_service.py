from argparse import Namespace
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

    update_description_response = ServiceDescription(
        id='DEV:GOV:9876:SUB1',
        url='https://openapi3',
        type=ServiceType.OPENAPI3,
        disabled=True,
        disabled_notice='',
        refreshed_at='2021-01-01T09:10:00',
        services=[Service(id='DEV:GOV:9876:SUB1:NewPetstore',
                          full_service_code='DEV:GOV:9876:SUB1:NewPetstore',
                          service_code='NewPetstore',
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
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'logging': {'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'},
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'TOOLKIT_SS1_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'clients': [
                  {
                      'member_class': 'GOV',
                      'member_code': '9876',
                      'subsystem_code': 'SUB1',
                      'member_name': 'NIIS',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://openapi3',
                          'rest_service_code': 'RestService',
                          'type': 'OPENAPI3',
                          'access': ['DEV:security-server-owners'],
                          'url_all': False,
                          'timeout_all': 60,
                          'ssl_auth_all': False,
                          'services': [
                              {
                                  'service_code': 'Petstore',
                                  'access': ['DEV:security-server-owners'],
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
                              'access': ['DEV:security-server-owners'],
                              'url_all': False,
                              'timeout_all': 60,
                              'ssl_auth_all': False,
                              'services': [
                                  {
                                      'service_code': 'service',
                                      'access': ['DEV:security-server-owners'],
                                      'timeout': 120,
                                      'ssl_auth': True,
                                      'url': 'https://wsdl'
                                  }
                              ]
                          }
                      ]
                  }
              ]},
             {'name': 'ssY',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'TOOLKIT_SS2_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'clients': [
                  {
                      'member_class': 'GOV',
                      'member_code': '9876',
                      'subsystem_code': 'SUB1',
                      'member_name': 'GOVERMENT',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://openapi3',
                          'rest_service_code': 'RestService',
                          'type': 'OPENAPI3',
                          'access': ['DEV:security-server-owners'],
                          'url_all': False,
                          'timeout_all': 60,
                          'ssl_auth_all': False,
                          'services': [
                              {
                                  'service_code': 'Petstore',
                                  'access': ['DEV:security-server-owners'],
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
                                      'access': ['DEV:security-server-owners'],
                                      'timeout': 120,
                                      'ssl_auth': True,
                                      'url': 'https://wsdl'
                                  }
                              ]
                          }
                      ]
                  }
              ]}
             ]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_service_apply(self):
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
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                    return_value=[ServiceTestData.add_description_response]):
                        with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.enable_service_description',
                                        return_value=None):
                            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                            return_value=[ServiceClient(
                                                id='DEV:security-server-owners',
                                                name='Security server owners',
                                                local_group_code=None,
                                                service_client_type=ServiceClientType.GLOBALGROUP,
                                                rights_given_at=datetime.now().isoformat())]):
                                with mock.patch('xrdsst.api.services_api.ServicesApi.add_service_service_clients',
                                                return_value=[ServiceClient(
                                                    id='DEV:security-server-owners',
                                                    name='Security server owners',
                                                    local_group_code=None,
                                                    service_client_type=ServiceClientType.GLOBALGROUP,
                                                    rights_given_at=datetime.now().isoformat())]):
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
                                        service_controller.apply()

                                        out, err = self.capsys.readouterr()
                                        assert out.count("Added service description") > 0
                                        assert out.count("enabled successfully") > 0
                                        assert out.count("Added access rights") > 0
                                        assert out.count("Updated service parameters") > 0

                                        with self.capsys.disabled():
                                            sys.stdout.write(out)
                                            sys.stderr.write(err)

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
                    assert out.count("Added service description") > 0

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
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        with mock.patch('xrdsst.api.services_api.ServicesApi.add_service_service_clients',
                                        return_value=[ServiceClient(
                                            id='DEV:security-server-owners',
                                            name='Security server owners',
                                            local_group_code=None,
                                            service_client_type=ServiceClientType.GLOBALGROUP,
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
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
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

    def test_service_list_descriptions_render_tabulated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_descriptions()

                    assert service_controller.app._last_rendered[0][1][1] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][1][2] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][1][3] == 'https://openapi3'
                    assert service_controller.app._last_rendered[0][1][4] == 'OPENAPI3'
                    assert service_controller.app._last_rendered[0][1][5] is True
                    assert service_controller.app._last_rendered[0][1][6] == 1

    def test_service_list_descriptions_render_as_object(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_descriptions()

                    assert service_controller.app._last_rendered[0][0]["client_id"] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][0]["description_id"] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][0]["url"] == 'https://openapi3'
                    assert service_controller.app._last_rendered[0][0]["type"] == 'OPENAPI3'
                    assert service_controller.app._last_rendered[0][0]["disabled"] is True
                    assert service_controller.app._last_rendered[0][0]["services"] == 1

    def test_service_list_descriptions_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_descriptions()

                    assert service_controller.app._last_rendered is None

    def test_service_list_services_render_tabulated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_services()

                    assert service_controller.app._last_rendered[0][1][1] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][1][2] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][1][3] == 'DEV:GOV:9876:SUB1:Petstore'
                    assert service_controller.app._last_rendered[0][1][4] == 'Petstore'
                    assert service_controller.app._last_rendered[0][1][5] == 60
                    assert service_controller.app._last_rendered[0][1][6] == 'url'

    def test_service_list_services_render_as_object(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_services()

                    assert service_controller.app._last_rendered[0][0]["client_id"] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][0]["description_id"] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][0]["service_id"] == 'DEV:GOV:9876:SUB1:Petstore'
                    assert service_controller.app._last_rendered[0][0]["service_code"] == 'Petstore'
                    assert service_controller.app._last_rendered[0][0]["timeout"] == 60
                    assert service_controller.app._last_rendered[0][0]["url"] == 'url'

    def test_service_list_services_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client=None, description='DEV:GOV:9876:SUB1:Petstore')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_services()

                    assert service_controller.app._last_rendered is None

    def test_service_list_services_fail_description_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1', description=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.list_services()

                    assert service_controller.app._last_rendered is None

    def test_service_delete_descriptions(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.delete_service_description', return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.delete_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("deleted successfully") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_delete_descriptions_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client=None, description='DEV:GOV:9876:SUB1:Petstore')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.delete_service_description', return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.delete_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("deleted successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_delete_descriptions_fail_description_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.delete_service_description', return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.delete_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("deleted successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_update_descriptions(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1', code='NewPetstore', url=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.update_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.update_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("updated successfully") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_update_descriptions_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client=None, description='DEV:GOV:9876:SUB1', code='NewPetstore', url=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.update_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.update_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("updated successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_update_descriptions_fail_description_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description=None, code='NewPetstore', url=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.update_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.update_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("updated successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_update_descriptions_fail_url_and_code_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1', code=None, url=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.update_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.update_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("updated successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_refresh_descriptions(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.refresh_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.refresh_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("refreshed successfully") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_refresh_descriptions_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client=None, description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.refresh_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.refresh_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("refreshed successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_refresh_descriptions_fail_description_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.refresh_service_description',
                                return_value=[ServiceTestData.update_description_response]):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.refresh_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("refreshed successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_disable_descriptions(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1', notice='disabled')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.disable_service_description',
                                return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.disable_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("disabled successfully") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_disable_descriptions_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client=None, description='DEV:GOV:9876:SUB1', notice='disabled')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.disable_service_description',
                                return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.disable_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("disabled successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_disable_descriptions_fail_description_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description=None, notice='disabled')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.disable_service_description',
                                return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.disable_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("disabled successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_disable_descriptions_fail_notice_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1', notice=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                            return_value=[ServiceTestData.add_description_response]):
                with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.disable_service_description',
                                return_value=None):
                    service_controller = ServiceController()
                    service_controller.app = app
                    service_controller.load_config = (lambda: self.ss_config)
                    service_controller.disable_descriptions()

                    out, err = self.capsys.readouterr()
                    assert out.count("disabled successfully") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_service_list_access_render_tabulated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.list_access()

                        assert service_controller.app._last_rendered[0][1][1] == 'DEV:GOV:9876:SUB1'
                        assert service_controller.app._last_rendered[0][1][2] == 'DEV:GOV:9876:SUB1'
                        assert service_controller.app._last_rendered[0][1][3] == 'DEV:GOV:9876:SUB1:Petstore'
                        assert service_controller.app._last_rendered[0][1][4] == 'DEV:security-server-owners'
                        assert service_controller.app._last_rendered[0][1][5] is None
                        assert service_controller.app._last_rendered[0][1][6] == 'Security server owners'
                        assert service_controller.app._last_rendered[0][1][7] is not None
                        assert service_controller.app._last_rendered[0][1][8] == ServiceClientType.GLOBALGROUP

    def test_service_list_access_render_as_object(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1', description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.list_access()

                    assert service_controller.app._last_rendered[0][0]["client_id"] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][0]["description_id"] == 'DEV:GOV:9876:SUB1'
                    assert service_controller.app._last_rendered[0][0]["service_id"] == 'DEV:GOV:9876:SUB1:Petstore'
                    assert service_controller.app._last_rendered[0][0]["service_client_id"] == 'DEV:security-server-owners'
                    assert service_controller.app._last_rendered[0][0]["local_group"] is None
                    assert service_controller.app._last_rendered[0][0]["name"] == 'Security server owners'
                    assert service_controller.app._last_rendered[0][0]["rights_given"] is not None
                    assert service_controller.app._last_rendered[0][0]["type"] == ServiceClientType.GLOBALGROUP

    def test_service_list_access_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client=None, description='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.list_access()

                        assert service_controller.app._last_rendered is None

    def test_service_list_access_fail_description_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(client='DEV:GOV:9876:SUB1', description=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[ServiceTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        service_controller = ServiceController()
                        service_controller.app = app
                        service_controller.load_config = (lambda: self.ss_config)
                        service_controller.list_access()

                        assert service_controller.app._last_rendered is None
