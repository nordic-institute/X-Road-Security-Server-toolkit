import sys
import unittest
from argparse import Namespace
from datetime import datetime
from unittest import mock
import pytest

from xrdsst.controllers.backup import BackupController
from xrdsst.main import XRDSSTTest
from xrdsst.models import Backup


class TestBackup(unittest.TestCase):
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

    def test_backup_list_render_tabulated(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.backups_api.BackupsApi.get_backups',
                                return_value=[Backup(filename='backup.tar', created_at=datetime.now())]):
                    backup_controller = BackupController()
                    backup_controller.app = app
                    backup_controller.load_config = (lambda: self.ss_config)
                    backup_controller.list()

                assert backup_controller.app._last_rendered[0][1][1] is 'backup.tar'

    def test_backup_list_render_as_object(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.backups_api.BackupsApi.get_backups',
                                return_value=[Backup(filename='backup.tar', created_at=datetime.now())]):
                    backup_controller = BackupController()
                    backup_controller.app = app
                    backup_controller.load_config = (lambda: self.ss_config)
                    backup_controller.list()

                    assert backup_controller.app._last_rendered[0][0]["file_name"] is 'backup.tar'

    def test_backup_list_fail_ss_name_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=True):
                with mock.patch('xrdsst.api.backups_api.BackupsApi.get_backups',
                                return_value=[Backup(filename='backup.tar', created_at=datetime.now())]):
                    backup_controller = BackupController()
                    backup_controller.app = app
                    backup_controller.load_config = (lambda: self.ss_config)
                    backup_controller.list()

                assert backup_controller.app._last_rendered is None

    def test_backup_add(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX')
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.backups_api.BackupsApi.add_backup',
                                return_value=Backup(filename='backup.tar', created_at=datetime.now())):
                    backup_controller = BackupController()
                    backup_controller.app = app
                    backup_controller.load_config = (lambda: self.ss_config)
                    backup_controller.add()

                    out, err = self.capsys.readouterr()
                    assert out.count("Created backup") > 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_backup_add_fail_ss_name_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None)
            with mock.patch('xrdsst.controllers.base.BaseController.is_output_tabulated', return_value=False):
                with mock.patch('xrdsst.api.backups_api.BackupsApi.add_backup',
                                return_value=Backup(filename='backup.tar', created_at=datetime.now())):
                    backup_controller = BackupController()
                    backup_controller.app = app
                    backup_controller.load_config = (lambda: self.ss_config)
                    backup_controller.add()

                    out, err = self.capsys.readouterr()
                    assert out.count("Creates backup") == 0

                    with self.capsys.disabled():
                        sys.stdout.write(out)
                        sys.stderr.write(err)

    def test_backup_download(self):
        class MockBackup:
            def __init__(self, status, data):
                self.status = status
                self.data = data

        def mocked_download_backup():
            return MockBackup(
                200,
                b'073656375726974795f58524f41445f362e32345f4445562f474f562f313233342f7373333134303733333332373531303037323432'
            )
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', file='backup.tar')
            with mock.patch('xrdsst.api.backups_api.BackupsApi.download_backup', return_value=mocked_download_backup()):
                backup_controller = BackupController()
                backup_controller.app = app
                backup_controller.load_config = (lambda: self.ss_config)
                backup_controller.download()

                out, err = self.capsys.readouterr()
                assert out.count("Downloaded backup") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_backup_download_fail_ss_name_missing(self):
        class MockBackup:
            def __init__(self, status, data):
                self.status = status
                self.data = data

        def mocked_download_backup():
            return MockBackup(
                200,
                b'073656375726974795f58524f41445f362e32345f4445562f474f562f313233342f7373333134303733333332373531303037323432'
            )
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None, file='backup.tar')
            with mock.patch('xrdsst.api.backups_api.BackupsApi.download_backup', return_value=mocked_download_backup()):
                backup_controller = BackupController()
                backup_controller.app = app
                backup_controller.load_config = (lambda: self.ss_config)
                backup_controller.download()

                out, err = self.capsys.readouterr()
                assert out.count("Downloaded backup") == 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_backup_download_fail_file_name_missing(self):
        class MockBackup:
            def __init__(self, status, data):
                self.status = status
                self.data = data

        def mocked_download_backup():
            return MockBackup(
                200,
                b'073656375726974795f58524f41445f362e32345f4445562f474f562f313233342f7373333134303733333332373531303037323432'
            )
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', file=None)
            with mock.patch('xrdsst.api.backups_api.BackupsApi.download_backup', return_value=mocked_download_backup()):
                backup_controller = BackupController()
                backup_controller.app = app
                backup_controller.load_config = (lambda: self.ss_config)
                backup_controller.download()

                out, err = self.capsys.readouterr()
                assert out.count("Downloaded backup") == 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_backup_delete(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', file='backup.tar')
            with mock.patch('xrdsst.api.backups_api.BackupsApi.delete_backup', return_value=None):
                backup_controller = BackupController()
                backup_controller.app = app
                backup_controller.load_config = (lambda: self.ss_config)
                backup_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count("Deleted backup") > 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_backup_delete_fail_ss_name_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss=None, file='backup.tar')
            with mock.patch('xrdsst.api.backups_api.BackupsApi.delete_backup', return_value=None):
                backup_controller = BackupController()
                backup_controller.app = app
                backup_controller.load_config = (lambda: self.ss_config)
                backup_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count("Deleted backup") == 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)

    def test_backup_delete_fail_file_name_missing(self):
        with XRDSSTTest() as app:
            app._parsed_args = Namespace(ss='ssX', file=None)
            with mock.patch('xrdsst.api.backups_api.BackupsApi.delete_backup', return_value=None):
                backup_controller = BackupController()
                backup_controller.app = app
                backup_controller.load_config = (lambda: self.ss_config)
                backup_controller.delete()

                out, err = self.capsys.readouterr()
                assert out.count("Deleted backup") == 0

                with self.capsys.disabled():
                    sys.stdout.write(out)
                    sys.stderr.write(err)
