from xrdsst.controllers.backup import BackupController
from xrdsst.controllers.base import BaseController
from xrdsst.main import XRDSSTTest


class BackupTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_add_backup(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                backups = backup_controller.remote_list_backups(configuration, security_server)
                assert len(backups) == 0
                response = backup_controller.remote_add_backup(configuration, security_server["name"])
                assert response is not None
                assert "conf_backup" in response.filename
                assert response.created_at is not None

    def step_list_backups(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                assert "conf_backup" in response[0]["file_name"]
                assert response[0]["created"] is not None

    def step_download_backups(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                file_name = response[0]["file_name"]
                response = backup_controller.remote_download_backup(configuration, security_server["name"], [file_name])
                assert len(response) == 1
                assert response[0] == '/tmp/' + file_name

    def step_restore_backup(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                file_name = response[0]["file_name"]
                response = backup_controller.remote_restore_backup(configuration, security_server["name"], file_name)
                assert response is not None

    def step_delete_backups(self):
        with XRDSSTTest() as app:
            base = BaseController()
            backup_controller = BackupController()
            backup_controller.app = app
            for security_server in self.test.config["security_server"]:
                configuration = base.create_api_config(security_server, self.test.config)
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 1
                file_name = response[0]["file_name"]
                backup_controller.remote_delete_backup(configuration, security_server["name"], [file_name])
                response = backup_controller.remote_list_backups(configuration, security_server)
                assert len(response) == 0

    def test_run_configuration(self):
        self.step_add_backup()
        self.step_list_backups()
        self.step_download_backups()
        self.step_restore_backup()
        self.step_delete_backups()
