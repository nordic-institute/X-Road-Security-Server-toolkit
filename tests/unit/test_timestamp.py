import unittest
from unittest import mock, TestCase
import urllib3

from tests.unit.test_base_controller import TestBaseController
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
    base_controller = TestBaseController()
    ss_config = base_controller.get_ss_config()

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

    def test_timestamp_service_init(self):
        with XRDSSTTest() as app:
            with mock.patch(
                    'xrdsst.api.timestamping_services_api.TimestampingServicesApi.get_approved_timestamping_services',
                    return_value=TimestampTestData.timestamp_service_list_response):
                with mock.patch('xrdsst.api.system_api.SystemApi.add_configured_timestamping_service',
                                return_value=TimestampTestData.timestamp_service_response):
                    timestamp_controller = TimestampController()
                    timestamp_controller.app = app
                    timestamp_controller.load_config = (lambda: self.ss_config)
                    timestamp_controller.init()

    def test_timestamp_service_init_nonresolving_url(self):
        with XRDSSTTest() as app:
            with mock.patch(
                    'xrdsst.api.timestamping_services_api.TimestampingServicesApi.get_approved_timestamping_services',
                    return_value=TimestampTestData.timestamp_service_list_response):
                timestamp_controller = TimestampController()
                timestamp_controller.app = app
                timestamp_controller.load_config = (lambda: self.ss_config)
                TestCase.assertRaises(self, urllib3.exceptions.MaxRetryError,
                                      lambda: timestamp_controller.init())
