import sys
import unittest
import copy
from unittest import mock
import os
from xrdsst.core.definitions import ROOT_DIR
import pytest
from urllib3._collections import HTTPHeaderDict

from tests.util.test_util import StatusTestData
from xrdsst.controllers.client import ClientController, ClientsListMapper
from xrdsst.models import Client, ConnectionType, ClientStatus
from xrdsst.main import XRDSSTTest
from xrdsst.resources.texts import server_error_map, ascii_art
from xrdsst.rest.rest import ApiException
from argparse import Namespace


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

    make_owner_response = Client(
        id='DEV:GOV:9876:SUB1',
        connection_type=ConnectionType.HTTP,
        has_valid_local_sign_cert=True,
        instance_id='DEV',
        member_class='GOV',
        member_code='9876',
        member_name='TEST',
        owner=False,
        status=ClientStatus.SAVED
    )


class TestClient(unittest.TestCase):
    tls_cert_existing = os.path.join(ROOT_DIR, "tests/resources/cert.pem")
    tls_cert_non_existing = os.path.join(ROOT_DIR, "tests/resources/111cert.pem")
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
              'owner_dn_org': 'NIIS',
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
              'owner_dn_org': 'NIIS',
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

    def ss_config_with_tls_cert(self):
        config = copy.deepcopy(self.ss_config)
        config['security_server'][0]['tls_certificates'] = [self.tls_cert_existing]
        return config

    def ss_config_with_tls_cert_non_existing(self):
        config = copy.deepcopy(self.ss_config)
        config['security_server'][0]['tls_certificates'] = [self.tls_cert_non_existing]
        return config

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


    def test_client_import_tls_certificate(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_class='GOV',
                    member_code='9876',
                    member_name='TEST',
                    subsystem_code=None,
                    connection_type=ConnectionType.HTTP,
                    status=ClientStatus.REGISTERED,
                    owner=True,
                    has_valid_local_sign_cert=True
            )]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_tls_certificate', return_value=None):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config_with_tls_cert())
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.import_tls_certs()

                    out, err = self.capsys.readouterr()
                    assert out.count("Import TLS certificate '%s' for client" % self.tls_cert_existing) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_client_import_tls_certificate_not_existing(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients', return_value=[Client(
                    id='DEV:GOV:9876:SUB1',
                    instance_id='DEV',
                    member_class='GOV',
                    member_code='9876',
                    member_name='TEST',
                    subsystem_code=None,
                    connection_type=ConnectionType.HTTP,
                    status=ClientStatus.REGISTERED,
                    owner=True,
                    has_valid_local_sign_cert=True
            )]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_tls_certificate', return_value=None):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config_with_tls_cert_non_existing())
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.import_tls_certs()

                    out, err = self.capsys.readouterr()
                    assert out.count("references non-existent file '%s'" % self.tls_cert_non_existing) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_client_import_tls_certificate_already_imported(self):
        class AlreadyImportedResponse:
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
                    member_name='TEST',
                    subsystem_code=None,
                    connection_type=ConnectionType.HTTP,
                    status=ClientStatus.REGISTERED,
                    owner=True,
                    has_valid_local_sign_cert=True
            )]):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.add_client_tls_certificate',
                                side_effect=ApiException(http_resp=AlreadyImportedResponse())):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config_with_tls_cert())
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.import_tls_certs()

                    out, err = self.capsys.readouterr()
                    assert out.count("TLS certificate '%s' for client DEV:GOV:9876:SUB1 already exists" % self.tls_cert_existing) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_client_unregister(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.unregister_client',
                            return_value=None):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.unregister()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "Unregister client: 'DEV:GOV:9876:SUB1' for security server: 'ssX'") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_unregister_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.unregister_client',
                            return_value=None):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.unregister()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "The following parameters missing for unregister clients: ['client']") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_unregister_fail_security_server_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None, client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.unregister_client',
                            return_value=None):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.unregister()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "The following parameters missing for unregister clients: ['ss']") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_already_unregister(self):
        class AlreadyUnregisterResponse:
            status = 409
            data = '{"status":409,"error":{"code":"client_already_unregister"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.unregister_client',
                            side_effect=ApiException(http_resp=AlreadyUnregisterResponse())):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.unregister()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "Client: 'DEV:GOV:9876:SUB1' for security server: 'ssX', already unregistered") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_delete(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.delete_client',
                            return_value=None):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "Deleted client: 'DEV:GOV:9876:SUB1' for security server: 'ssX'") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_delete_fail_client_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.delete_client',
                            return_value=None):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "The following parameters missing for deleting clients: ['client']") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_delete_fail_security_server_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None, client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.delete_client',
                            return_value=None):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "The following parameters missing for deleting clients: ['ss']") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_not_found(self):
        class AlreadyUnregisterResponse:
            status = 404
            data = '{"status":404,"error":{"code":"client_not_found"}}'
            reason = None

            def getheaders(self): return None

        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', client='DEV:GOV:9876:SUB1')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.delete_client',
                            side_effect=ApiException(http_resp=AlreadyUnregisterResponse())):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count(
                    "Error deleting client: 'DEV:GOV:9876:SUB1' for security server: 'ssX', not found") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_client_make_owner(self):
        ss = 'ssX'
        member = 'DEV:GOV:9876'
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=ss, member=member)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client', return_value=ClientTestData.make_owner_response):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.change_owner', return_value=None):
                    with mock.patch('xrdsst.controllers.token.TokenController.remote_token_add_auth_key_with_csrs', return_value=None):
                        client_controller = ClientController()
                        client_controller.app = app
                        client_controller.load_config = (lambda: self.ss_config_with_tls_cert_non_existing())
                        client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        client_controller.make_owner()

                        out, err = self.capsys.readouterr()
                        assert out.count("Change owner request submitted: '%s' for security server: '%s'" % (member, ss)) > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_client_make_owner_owner_is_subsystem(self):
        ss = 'ssX'
        member = 'DEV:GOV:9876:SUB1'
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=ss, member=member)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client', return_value=ClientTestData.add_response):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.change_owner', return_value=None):
                    with mock.patch('xrdsst.controllers.token.TokenController.remote_token_add_auth_key_with_csrs',
                                    return_value=None):
                        client_controller = ClientController()
                        client_controller.app = app
                        client_controller.load_config = (lambda: self.ss_config_with_tls_cert_non_existing())
                        client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                        client_controller.make_owner()

                        out, err = self.capsys.readouterr()
                        assert out.count("It's not possible to make owner to subsystems: %s for security server: '%s'"
                                         % (member, ss)) > 0

                        with self.capsys.disabled():
                            sys.stdout.write(out)
                            sys.stderr.write(err)

    def test_client_make_owner_already_owner(self):
        class AlreadyOwnerResponse:
            status = 400
            data = '{"status":400,"error":{"code":"member_already_owner"}}'
            reason = None

            def getheaders(self): return None

        ss = 'ssX'
        member = 'DEV:GOV:9876'
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=ss, member=member)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.get_client', return_value=ClientTestData.make_owner_response):
                with mock.patch('xrdsst.api.clients_api.ClientsApi.change_owner',
                                side_effect=ApiException(http_resp=AlreadyOwnerResponse())):
                    client_controller = ClientController()
                    client_controller.app = app
                    client_controller.load_config = (lambda: self.ss_config_with_tls_cert_non_existing())
                    client_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
                    client_controller.make_owner()

                    out, err = self.capsys.readouterr()
                    assert out.count("Member: '%s' for security server: '%s', already owner" % (member, ss)) > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_client_list(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX')
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                            return_value=[ClientTestData.add_response]):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.list()

                for header in ClientsListMapper.headers():
                    assert header in client_controller.app._last_rendered[0][0]

                assert client_controller.app._last_rendered[0][1][0] == 'DEV:GOV:9876:SUB1'
                assert client_controller.app._last_rendered[0][1][1] == 'DEV'
                assert client_controller.app._last_rendered[0][1][2] == 'GOV'

    def test_key_list_ss_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None)
            with mock.patch('xrdsst.api.clients_api.ClientsApi.find_clients',
                            return_value=[ClientTestData.add_response]):
                client_controller = ClientController()
                client_controller.app = app
                client_controller.load_config = (lambda: self.ss_config)
                client_controller.list()

                out, err = self.capsys.readouterr()
                assert out.count("The following parameters missing listing clients: ['ss']") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

                assert client_controller.app._last_rendered is None
