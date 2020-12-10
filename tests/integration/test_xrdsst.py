
import unittest
import time
import subprocess
import os
import json
import git
import urllib3

from definitions import ROOT_DIR
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest


class TestXRDSST(unittest.TestCase):
    git_repo = 'https://github.com/nordic-institute/X-Road.git'
    local_folder = os.path.join(ROOT_DIR, "tests/integration/X-Road")
    branch_name = 'develop'
    docker_folder = local_folder + '/Docker/securityserver'
    dist = 'bionic-6.25.0'
    image = 'xroad-security-server:' + dist
    url = 'https://localhost:4000/api/v1/api-keys'
    roles = '[\"XROAD_SYSTEM_ADMINISTRATOR\",\"XROAD_SECURITY_OFFICER\"]'
    header = 'Content-Type: application/json'
    file_name = 'api-key.txt'
    max_retries = 100
    curl_retry_wait_seconds = 5

    api_key = None

    @staticmethod
    def single_ss_config():
        configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
        config = {
            'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
            'security-server':
                [{'name': 'ss',
                  'url': 'https://localhost:8000/api/v1',
                  'api_key': 'X-Road-apikey token=a2e9dea1-de53-4ebc-a750-6be6461d91f0',
                  'configuration_anchor': configuration_anchor,
                  'owner_dn_country': 'FI',
                  'owner_dn_org': 'UNSERE',
                  'owner_member_class': 'GOV',
                  'owner_member_code': '1234',
                  'security_server_code': 'SS',
                  'software_token_id': 0,
                  'software_token_pin': '1234'}]}
        return config

    def setUp(self):
        config = self.single_ss_config()
        name = config["security-server"][0]["name"]
        if not os.path.exists('./' + self.local_folder):
            git.Repo.clone_from(self.git_repo, self.local_folder, branch=self.branch_name)
        process = subprocess.run('docker image inspect ' + self.image + ':' + self.dist, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True, check=False)
        if len(process.stderr) > 0:
            subprocess.run('docker build --build-arg DIST=' + self.dist + ' -t ' + self.image + ' .', shell=True,
                           cwd=self.docker_folder, check=False)
        process = subprocess.run("docker top " + name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                 check=False)
        if len(process.stderr) > 0:
            subprocess.run("docker run -p 8000:4000 -p 4001:80 --detach --name " + name + " " + self.image,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False)
        return_code = 1
        retries = 0
        while return_code != 0 and retries <= self.max_retries:
            process = subprocess.run(
                "docker exec " + name + " curl -X POST -u xrd:secret " + self.url + " --data \'" + self.roles
                + "\'" + " --header \"" + self.header + "\" -k >" + self.file_name, shell=True, check=False)
            return_code = process.returncode
            if return_code == 0:
                break
            time.sleep(self.curl_retry_wait_seconds)
            retries += 1
        with open(self.file_name) as json_file:
            data = json.load(json_file)
        assert data["key"] is not None
        self.api_key = data["key"]

    def tearDown(self):
        subprocess.call("rm -rf " + self.local_folder + "/", shell=True)
        subprocess.call("rm " + self.file_name, shell=True)
        subprocess.call("docker ps -a | awk '{ print $1,$2 }' | grep " + self.image +
                        " | awk '{print $1 }' | xargs -I {} docker rm -f {}", shell=True)
        subprocess.call("docker rmi -f $(docker images --format '{{.Repository}}:{{.Tag}}' "
                        "| grep \'" + self.image + "\')", shell=True)

    def step_init(self):
        config = self.single_ss_config()
        config["security-server"][0]["api_key"] = 'X-Road-apikey token=' + self.api_key
        base = BaseController()
        init = InitServerController()
        configuration = base.initialize_basic_config_values(config["security-server"][0])
        status = init.check_init_status(configuration)
        assert status.is_anchor_imported is False
        assert status.is_server_code_initialized is False
        init.initialize_server(config)
        status = init.check_init_status(configuration)
        assert status.is_anchor_imported is True
        assert status.is_server_code_initialized is True

    def step_timestamp_init(self):
        config = self.single_ss_config()
        config["security-server"][0]["api_key"] = 'X-Road-apikey token=' + self.api_key
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            timestamp_controller.load_config = (lambda: config)
            timestamp_controller.init()

    def step_token_login(self):
        config = self.single_ss_config()
        config["security-server"][0]["api_key"] = 'X-Road-apikey token=' + self.api_key
        token_controller = TokenController()
        token_controller.load_config = (lambda: config)
        token_controller.login()

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.step_init()
        self.step_timestamp_init()
        self.step_token_login()
