import logging
import os
import subprocess
import sys

from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.core.util import get_admin_credentials, get_ssh_key, get_ssh_user
from xrdsst.resources.texts import texts


class UserController(BaseController):
    _GROUP_NAMES = ['xroad-security-officer',
                    'xroad-registration-officer',
                    'xroad-service-administrator',
                    'xroad-system-administrator',
                    'xroad-securityserver-observer']

    class Meta:
        label = 'user'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['user.controller.description']

    @ex(help="Create admin user", arguments=[])
    def create_admin(self):
        self.create_user(self.load_config())

    def create_user(self, conf):
        for security_server in conf["security_server"]:
            self.log_debug('Creating admin user for security server: ' + security_server['name'])
            admin_credentials = get_admin_credentials(security_server, conf)
            user_name, pwd = admin_credentials.split(":")
            ssh_key = get_ssh_key(security_server, conf)
            ssh_user = get_ssh_user(security_server, conf)
            os_name = self.determine_os(ssh_key, ssh_user, security_server)
            self.prepare_os(user_name, os_name, ssh_key, ssh_user, security_server)
            self.add_groups(self._GROUP_NAMES, user_name, ssh_key, ssh_user, security_server)
            self.add_user_with_groups(self._GROUP_NAMES, user_name, pwd, ssh_key, ssh_user, security_server)
            self.log_info('Admin user \"' + user_name + '\" for security server ' + security_server['name'] +
                          ' created.')

    def determine_os(self, ssh_key, ssh_user, security_server):
        self.log_debug('Determining operation system for security server: ' + security_server['name'])
        os_name_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
            ssh_key, ssh_user, self.security_server_address(security_server), "grep '^NAME' /etc/os-release")
        if os.path.isfile(ssh_key):
            try:
                exitcode, data = subprocess.getstatusoutput(os_name_cmd)
                if exitcode == 0:
                    if data.lower().find("ubuntu") >= 0:
                        return "Ubuntu"
                    elif data.lower().find("centos") >= 0:
                        return "Centos"
                    else:
                        return None
                else:
                    self.log_error('UserController->create_user:', 'Determination of operating system for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))
            except Exception as err:
                self.log_error('UserController->create_user:', err)
        else:
            raise Exception("SSH private key file does not exists")

    def prepare_os(self, user_name, os_name, ssh_key, ssh_user, security_server):
        self.log_debug('Operation system for security server \'' + security_server['name'] + '\' is: ' + os_name)
        if os_name == "Centos":
            prepare_os = False
            cmd = "getent passwd \"xroad\""
            check_xroad_user_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                ssh_key, ssh_user, self.security_server_address(security_server), cmd)
            exitcode, data = subprocess.getstatusoutput(check_xroad_user_cmd)
            if exitcode == 0:
                prepare_os = False if len(data) > 0 else True
            else:
                self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                   + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

            if prepare_os:
                self.log_debug(
                    'Performing preparation procedures before adding new user on Centos operation system for security server: ' + security_server['name'])
                cmd = "sudo useradd --system --home /var/lib/xroad --no-create-home --shell /bin/bash --user-group --comment \"X-Road system user\" xroad"
                add_system_user_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), cmd)
                exitcode, data = subprocess.getstatusoutput(add_system_user_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                mkdir_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "mkdir /etc/xroad")
                exitcode, data = subprocess.getstatusoutput(mkdir_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                chown_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "chown xroad:xroad /etc/xroad")
                exitcode, data = subprocess.getstatusoutput(chown_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                chmod_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "chmod 751 /etc/xroad")
                exitcode, data = subprocess.getstatusoutput(chmod_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                touch_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "touch /etc/xroad/db.properties")
                exitcode, data = subprocess.getstatusoutput(touch_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                chown_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "chown xroad:xroad /etc/xroad/db.properties")
                exitcode, data = subprocess.getstatusoutput(chown_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                chmod_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "chmod 640 /etc/xroad/db.properties")
                exitcode, data = subprocess.getstatusoutput(chmod_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                cmd = "sudo groupadd -f {}".format(user_name)
                group_add_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), cmd)
                exitcode, data = subprocess.getstatusoutput(group_add_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                chgrp_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "chgrp shadow /etc/shadow")
                exitcode, data = subprocess.getstatusoutput(chgrp_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                chmod_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "chmod g+r /etc/shadow")
                exitcode, data = subprocess.getstatusoutput(chmod_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

                usermod_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), "usermod -a -G shadow xroad || true")
                exitcode, data = subprocess.getstatusoutput(usermod_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Preparation procedures for adding new user on Centos for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

    def add_groups(self, groups, user_name, ssh_key, ssh_user, security_server):
        self.log_debug('Adding groups \'' + str(groups) + '\' for security server: ' + security_server['name'])
        cmd = "sudo groupadd -f {}".format(user_name)
        add_group_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
            ssh_key, ssh_user, self.security_server_address(security_server), cmd)
        exitcode, data = subprocess.getstatusoutput(add_group_cmd)
        if exitcode != 0:
            self.log_error('UserController->create_user:', 'Adding users own user group for ' \
                               + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))
        for group in groups:
            cmd = "sudo groupadd -f --system {}".format(group)
            add_group_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                ssh_key, ssh_user, self.security_server_address(security_server), cmd)
            exitcode, data = subprocess.getstatusoutput(add_group_cmd)
            if exitcode != 0:
                self.log_error('UserController->create_user:', 'Adding new user groups for ' \
                                   + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

    def add_user_with_groups(self, groups, user_name, pwd, ssh_key, ssh_user, security_server):
        self.log_debug('Adding user \'' + user_name + '\' into groups \'' + str(groups) + '\' for security server: ' + security_server['name'])
        cmd = "sudo useradd {} -g {} -p {}".format(user_name, user_name, pwd)
        add_user_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
            ssh_key, ssh_user, self.security_server_address(security_server), cmd)
        exitcode, data = subprocess.getstatusoutput(add_user_cmd)
        if exitcode == 0:
            for group in groups:
                cmd = "sudo usermod -a -G {} {}".format(group, user_name)
                user_mod_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                    ssh_key, ssh_user, self.security_server_address(security_server), cmd)
                exitcode, data = subprocess.getstatusoutput(user_mod_cmd)
                if exitcode != 0:
                    self.log_error('UserController->create_user:', 'Adding user to group for ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))
        else:
            self.log_error('UserController->create_user:', 'Adding new user for ' \
                               + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))

    @staticmethod
    def log_error(msg, exception):
        logging.error("Exception calling " + msg + ": " + str(exception))
        print("Exception calling " + msg + ": " + str(exception), file=sys.stderr)