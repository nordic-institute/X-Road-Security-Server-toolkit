from datetime import datetime
import sys
import unittest
from unittest import mock
import copy
import pytest
from argparse import Namespace

from tests.util.test_util import StatusTestData
from xrdsst.controllers.endpoint import EndpointController, EndpointListMapper, EndpointAccessListMapper
from xrdsst.models import Client, ConnectionType, ClientStatus, ServiceDescription, ServiceType, ServiceClient, ServiceClientType, Service, Endpoint
from xrdsst.main import XRDSSTTest
from xrdsst.rest.rest import ApiException
from datetime import date

class EndpointTestData:
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
                          endpoints=[Endpoint(id="1", service_code='Petstore', path='/testPath', method='POST')])],
        client_id='DEV:GOV:9876:SUB1'
    )

    add_access_response = [ServiceClient(id='DEV:security-server-owners',
                                         name='Security server owners',
                                         local_group_code=None,
                                         service_client_type='GLOBALGROUP',
                                         rights_given_at=None)]
    get_endpoint = Endpoint(
                    id='1',
                    service_code="Test",
                    method="PUT",
                    path="/testPath",
                    generated=False
            )



class TestEndpoint(unittest.TestCase):
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
                      'member_name': 'NIIS',
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
                          ],
                          'endpoints': [{
                              'path': '/testPath',
                              'method': 'POST',
                              'access': ['DEV:security-server-owners']
                          }]
                      }]
                  }
              ]}]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_endpoint_add(self):
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
                                return_value=[EndpointTestData.add_description_response]):
                    with mock.patch(
                            'xrdsst.api.services_api.ServicesApi.add_endpoint',
                            return_value=EndpointTestData.add_description_response):
                        endpoint_controller = EndpointController()
                        endpoint_controller.app = app
                        endpoint_controller.load_config = (lambda: self.ss_config)
                        endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        endpoint_controller.add()

                        out, err = self.capsys.readouterr()
                        assert out.count("Added service endpoint") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_endpoint_already_added(self):
        class AlreadyEnabledResponse:
            status = 409
            data = '{"status":409,"error":{"code":"service_endpoint_already_enabled"}}'
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
                                return_value=[EndpointTestData.add_description_response]):
                    with mock.patch(
                            'xrdsst.api.services_api.ServicesApi.add_endpoint',
                            side_effect=ApiException(http_resp=AlreadyEnabledResponse())):
                        endpoint_controller = EndpointController()
                        endpoint_controller.app = app
                        endpoint_controller.load_config = (lambda: self.ss_config)
                        endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        endpoint_controller.add()

                        out, err = self.capsys.readouterr()
                        assert out.count("already added") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_endpoint_add_access(self):
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
                                return_value=[EndpointTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        with mock.patch(
                                'xrdsst.api.endpoints_api.EndpointsApi.add_endpoint_service_clients',
                                return_value=EndpointTestData.add_access_response):

                            endpoint_controller = EndpointController()
                            endpoint_controller.app = app
                            endpoint_controller.load_config = (lambda: self.ss_config)
                            endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                            endpoint_controller.add_access()

                            out, err = self.capsys.readouterr()
                            assert out.count("Added client access rights") > 0

                            with self.capsys.disabled():
                                sys.stdout.write(out)
                                sys.stderr.write(err)

    def test_endpoint_add_access_not_valid_candidate(self):
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
                                return_value=[EndpointTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[]):
                        with mock.patch(
                                'xrdsst.api.endpoints_api.EndpointsApi.add_endpoint_service_clients',
                                return_value=EndpointTestData.add_access_response):

                            endpoint_controller = EndpointController()
                            endpoint_controller.app = app
                            endpoint_controller.load_config = (lambda: self.ss_config)
                            endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                            endpoint_controller.add_access()

                            out, err = self.capsys.readouterr()
                            assert out.count("no valid candidate found") > 0

                            with self.capsys.disabled():
                                sys.stdout.write(out)
                                sys.stderr.write(err)


    def test_endpoint_add_access_endpoint_not_found(self):
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

                service_description = copy.deepcopy(EndpointTestData.add_description_response)
                service_description.services[0].endpoints[0].method = 'GET'
                with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_service_descriptions',
                                return_value=[service_description]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        with mock.patch(
                                'xrdsst.api.endpoints_api.EndpointsApi.add_endpoint_service_clients',
                                return_value=EndpointTestData.add_access_response):

                            endpoint_controller = EndpointController()
                            endpoint_controller.app = app
                            endpoint_controller.load_config = (lambda: self.ss_config)
                            endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                            endpoint_controller.add_access()

                            out, err = self.capsys.readouterr()
                            assert out.count("endpoint not found") > 0

                            with self.capsys.disabled():
                                sys.stdout.write(out)
                                sys.stderr.write(err)

    def test_endpoint_add_access_already_added(self):
        class AlreadyEnabledResponse:
            status = 409
            data = '{"status":409,"error":{"code":"service_endpoint_already_enabled"}}'
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
                                return_value=[EndpointTestData.add_description_response]):
                    with mock.patch('xrdsst.api.clients_api.ClientsApi.find_service_client_candidates',
                                    return_value=[ServiceClient(
                                        id='DEV:security-server-owners',
                                        name='Security server owners',
                                        local_group_code=None,
                                        service_client_type=ServiceClientType.GLOBALGROUP,
                                        rights_given_at=datetime.now().isoformat())]):
                        with mock.patch(
                                'xrdsst.api.endpoints_api.EndpointsApi.add_endpoint_service_clients',
                                side_effect=ApiException(http_resp=AlreadyEnabledResponse())):

                            endpoint_controller = EndpointController()
                            endpoint_controller.app = app
                            endpoint_controller.load_config = (lambda: self.ss_config)
                            endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                            endpoint_controller.add_access()

                            out, err = self.capsys.readouterr()
                            assert out.count("already added") > 0

                            with self.capsys.disabled():
                                sys.stdout.write(out)
                                sys.stderr.write(err)

    def test_endpoint_list(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', description='1')
            with mock.patch('xrdsst.api.service_descriptions_api.ServiceDescriptionsApi.get_service_description',
                            return_value=EndpointTestData.add_description_response):
                endpoint_controller = EndpointController()
                endpoint_controller.app = app
                endpoint_controller.load_config = (lambda: self.ss_config)
                endpoint_controller.list()

            for header in EndpointListMapper.headers():
                assert header in endpoint_controller.app._last_rendered[0][0]

            assert endpoint_controller.app._last_rendered[0][1][0] == '1'
            assert endpoint_controller.app._last_rendered[0][1][1] == 'POST'
            assert endpoint_controller.app._last_rendered[0][1][2] == '/testPath'
            assert endpoint_controller.app._last_rendered[0][1][3] == 'Petstore'
            assert endpoint_controller.app._last_rendered[0][1][4] == 'DEV:GOV:9876:SUB1'
            assert endpoint_controller.app._last_rendered[0][1][5] == 'https://openapi3'
            assert endpoint_controller.app._last_rendered[0][1][6] == ServiceType.OPENAPI3


    def test_endpoint_update(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX',
                                         endpoint='1',
                                         method='POST',
                                         path='/testPath')

            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', return_value=EndpointTestData.get_endpoint):

                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.update_endpoint',
                                return_value={}):

                    endpoint_controller = EndpointController()
                    endpoint_controller.app = app
                    endpoint_controller.load_config = (lambda: self.ss_config)
                    endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    endpoint_controller.update()

                    out, err = self.capsys.readouterr()
                    assert out.count("Updated endpoint ") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_endpoint_update_endpoint_not_found(self):
        class NotFoundResponse:
            status = 404
            data = '{"status":404}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX',
                                         endpoint='1',
                                         method='POST',
                                         path='/testPath')

            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', side_effect=ApiException(http_resp=NotFoundResponse())):
                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.update_endpoint',
                                return_value={}):
                    endpoint_controller = EndpointController()
                    endpoint_controller.app = app
                    endpoint_controller.load_config = (lambda: self.ss_config)
                    endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    endpoint_controller.update()

                    out, err = self.capsys.readouterr()
                    assert out.count("Could not find an endpoint with id: '1' for security server: 'ssX'") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_endpoint_is_generated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX',
                                         endpoint='1',
                                         method='POST',
                                         path='/testPath')

            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', return_value=Endpoint(
                id=1,
                service_code="Test",
                method="PUT",
                path="/testPath",
                generated=True
            )):

                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.update_endpoint',
                                return_value={}):

                    endpoint_controller = EndpointController()
                    endpoint_controller.app = app
                    endpoint_controller.load_config = (lambda: self.ss_config)
                    endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    endpoint_controller.update()

                    out, err = self.capsys.readouterr()
                    assert out.count("could not update generated endpoints") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_endpoint_delete(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX',
                                         endpoint='1')

            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', return_value=EndpointTestData.get_endpoint):

                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.delete_endpoint',
                                return_value={}):

                    endpoint_controller = EndpointController()
                    endpoint_controller.app = app
                    endpoint_controller.load_config = (lambda: self.ss_config)
                    endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    endpoint_controller.delete()

                    out, err = self.capsys.readouterr()
                    assert out.count("Deleted endpoint with id") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_endpoint_update_endpoint_not_found(self):
        class NotFoundResponse:
            status = 404
            data = '{"status":404}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX',
                                         endpoint='1')

            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', side_effect=ApiException(http_resp=NotFoundResponse())):
                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.delete_endpoint',
                                return_value={}):
                    endpoint_controller = EndpointController()
                    endpoint_controller.app = app
                    endpoint_controller.load_config = (lambda: self.ss_config)
                    endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    endpoint_controller.delete()

                    out, err = self.capsys.readouterr()
                    assert out.count("Could not find an endpoint with id: '1' for security server: 'ssX'") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_endpoint_list_access(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', endpoint='1')
            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', return_value=EndpointTestData.get_endpoint):
                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint_service_clients',
                                return_value=EndpointTestData.add_access_response):
                    endpoint_controller = EndpointController()
                    endpoint_controller.app = app
                    endpoint_controller.load_config = (lambda: self.ss_config)
                    endpoint_controller.list_access()

            for header in EndpointAccessListMapper.headers():
                assert header in endpoint_controller.app._last_rendered[0][0]

            assert endpoint_controller.app._last_rendered[0][1][0] == '1'
            assert endpoint_controller.app._last_rendered[0][1][1] == 'PUT /testPath'
            assert endpoint_controller.app._last_rendered[0][1][2] == 'Test'
            assert endpoint_controller.app._last_rendered[0][1][3] == 'DEV:security-server-owners'

    def test_endpoint_delete_access(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', endpoint='1', access='DEV:security-server-owners')
            with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint', return_value=EndpointTestData.get_endpoint):
                with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.get_endpoint_service_clients',
                                return_value=EndpointTestData.add_access_response):
                    with mock.patch('xrdsst.api.endpoints_api.EndpointsApi.delete_endpoint_service_clients',
                                    return_value={}):

                        endpoint_controller = EndpointController()
                        endpoint_controller.app = app
                        endpoint_controller.load_config = (lambda: self.ss_config)
                        endpoint_controller.delete_access()

                        out, err = self.capsys.readouterr()
                        assert out.count("Deleted access rights: '['DEV:security-server-owners']', endpoint id: '1', security server: 'ssX'") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)
