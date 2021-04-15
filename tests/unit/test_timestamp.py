import os
import unittest
from pathlib import Path
from unittest import mock

import pytest

from xrdsst.core.definitions import ROOT_DIR
from tests.util.test_util import StatusTestData
from xrdsst.api import TimestampingServicesApi, SystemApi
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.main import XRDSSTTest
from xrdsst.models import TimestampingService
from xrdsst.rest.rest import ApiException


class TimestampTestData:
    timestamp_service_response = TimestampingService(
        name='one name to rule them all',
        url='http://in.the.darkness.bind.them:8899'
    )

    timestamp_service_list_response = [
        timestamp_service_response
    ]


class TestTimestamp(unittest.TestCase):
    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    ss_config = {
        'admin_credentials': 'user:pass',
        'logging': {'file': str(Path.home()) + '/xrdsst_tests.log', 'level': 'INFO'},
        'ssh_access': {'user': 'user', 'private_key': 'key'},
        'security_server':
            [{'name': 'ss',
              'url': 'https://ss:4000/api/v1',
              'api_key': 'X-Road-apikey token=<API_KEY>',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS',
              'software_token_pin': '1234',
              'software_token_id': 0},
             {'name': 'ss2',
              'url': 'https://ss:4000/api/v1',
              'api_key': 'X-Road-apikey token=<API_KEY>',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS2',
              'software_token_pin': '1234',
              'software_token_id': 0}
             ]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_timestamp_service_approved_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.timestamping_services_api.TimestampingServicesApi'
                            '.get_approved_timestamping_services',
                            return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: self.ss_config)
                timestamp_controller.list_approved()

    def test_timestamp_service_configured_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.get_configured_timestamping_services',
                            return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: self.ss_config)
                timestamp_controller.list_configured()

    def test_timestamp_get_configured(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.get_configured_timestamping_services',
                            return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: self.ss_config)
                for security_server in self.ss_config["security_server"]:
                    configuration = timestamp_controller.create_api_config(security_server, self.ss_config)
                    response = timestamp_controller.remote_get_configured(configuration)
                    assert response == TimestampTestData.timestamp_service_list_response

    def test_timestamp_get_configured_exception(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.get_configured_timestamping_services',
                            side_effect=ApiException):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: self.ss_config)
                for security_server in self.ss_config["security_server"]:
                    configuration = timestamp_controller.create_api_config(security_server, self.ss_config)
                    timestamp_controller.remote_get_configured(configuration)
                    self.assertRaises(ApiException)

    @mock.patch.object(TimestampingServicesApi, 'get_approved_timestamping_services', (lambda x, **kwargs: TimestampTestData.timestamp_service_list_response))
    @mock.patch.object(SystemApi, 'add_configured_timestamping_service', (lambda x, **kwargs: TimestampTestData.timestamp_service_response))
    def test_timestamp_service_init(self):
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            timestamp_controller.load_config = (lambda: self.ss_config)
            timestamp_controller.get_server_status = (lambda x, y: StatusTestData.server_status_essentials_complete)
            timestamp_controller.init()

    def test_timestamp_service_init_nonresolving_url(self):
        with XRDSSTTest() as app:
            with mock.patch(
                    'xrdsst.api.timestamping_services_api.TimestampingServicesApi.get_approved_timestamping_services',
                    return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: self.ss_config)
                timestamp_controller.init()

                out, err = self.capsys.readouterr()
                assert out.count("SKIPPED 'ss': no connectivity") > 0
