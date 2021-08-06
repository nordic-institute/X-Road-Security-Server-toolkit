from xrdsst.controllers.instance import InstanceController
from xrdsst.main import XRDSSTTest


class InstanceTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def step_instance_list(self):
        list_key_dic = []
        with XRDSSTTest() as app:
            instance_controller = InstanceController()
            instance_controller.app = app
            instance_controller.load_config = (lambda: self.test.config)

            instances = instance_controller.list_instances(self.test.config)
            assert len(instance_controller.app._last_rendered[0]) == (len(self.test.config["security_server"]) + 1)
            assert len(instances) == len(self.test.config["security_server"])

        return list_key_dic

    def test_run_configuration(self):
        self.step_instance_list()
