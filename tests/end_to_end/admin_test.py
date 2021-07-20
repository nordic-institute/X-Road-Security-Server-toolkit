import os
from xrdsst.controllers.user import UserController


class AdminTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_create_admin_user_fail_admin_credentials_missing(self):
        admin_credentials_env_var = self.test.config["security_server"][0]["admin_credentials"]
        admin_credentials = os.getenv(admin_credentials_env_var, "")
        os.environ[admin_credentials_env_var] = ""
        user = UserController()
        user_created = user.create_user(self.test.config)
        assert user_created is None
        os.environ[admin_credentials_env_var] = admin_credentials

    def step_create_admin_user_fail_ssh_user_missing(self):
        ssh_user_env_var = self.test.config["security_server"][0]["ssh_user"]
        ssh_user = os.getenv(ssh_user_env_var, "")
        os.environ[ssh_user_env_var] = ""
        user = UserController()
        user_created = user.create_user(self.test.config)
        assert user_created is None
        os.environ[ssh_user_env_var] = ssh_user

    def step_create_admin_user_fail_ssh_private_key_missing(self):
        ssh_private_key_env_var = self.test.config["security_server"][0]["ssh_private_key"]
        ssh_private_key = os.getenv(ssh_private_key_env_var, "")
        os.environ[ssh_private_key_env_var] = ""
        user = UserController()
        user_created = user.create_user(self.test.config)
        assert user_created is None
        os.environ[ssh_private_key_env_var] = ssh_private_key

    def step_create_admin_user(self):
        admin_credentials_env_var = self.test.config["security_server"][0]["admin_credentials"]
        old_admin_user = os.getenv(admin_credentials_env_var, "")
        os.environ[admin_credentials_env_var] = 'newxrd:pwd'
        user = UserController()
        user_created = user.create_user(self.test.config)
        assert len(user_created) == 2
        for ssn in range(0, len(self.test.config["security_server"])):
            assert user_created[ssn] is True
        os.environ[admin_credentials_env_var] = old_admin_user

    def test_run_configuration(self):
        self.step_create_admin_user_fail_admin_credentials_missing()
        self.step_create_admin_user_fail_ssh_user_missing()
        self.step_create_admin_user_fail_ssh_private_key_missing()
        self.step_create_admin_user()
