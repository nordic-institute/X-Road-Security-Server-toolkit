
import unittest
from unittest import mock, TestCase
import urllib3

from xrdsst.controllers.timestamp import TimestampController
from xrdsst.main import XRDSSTTest
from xrdsst.models import TimestampingService

class TimestampTestData:
    timestamp_service_response = TimestampingService(
        name='one name to rule them all',
        url='http://in.the.darkness.bind.them:8899'
    )

    timestamp_service_list_response = [
        timestamp_service_response
    ]

class TestTimestamp(unittest.TestCase):
    ss_config = {
        'logging': [{'file': '/tmp/xrdsst_test_token_log', 'level': 'INFO'}],
        'security-server':
            [{'name': 'ssX',
              'url': 'https://non.existing.url.blah:8999/api/v1',
              'api_key': 'X-Road-apikey token=api-key',
              'configuration_anchor': '/tmp/configuration-anchor.xml',
              'owner_member_class': 'VOG',
              'owner_member_code': '4321',
              'security_server_code': 'SS3',
              'software_token_id': '0',
              'software_token_pin': '1122'}]}

    def test_timestamp_service_approved_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.timestamping_services_api.TimestampingServicesApi.get_approved_timestamping_services',
                             return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: TestTimestamp.ss_config)
                timestamp_controller.list_approved()

    def test_timestamp_service_configured_list(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.system_api.SystemApi.get_configured_timestamping_services',
                             return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: TestTimestamp.ss_config)
                timestamp_controller.list_configured()

    def test_timestamp_service_init(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.timestamping_services_api.TimestampingServicesApi.get_approved_timestamping_services',
                             return_value=TimestampTestData.timestamp_service_list_response):
                with mock.patch('xrdsst.api.system_api.SystemApi.add_configured_timestamping_service',
                             return_value=TimestampTestData.timestamp_service_response):
                    timestamp_controller = TimestampController()
                    timestamp_controller.app = app
                    timestamp_controller.load_config = (lambda: TestTimestamp.ss_config)
                    timestamp_controller.init()

    def test_timestamp_service_init_nonresolving_url(self):
        with XRDSSTTest() as app:
            with mock.patch('xrdsst.api.timestamping_services_api.TimestampingServicesApi.get_approved_timestamping_services',
                             return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: TestTimestamp.ss_config)
                TestCase.assertRaises(TestTimestamp, urllib3.exceptions.MaxRetryError, lambda: timestamp_controller.init())
