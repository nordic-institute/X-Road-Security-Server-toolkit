import os
import urllib3


from tests.util.test_util import get_client

from xrdsst.main import XRDSSTTest
from xrdsst.core.conf_keys import ConfKeysSecServerClients
from xrdsst.controllers.local_group import LocalGroupController, LocalGroupListMapper


class LocalGroupTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_add_local_group(self):
        with XRDSSTTest() as app:
            local_group_controller = LocalGroupController()
            local_group_controller.app = app
            ssn = 0

            for security_server_conf in self.test.config["security_server"]:
                configuration = local_group_controller.create_api_config(security_server_conf, self.test.config)
                for client_conf in security_server_conf["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client_conf:
                        for local_group_conf in client_conf[ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS]:
                            found_client = get_client(self.test.config, client_conf, ssn)
                            local_group_controller.remote_add_local_group(configuration, security_server_conf,
                                                                          client_conf, local_group_conf)

                            assert len(found_client) > 0
                            client_local_groups = local_group_controller.remote_list_local_groups(configuration, found_client[0]["id"])
                            assert len(client_local_groups) == 1
                        ssn = ssn + 1

    def list_local_groups(self):
        with XRDSSTTest() as app:
            local_group_controller = LocalGroupController()
            local_group_controller.app = app
            ssn = 0
            for security_server_conf in self.test.config["security_server"]:
                configuration = local_group_controller.create_api_config(security_server_conf, self.test.config)
                for client_conf in security_server_conf["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client_conf:
                        found_client = get_client(self.test.config, client_conf, ssn)
                        client_local_groups = local_group_controller.remote_list_local_groups(configuration, found_client[0]["id"])
                        assert len(client_local_groups) == 1
                        for header in LocalGroupListMapper.headers():
                            assert header in local_group_controller.app._last_rendered[0][0]

                        assert len(local_group_controller.app._last_rendered[0]) == 2
                        ssn = ssn + 1

    def step_add_local_group_member(self):
        with XRDSSTTest() as app:
            local_group_controller = LocalGroupController()
            local_group_controller.app = app
            ssn = 0
            for security_server_conf in self.test.config["security_server"]:
                configuration = local_group_controller.create_api_config(security_server_conf, self.test.config)
                for client_conf in security_server_conf["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client_conf:
                        for local_group_conf in client_conf[ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS]:
                            local_group_controller.remote_add_local_group_member(configuration, security_server_conf,
                                                                          client_conf, local_group_conf)

                            found_client = get_client(self.test.config, client_conf, ssn)
                            client_local_groups = local_group_controller.remote_list_local_groups(configuration, found_client[0]["id"])

                            assert len(client_local_groups) == 1
                            assert len(client_local_groups[0].members) == 1
                        ssn = ssn + 1

    def step_delete_local_group_member(self):
        with XRDSSTTest() as app:
            local_group_controller = LocalGroupController()
            local_group_controller.app = app
            ssn = 0
            for security_server_conf in self.test.config["security_server"]:
                configuration = local_group_controller.create_api_config(security_server_conf, self.test.config)
                for client_conf in security_server_conf["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client_conf:
                        for local_group_conf in client_conf[ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS]:

                            found_client = get_client(self.test.config, client_conf, ssn)
                            client_local_groups = local_group_controller.remote_list_local_groups(configuration,
                                                                                                  found_client[0]["id"])
                            assert len(client_local_groups) == 1
                            assert len(client_local_groups[0].members) == 1
                            local_group_ids = [client_local_groups[0].id]
                            local_groups_members_id = client_local_groups[0].members[0].id
                            local_group_controller.remote_delete_local_group_member(configuration, local_group_ids, local_groups_members_id)

                            client_local_groups_after = local_group_controller.remote_list_local_groups(configuration,
                                                                                                  found_client[0]["id"])
                            assert len(client_local_groups_after[0].members) == 0
                        ssn = ssn + 1

    def step_delete_local_group(self):
        with XRDSSTTest() as app:
            local_group_controller = LocalGroupController()
            local_group_controller.app = app
            ssn = 0
            for security_server_conf in self.test.config["security_server"]:
                configuration = local_group_controller.create_api_config(security_server_conf, self.test.config)
                for client_conf in security_server_conf["clients"]:
                    if ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_SUBSYSTEM_CODE in client_conf:
                        for local_group_conf in client_conf[ConfKeysSecServerClients.CONF_KEY_LOCAL_GROUPS]:

                            found_client = get_client(self.test.config, client_conf, ssn)
                            client_local_groups = local_group_controller.remote_list_local_groups(configuration,
                                                                                                  found_client[0]["id"])
                            assert len(client_local_groups) == 1
                            local_group_ids = [client_local_groups[0].id]

                            local_group_controller.remote_delete_local_group(configuration, local_group_ids)

                            client_local_groups_after = local_group_controller.remote_list_local_groups(configuration,
                                                                                                  found_client[0]["id"])
                            assert len(client_local_groups_after) == 0
                        ssn = ssn + 1

    def test_run_configuration(self):
        self.step_add_local_group()
        self.list_local_groups()
        self.step_add_local_group_member()
        self.step_delete_local_group_member()
        self.step_delete_local_group()