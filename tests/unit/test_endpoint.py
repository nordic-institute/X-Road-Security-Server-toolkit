from datetime import datetime
import sys
import unittest
from unittest import mock

import pytest

from tests.util.test_util import StatusTestData
from xrdsst.controllers.endpoint import EndpointController
from xrdsst.models import Client, ConnectionType, ClientStatus, ServiceDescription, ServiceType, ServiceClient, ServiceClientType, Service
from xrdsst.main import XRDSSTTest
from xrdsst.rest.rest import ApiException

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
                          endpoints=[])],
        client_id='DEV:GOV:9876:SUB1'
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
                              'method': 'POST'
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
                            return_value=None):
                        endpoint_controller = EndpointController()
                        endpoint_controller.app = app
                        endpoint_controller.load_config = (lambda: self.ss_config)
                        endpoint_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        endpoint_controller.add_endpoints()

                        out, err = self.capsys.readouterr()
                        assert out.count("Added service endpoint") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)
