import unittest
from argparse import Namespace
from unittest import mock
import pytest
from xrdsst.controllers.member import MemberController
from xrdsst.main import XRDSSTTest
from xrdsst.models import MemberName


class TestMember(unittest.TestCase):
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

    def test_member_find_render_tabulated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(mclass='GOV', mcode='1234')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.member_names_api.MemberNamesApi.find_member_name', return_value=MemberName(member_name='ACME')):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.find()

                assert member_controller.app._last_rendered[0][1][1] is 'ACME'

    def test_member_find_render_as_object(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(mclass='GOV', mcode='1234')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.member_names_api.MemberNamesApi.find_member_name', return_value=MemberName(member_name='ACME')):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.find()

                    assert member_controller.app._last_rendered[0][0]["member_name"] is 'ACME'

    def test_member_find_fail_member_class_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(mclass=None, mcode='1234')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.member_names_api.MemberNamesApi.find_member_name', return_value=MemberName(member_name='ACME')):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.find()

                assert member_controller.app._last_rendered is None

    def test_member_find_fail_member_code_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(mclass='GOV', mcode=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.member_names_api.MemberNamesApi.find_member_name', return_value=MemberName(member_name='ACME')):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.find()

                assert member_controller.app._last_rendered is None

    def test_member_list_classes_render_tabulated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(instance='DEV')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.member_classes_api.MemberClassesApi.get_member_classes_for_instance',
                                return_value=['GOV']):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.list_classes()

                assert member_controller.app._last_rendered[0][1][2] is 'GOV'

    def test_member_list_classes_render_as_object(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(instance='DEV')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.member_classes_api.MemberClassesApi.get_member_classes_for_instance',
                                return_value=['GOV']):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.list_classes()

                assert member_controller.app._last_rendered[0][0]["member_class"] is 'GOV'

    def test_member_list_classes_fail_instance_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(instance=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.member_classes_api.MemberClassesApi.get_member_classes_for_instance',
                                return_value=['GOV']):
                    member_controller = MemberController()
                    member_controller.app = app
                    member_controller.load_config = (lambda: self.ss_config)
                    member_controller.list_classes()

                assert member_controller.app._last_rendered is None
