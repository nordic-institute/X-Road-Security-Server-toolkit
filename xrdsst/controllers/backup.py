import os

from cement import ex
from xrdsst.api import BackupsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.core.util import parse_argument_list
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException


class BackupListMapper:
    @staticmethod
    def headers():
        return ['SECURITY_SERVER', 'FILE_NAME', 'CREATED']

    @staticmethod
    def as_list(backup):
        return [backup.get('security_server'), backup.get('file_name'), backup.get('created')]

    @staticmethod
    def as_object(backup):
        return {
            'security_server': backup.get('security_server'),
            'file_name': backup.get('file_name'),
            'created': backup.get('created')
        }


class BackupController(BaseController):
    class Meta:
        label = 'backup'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['backup.controller.description']

    FOR_SECURITY_SERVER = 'for security server'

    @ex(help="List backups", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'})])
    def list(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for listing backups: %s' % missing_parameters)
            return

        self.list_server_backups(active_config, self.app.pargs.ss)

    @ex(help="Add backup", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'})])
    def add(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for creating backups: %s' % missing_parameters)
            return

        self.add_server_backup(active_config, self.app.pargs.ss)

    @ex(help="Download backups", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                            (['--file'], {'help': 'Backup file name', 'dest': 'file'})])
    def download(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.file is None:
            missing_parameters.append('file')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for downloading backups: %s' % missing_parameters)
            return

        file_names = parse_argument_list(self.app.pargs.file)

        self.download_backup(active_config, self.app.pargs.ss, file_names)

    @ex(help="Delete backups", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                          (['--file'], {'help': 'Backup file name', 'dest': 'file'})])
    def delete(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.file is None:
            missing_parameters.append('file')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for deleting backups: %s' % missing_parameters)
            return

        file_names = parse_argument_list(self.app.pargs.file)

        self.delete_backup(active_config, self.app.pargs.ss, file_names)

    @ex(help="Restore from backup", arguments=[(['--ss'], {'help': 'Security server name', 'dest': 'ss'}),
                                               (['--file'], {'help': 'Backup file name', 'dest': 'file'})])
    def restore(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.ss is None:
            missing_parameters.append('ss')
        if self.app.pargs.file is None:
            missing_parameters.append('file')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for restoring from backups: %s' % missing_parameters)
            return

        self.restore_backup(active_config, self.app.pargs.ss, self.app.pargs.file)

    def list_server_backups(self, config, ss_name):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_list_backups(ss_api_config, security_server)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def add_server_backup(self, config, ss_name):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_add_backup(ss_api_config, ss_name)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def download_backup(self, config, ss_name, file_names):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_download_backup(ss_api_config, ss_name, file_names)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def delete_backup(self, config, ss_name, file_names):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_delete_backup(ss_api_config, ss_name, file_names)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def restore_backup(self, config, ss_name, file_name):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            if security_server["name"] == ss_name:
                ss_api_config = self.create_api_config(security_server, config)
                self.remote_restore_backup(ss_api_config, ss_name, file_name)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_list_backups(self, ss_api_config, security_server):
        backups_api = BackupsApi(ApiClient(ss_api_config))
        try:
            backups_list = []
            backups = backups_api.get_backups()
            for backup in backups:
                backups_list.append({'security_server': security_server["name"],
                                     'file_name': backup.filename,
                                     'created': backup.created_at.strftime("%Y/%m/%d")})
            render_data = []
            if self.is_output_tabulated():
                render_data = [BackupListMapper.headers()]
                render_data.extend(map(BackupListMapper.as_list, backups_list))
            else:
                render_data.extend(map(BackupListMapper.as_object, backups_list))
            self.render(render_data)
            return backups_list
        except ApiException as err:
            BaseController.log_api_error('BackupsApi->get_backups', err)

    @staticmethod
    def remote_add_backup(ss_api_config, ss_name):
        backups_api = BackupsApi(ApiClient(ss_api_config))
        try:
            response = backups_api.add_backup()
            if response is not None:
                BaseController.log_info("Created backup '" + response.filename + "' " + BackupController.FOR_SECURITY_SERVER + "' " + ss_name + "'")
            return response
        except ApiException as err:
            BaseController.log_api_error('BackupsApi->get_backups', err)

    @staticmethod
    def remote_download_backup(ss_api_config, ss_name, file_names):
        backups_api = BackupsApi(ApiClient(ss_api_config))
        try:
            response_list = []
            for file_name in file_names:
                response = backups_api.download_backup(filename=file_name, _preload_content=False)
                if response is not None:
                    with open(os.path.join('/tmp/', file_name), "wb") as file:
                        file.write(response.data)
                        response_list.append(file.name)
                        BaseController.log_info("Downloaded backup '" + file_name + "' " + BackupController.FOR_SECURITY_SERVER + "' " + ss_name
                                                + "' to '" + os.path.join('/tmp/', file_name) + "'")
                else:
                    BaseController.log_info("Failed to download backup '" + file_name + "'")
            return response_list
        except ApiException as err:
            BaseController.log_api_error('BackupsApi->download_backup', err)

    @staticmethod
    def remote_delete_backup(ss_api_config, ss_name, file_names):
        backups_api = BackupsApi(ApiClient(ss_api_config))
        try:
            for file_name in file_names:
                backups_api.delete_backup(filename=file_name)
                BaseController.log_info("Deleted backup '" + file_name + "' " + BackupController.FOR_SECURITY_SERVER + "' " + ss_name + "'")
        except ApiException as err:
            BaseController.log_api_error('BackupsApi->delete_backup', err)

    @staticmethod
    def remote_restore_backup(ss_api_config, ss_name, file_name):
        backups_api = BackupsApi(ApiClient(ss_api_config))
        try:
            response = backups_api.restore_backup(filename=file_name)
            if response is not None:
                BaseController.log_info("Restored from backup '" + file_name + "' " + BackupController.FOR_SECURITY_SERVER + "' " + ss_name + "'")
            return response
        except ApiException as err:
            BaseController.log_api_error('BackupsApi->restore_backup', err)
