import subprocess

from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.core.util import get_admin_credentials, get_ssh_key, get_ssh_user
from xrdsst.resources.texts import texts


class UserException(Exception):
    """Exception raised for errors related to UserController.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


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
            if admin_credentials is None:
                raise UserException('UserController->create_user: required admin credentials missing for security server ' + security_server['name'])
            user_name, pwd = admin_credentials.split(":")
            ssh_key = get_ssh_key(security_server, conf)
            if ssh_key is None:
                raise UserException('UserController->create_user: required SSH private key missing for security server ' + security_server['name'])
            ssh_user = get_ssh_user(security_server, conf)
            if ssh_user is None:
                raise UserException('UserController->create_user: required SSH username missing for security server ' + security_server['name'])
            self.add_user_with_groups(self._GROUP_NAMES, user_name, pwd, ssh_key, ssh_user, security_server)
            self.log_info('Admin user \"' + user_name + '\" for security server ' + security_server['name'] +
                          ' created.')

    def add_user_with_groups(self, groups, user_name, pwd, ssh_key, ssh_user, security_server):
        self.log_debug('Adding user \'' + user_name + '\' into groups \'' + str(groups) + '\' for security server: ' + security_server['name'])
        ubuntu_cmd = "sudo adduser --quiet --disabled-password --gecos '' {} --shell /bin/false".format(user_name)
        centos_cmd = "sudo adduser {} -c '' --shell /bin/false".format(user_name)
        cmd = ubuntu_cmd + ' || ' + centos_cmd
        add_user_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
            ssh_key, ssh_user, self.security_server_address(security_server), cmd)
        exitcode, data = subprocess.getstatusoutput(add_user_cmd)
        if exitcode == 0:
            cmd = "echo -e '{}\n{}\n' | sudo passwd {}".format(pwd, pwd, user_name)
            add_user_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
                ssh_key, ssh_user, self.security_server_address(security_server), cmd)
            exitcode, data = subprocess.getstatusoutput(add_user_cmd)
            if exitcode == 0:
                for group in groups:
                    ubuntu_cmd = "sudo adduser {} {}".format(user_name, group)
                    centos_cmd = "sudo usermod -a -G {} {}".format(group, user_name)
                    cmd = ubuntu_cmd + ' || ' + centos_cmd
                    user_mod_cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' \
                                   + '-o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(ssh_key,
                                                                                   ssh_user,
                                                                                   self.security_server_address(security_server),
                                                                                   cmd)
                    exitcode, data = subprocess.getstatusoutput(user_mod_cmd)
                    if exitcode != 0:
                        raise UserException("UserController->create_user: Adding user to group for {0} failed "
                                            "(exit_code = {1}, data = {2})".format(security_server['name'], exitcode, data))
            else:
                raise UserException("UserController->create_user: UserController->create_user: Setting password for the new user for {0} failed "
                                    "(exit_code = {1}, data = {2})".format(security_server['name'], exitcode, data))
        else:
            raise UserException("UserController->create_user: Adding new user for {0} failed "
                                "(exit_code = {1}, data = {2})".format(security_server['name'], exitcode, data))
