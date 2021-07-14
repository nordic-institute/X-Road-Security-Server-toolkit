from argparse import Namespace
from datetime import datetime
import sys
import unittest
from unittest import mock
import pytest
from tests.util.test_util import StatusTestData
from xrdsst.controllers.local_group import LocalGroupController
from xrdsst.models import Client, ConnectionType, ClientStatus, LocalGroup, GroupMember
from xrdsst.main import XRDSSTTest
from xrdsst.rest.rest import ApiException
from datetime import date

class ClientTestData:
    find_client_response = Client(
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

    find_client_member_not_found = Client(
        id='DEV:COM:12345:COMPANY',
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

    client_local_group_response_not_found = LocalGroup(
        id=185,
        code="Test",
        description="test_description",
        member_count=1,
        members=[
            GroupMember(
                id='DEV:GOV:9876:SUB1',
                name='NIIS',
                created_at=date.today()
            )]
    )
    client_local_group_response = LocalGroup(
        id=185,
        code="testGroup",
        description="test group description",
        member_count=1,
        members=[
            GroupMember(
                id='DEV:ORG:111:TEST',
                name='NIIS',
                created_at=date.today()
            )]
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
                      'local_groups': [{
                          'code': 'testGroup',
                          'description': 'test group description',
                          'members': ['DEV:GOV:9876:SUB1']
                      }],
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
                      'local_groups': [{
                          'code': 'testGroup',
                          'description': 'test group description',
                          'members': ['DEV:GOV:9876:SUB1']
                      }],
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

    def test_localgroup_add(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                            return_value=[ClientTestData.find_client_response]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_local_group',
                                return_value={}):

                    local_group_controller = LocalGroupController()
                    local_group_controller.app = app
                    local_group_controller.load_config = (lambda: self.ss_config)
                    local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    local_group_controller.add()

                    out, err = self.capsys.readouterr()
                    assert out.count("Added local group") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)
    def test_localgroup_add_already_added(self):
        class AlreadyExistingResponse:
            status = 409
            data = '{"status":409,"error":{"code":"local_group_already_exists"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                            return_value=[ClientTestData.find_client_response]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_local_group',
                                side_effect=ApiException(http_resp=AlreadyExistingResponse())):

                    local_group_controller = LocalGroupController()
                    local_group_controller.app = app
                    local_group_controller.load_config = (lambda: self.ss_config)
                    local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    local_group_controller.add()

                    out, err = self.capsys.readouterr()
                    assert out.count("already added") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_localgroup_add_members(self):
        with XRDSSTTest() as app:

            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_local_groups',
                            return_value=[ClientTestData.client_local_group_response]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                                return_value=[ClientTestData.find_client_response]):
                    with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.add_local_group_member',
                                    return_value={}):

                        local_group_controller = LocalGroupController()
                        local_group_controller.app = app
                        local_group_controller.load_config = (lambda: self.ss_config)
                        local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        local_group_controller.add_members()

                        out, err = self.capsys.readouterr()
                        assert out.count("Added member(s)") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_localgroup_add_members_already_added(self):
        class AlreadyExistingResponse:
            status = 409
            data = '{"status":409,"error":{"code":"local_group_member_already_exists"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:

            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_local_groups',
                            return_value=[ClientTestData.client_local_group_response]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                                return_value=[ClientTestData.find_client_response]):
                    with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.add_local_group_member',
                                side_effect=ApiException(http_resp=AlreadyExistingResponse())):

                        local_group_controller = LocalGroupController()
                        local_group_controller.app = app
                        local_group_controller.load_config = (lambda: self.ss_config)
                        local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        local_group_controller.add_members()

                        out, err = self.capsys.readouterr()
                        assert out.count(", already added") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_localgroup_add_members_local_group_not_found(self):
        with XRDSSTTest() as app:

            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_local_groups',
                            return_value=[ClientTestData.client_local_group_response_not_found]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                                return_value=[ClientTestData.find_client_response]):
                    with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.add_local_group_member',
                                    return_value={}):

                        local_group_controller = LocalGroupController()
                        local_group_controller.app = app
                        local_group_controller.load_config = (lambda: self.ss_config)
                        local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        local_group_controller.add_members()

                        out, err = self.capsys.readouterr()
                        assert out.count("local group not found") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_localgroup_add_members_member_not_found(self):
        with XRDSSTTest() as app:

            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_local_groups',
                            return_value=[ClientTestData.client_local_group_response]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                                return_value=[ClientTestData.client_local_group_response_not_found]):
                    with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.add_local_group_member',
                                    return_value={}):

                        local_group_controller = LocalGroupController()
                        local_group_controller.app = app
                        local_group_controller.load_config = (lambda: self.ss_config)
                        local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        local_group_controller.add_members()

                        out, err = self.capsys.readouterr()
                        assert out.count(", member not found") > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_localgroup_list(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client_local_groups',
                            return_value=[ClientTestData.client_local_group_response]):

                local_group_controller = LocalGroupController()
                local_group_controller.app = app
                local_group_controller.load_config = (lambda: self.ss_config)
                local_group_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                local_group_controller.list()

                assert local_group_controller.app._last_rendered[0][0] == ['ID','CODE','DESCRIPTION','MEMBERS']
                assert local_group_controller.app._last_rendered[0][1] == [185,'testGroup','test group description',['DEV:ORG:111:TEST']]


    def test_local_group_delete(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', local_group='185')
            with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.delete_local_group',
                            return_value={}):
                local_group_controller = LocalGroupController()
                local_group_controller.app = app
                local_group_controller.load_config = (lambda: self.ss_config)
                local_group_controller.get_server_status = (
                    lambda x, y: StatusTestData.server_status_essentials_complete)
                local_group_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count("Deleted local group ") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_local_group_delete_member(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', local_group='185', member='DEV:ORG:111:TEST')
            with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.get_local_group',
                            return_value=ClientTestData.client_local_group_response):
                with mock.patch('xrdsst.api.local_groups_api.LocalGroupsApi.delete_local_group_member',
                                return_value={}):
                    local_group_controller = LocalGroupController()
                    local_group_controller.app = app
                    local_group_controller.load_config = (lambda: self.ss_config)
                    local_group_controller.get_server_status = (
                        lambda x, y: StatusTestData.server_status_essentials_complete)
                    local_group_controller.delete_member()

                    out, err = self.capsys.readouterr()
                    assert out.count("Deleted local group member(s)") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)