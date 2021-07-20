import unittest

from datetime import datetime
from unittest import mock
import pytest

from xrdsst.controllers.diagnostics import DiagnosticsController
from xrdsst.main import XRDSSTTest
from xrdsst.models import GlobalConfDiagnostics, AllOfGlobalConfDiagnosticsStatusClass, AllOfGlobalConfDiagnosticsStatusCode, OcspResponderDiagnostics, \
    OcspResponder, TimestampingServiceDiagnostics, AllOfTimestampingServiceDiagnosticsStatusClass, AllOfTimestampingServiceDiagnosticsStatusCode, \
    AllOfOcspResponderStatusClass, AllOfOcspResponderStatusCode


class TestDiagnostics(unittest.TestCase):
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

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_diagnostics_global_configuration_render_tabulated(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_global_conf_diagnostics',
                                return_value=GlobalConfDiagnostics(status_class=AllOfGlobalConfDiagnosticsStatusClass.OK,
                                                                   status_code=AllOfGlobalConfDiagnosticsStatusCode.SUCCESS,
                                                                   prev_update_at=datetime.now(),
                                                                   next_update_at=datetime.now())):
                    diagnostics_controller = DiagnosticsController()
                    diagnostics_controller.app = app
                    diagnostics_controller.load_config = (lambda: self.ss_config)
                    diagnostics_controller.global_configuration()

                assert diagnostics_controller.app._last_rendered[0][1][1] is 'OK'
                assert diagnostics_controller.app._last_rendered[0][1][2] is 'SUCCESS'
                assert diagnostics_controller.app._last_rendered[0][1][3] is not None
                assert diagnostics_controller.app._last_rendered[0][1][4] is not None

    def test_member_find_render_as_object(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_global_conf_diagnostics',
                                return_value=GlobalConfDiagnostics(status_class=AllOfGlobalConfDiagnosticsStatusClass.OK,
                                                                   status_code=AllOfGlobalConfDiagnosticsStatusCode.SUCCESS,
                                                                   prev_update_at=datetime.now(),
                                                                   next_update_at=datetime.now())):
                    diagnostics_controller = DiagnosticsController()
                    diagnostics_controller.app = app
                    diagnostics_controller.load_config = (lambda: self.ss_config)
                    diagnostics_controller.global_configuration()

                assert diagnostics_controller.app._last_rendered[0][0]["status_class"] is 'OK'
                assert diagnostics_controller.app._last_rendered[0][0]["status_code"] is 'SUCCESS'
                assert diagnostics_controller.app._last_rendered[0][0]["prev_update_at"] is not None
                assert diagnostics_controller.app._last_rendered[0][0]["next_update_at"] is not None

    def test_diagnostics_ocsp_responders_render_tabulated(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_ocsp_responders_diagnostics',
                                return_value=[OcspResponderDiagnostics(distinguished_name='TEST',
                                                                       ocsp_responders=[OcspResponder(url='http://127.0.0.1:8888',
                                                                                                      status_class=AllOfOcspResponderStatusClass.OK,
                                                                                                      status_code=AllOfOcspResponderStatusCode.SUCCESS,
                                                                                                      prev_update_at=datetime.now(),
                                                                                                      next_update_at=datetime.now())])]):
                    diagnostics_controller = DiagnosticsController()
                    diagnostics_controller.app = app
                    diagnostics_controller.load_config = (lambda: self.ss_config)
                    diagnostics_controller.ocsp_responders()

                assert diagnostics_controller.app._last_rendered[0][1][1] is 'TEST'
                assert diagnostics_controller.app._last_rendered[0][1][2] is 'http://127.0.0.1:8888'
                assert diagnostics_controller.app._last_rendered[0][1][3] is 'OK'
                assert diagnostics_controller.app._last_rendered[0][1][4] is 'SUCCESS'
                assert diagnostics_controller.app._last_rendered[0][1][5] is not None
                assert diagnostics_controller.app._last_rendered[0][1][6] is not None

    def test_diagnostics_ocsp_responders_render_as_object(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_ocsp_responders_diagnostics',
                                return_value=[OcspResponderDiagnostics(distinguished_name='TEST',
                                                                       ocsp_responders=[OcspResponder(url='http://127.0.0.1:8888',
                                                                                                      status_class=AllOfOcspResponderStatusClass.OK,
                                                                                                      status_code=AllOfOcspResponderStatusCode.SUCCESS,
                                                                                                      prev_update_at=datetime.now(),
                                                                                                      next_update_at=datetime.now())])]):
                    diagnostics_controller = DiagnosticsController()
                    diagnostics_controller.app = app
                    diagnostics_controller.load_config = (lambda: self.ss_config)
                    diagnostics_controller.ocsp_responders()

                assert diagnostics_controller.app._last_rendered[0][0]["name"] is 'TEST'
                assert diagnostics_controller.app._last_rendered[0][0]["url"] is 'http://127.0.0.1:8888'
                assert diagnostics_controller.app._last_rendered[0][0]["status_class"] is 'OK'
                assert diagnostics_controller.app._last_rendered[0][0]["status_code"] is 'SUCCESS'
                assert diagnostics_controller.app._last_rendered[0][0]["prev_update_at"] is not None
                assert diagnostics_controller.app._last_rendered[0][0]["next_update_at"] is not None

    def test_diagnostics_timestamping_services_render_tabulated(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_timestamping_services_diagnostics',
                                return_value=[TimestampingServiceDiagnostics(url='http://127.0.0.1:8888',
                                                                             status_class=AllOfTimestampingServiceDiagnosticsStatusClass.OK,
                                                                             status_code=AllOfTimestampingServiceDiagnosticsStatusCode.SUCCESS,
                                                                             prev_update_at=datetime.now())]):
                    diagnostics_controller = DiagnosticsController()
                    diagnostics_controller.app = app
                    diagnostics_controller.load_config = (lambda: self.ss_config)
                    diagnostics_controller.timestamping_services()

                assert diagnostics_controller.app._last_rendered[0][1][1] is 'http://127.0.0.1:8888'
                assert diagnostics_controller.app._last_rendered[0][1][2] is 'OK'
                assert diagnostics_controller.app._last_rendered[0][1][3] is 'SUCCESS'
                assert diagnostics_controller.app._last_rendered[0][1][4] is not None

    def test_diagnostics_timestamping_services_render_as_object(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_timestamping_services_diagnostics',
                                return_value=[TimestampingServiceDiagnostics(url='http://127.0.0.1:8888',
                                                                             status_class=AllOfTimestampingServiceDiagnosticsStatusClass.OK,
                                                                             status_code=AllOfTimestampingServiceDiagnosticsStatusCode.SUCCESS,
                                                                             prev_update_at=datetime.now())]):
                    diagnostics_controller = DiagnosticsController()
                    diagnostics_controller.app = app
                    diagnostics_controller.load_config = (lambda: self.ss_config)
                    diagnostics_controller.timestamping_services()

                assert diagnostics_controller.app._last_rendered[0][0]["url"] is 'http://127.0.0.1:8888'
                assert diagnostics_controller.app._last_rendered[0][0]["status_class"] is 'OK'
                assert diagnostics_controller.app._last_rendered[0][0]["status_code"] is 'SUCCESS'
                assert diagnostics_controller.app._last_rendered[0][0]["prev_update_at"] is not None

    def test_diagnostics_all_render_tabulated(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_global_conf_diagnostics',
                                return_value=GlobalConfDiagnostics(status_class=AllOfGlobalConfDiagnosticsStatusClass.OK,
                                                                   status_code=AllOfGlobalConfDiagnosticsStatusCode.SUCCESS,
                                                                   prev_update_at=datetime.now(),
                                                                   next_update_at=datetime.now())):
                    with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_ocsp_responders_diagnostics',
                                    return_value=[OcspResponderDiagnostics(distinguished_name='TEST',
                                                                           ocsp_responders=[OcspResponder(url='http://127.0.0.1:8888',
                                                                                                          status_class=AllOfOcspResponderStatusClass.OK,
                                                                                                          status_code=AllOfOcspResponderStatusCode.SUCCESS,
                                                                                                          prev_update_at=datetime.now(),
                                                                                                          next_update_at=datetime.now())])]):
                        with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_timestamping_services_diagnostics',
                                        return_value=[TimestampingServiceDiagnostics(url='http://127.0.0.1:8888',
                                                                                     status_class=AllOfTimestampingServiceDiagnosticsStatusClass.OK,
                                                                                     status_code=AllOfTimestampingServiceDiagnosticsStatusCode.SUCCESS,
                                                                                     prev_update_at=datetime.now())]):
                            diagnostics_controller = DiagnosticsController()
                            diagnostics_controller.app = app
                            diagnostics_controller.load_config = (lambda: self.ss_config)
                            diagnostics_controller.all()

                            assert diagnostics_controller.app._last_rendered[0][1][1] is 'http://127.0.0.1:8888'
                            assert diagnostics_controller.app._last_rendered[0][1][2] is 'OK'
                            assert diagnostics_controller.app._last_rendered[0][1][3] is 'SUCCESS'
                            assert diagnostics_controller.app._last_rendered[0][1][4] is not None

    def test_diagnostics_all_render_as_object(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_global_conf_diagnostics',
                                return_value=GlobalConfDiagnostics(status_class=AllOfGlobalConfDiagnosticsStatusClass.OK,
                                                                   status_code=AllOfGlobalConfDiagnosticsStatusCode.SUCCESS,
                                                                   prev_update_at=datetime.now(),
                                                                   next_update_at=datetime.now())):
                    with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_ocsp_responders_diagnostics',
                                    return_value=[OcspResponderDiagnostics(distinguished_name='TEST',
                                                                           ocsp_responders=[OcspResponder(url='http://127.0.0.1:8888',
                                                                                                          status_class=AllOfOcspResponderStatusClass.OK,
                                                                                                          status_code=AllOfOcspResponderStatusCode.SUCCESS,
                                                                                                          prev_update_at=datetime.now(),
                                                                                                          next_update_at=datetime.now())])]):
                        with mock.patch('xrdsst.api.diagnostics_api.DiagnosticsApi.get_timestamping_services_diagnostics',
                                        return_value=[TimestampingServiceDiagnostics(url='http://127.0.0.1:8888',
                                                                                     status_class=AllOfTimestampingServiceDiagnosticsStatusClass.OK,
                                                                                     status_code=AllOfTimestampingServiceDiagnosticsStatusCode.SUCCESS,
                                                                                     prev_update_at=datetime.now())]):
                            diagnostics_controller = DiagnosticsController()
                            diagnostics_controller.app = app
                            diagnostics_controller.load_config = (lambda: self.ss_config)
                            diagnostics_controller.all()

                            assert diagnostics_controller.app._last_rendered[0][0]["url"] is 'http://127.0.0.1:8888'
                            assert diagnostics_controller.app._last_rendered[0][0]["status_class"] is 'OK'
                            assert diagnostics_controller.app._last_rendered[0][0]["status_code"] is 'SUCCESS'
                            assert diagnostics_controller.app._last_rendered[0][0]["prev_update_at"] is not None
