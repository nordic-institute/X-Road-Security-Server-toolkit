from tests.util.test_util import get_client
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.service import ServiceController
from xrdsst.main import XRDSSTTest
from xrdsst.models import ClientStatus


class CleanDeleteTest:

    def __init__(self, end_to_end_tests):
        self.test = end_to_end_tests

    def test_run_configuration(self):
        a=1