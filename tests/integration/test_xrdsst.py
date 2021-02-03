import json
import os
import subprocess
import time
import unittest

import docker
import git
import urllib3

from definitions import ROOT_DIR
from tests.util.test_util import get_service_description, find_test_ca_sign_url, perform_test_ca_sign
from tests.util.test_util import get_client, auth_cert_registration_global_configuration_update_received, waitfor
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import StatusController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest


class TestXRDSST(unittest.TestCase):
    configuration_anchor = "tests/resources/configuration-anchor.xml"
    credentials = "xrd:secret"
    git_repo = 'https://github.com/nordic-institute/X-Road.git'
    local_folder = os.path.join(ROOT_DIR, "tests/integration/X-Road")
    branch_name = 'develop'
    docker_folder = local_folder + '/Docker/securityserver'
    image = 'xroad-security-server:latest'
    url = 'https://localhost:4000/api/v1/api-keys'
    roles = '[\"XROAD_SYSTEM_ADMINISTRATOR\",\"XROAD_SERVICE_ADMINISTRATOR\", \"XROAD_SECURITY_OFFICER\", \"XROAD_REGISTRATION_OFFICER\"]'
    header = 'Content-Type: application/json'
    max_retries = 300
    retry_wait = 1  # in seconds
    name = None
    config = None

    def load_config(self):
        self.config = {
            'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
            'api_key': [{'url': self.url,
                         'key': 'key',
                         'roles': json.loads(self.roles)}],
            'security_server':
                [{'name': 'ss',
                  'url': 'https://CONTAINER_HOST:4000/api/v1',
                  'api_key': 'X-Road-apikey token=a2e9dea1-de53-4ebc-a750-6be6461d91f0',
                  'configuration_anchor': os.path.join(ROOT_DIR, self.configuration_anchor),
                  'owner_dn_country': 'EE',
                  'owner_dn_org': 'ORG',
                  'owner_member_class': 'GOV',
                  'owner_member_code': '1234',
                  'security_server_code': 'SS',
                  'software_token_id': 0,
                  'software_token_pin': '1234',
                  'clients': [{
                      'member_class': 'GOV',
                      'member_code': '1234',
                      'subsystem_code': 'BUS',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/modules/openapi-generator-gradle-plugin/samples/local-spec/petstore-v3.0.yaml',
                          'rest_service_code': 'Petstore',
                          'type': 'OPENAPI3'
                      }
                      ]
                  }]
                  }]
        }
        self.name = self.config["security_server"][0]["name"]
        return self.config

    def set_api_key(self, api_key):
        self.config["security_server"][0]["api_key"] = 'X-Road-apikey token=' + api_key

    def set_ip_url(self, ip_address):
        local_url = self.config["security_server"][0]["url"]
        container_ip_url = local_url.replace("CONTAINER_HOST", ip_address)
        self.config["security_server"][0]["url"] = container_ip_url

    def setUp(self):
        self.load_config()
        self.clean_docker()
        self.clone_repo()
        client = docker.from_env()
        self.build_image(client)
        self.run_container(client)

        # Wait for functional networking to be started up, with side effect of configuration update.
        container_ip = ''
        count = 0
        while not container_ip and count < self.max_retries:
            time.sleep(self.retry_wait)
            count += 1
            container_ip = client.containers.list(filters={"name": self.name})[0].attrs['NetworkSettings']['IPAddress']
        if count >= self.max_retries and not container_ip:
            raise Exception("Unable to acquire network address of the container '" + self.name + "'.")

        self.set_ip_url(container_ip)
        self.create_api_key(client)

    def tearDown(self):
        subprocess.call("rm -rf " + self.local_folder + "/", shell=True)
        self.clean_docker()

    def clone_repo(self):
        if not os.path.exists(self.local_folder):
            git.Repo.clone_from(self.git_repo, self.local_folder, branch=self.branch_name)

    def build_image(self, client):
        images = client.images.list(name=self.image)
        if len(images) == 0:
            client.images.build(path=self.docker_folder, tag=self.image)

    def run_container(self, client):
        containers = client.containers.list(filters={"name": self.name})
        if len(containers) == 0:
            client.containers.run(detach=True, name=self.name, image=self.image, ports={'4000/tcp': 8000})
        elif len(containers) == 1:
            if containers[0].status != 'running':
                containers[0].restart()
        else:
            raise Exception("Encountered multiple containers named '" + self.name + "', no action taken.")

    def create_api_key(self, client):
        containers = client.containers.list(filters={"name": self.name})
        for container in containers:
            if container.name == self.name:
                retries = 0
                while retries <= self.max_retries:
                    cmd = "curl -X POST -u " + self.credentials + " --silent " + self.url + " --data \'" + self.roles + \
                          "\'" + " --header \"" + self.header + "\" -k"
                    result = container.exec_run(cmd, stdout=True, stderr=True, demux=False)
                    if len(result.output) > 0:
                        json_data = json.loads(result.output)
                        self.set_api_key(json_data["key"])
                        break
                    time.sleep(self.retry_wait)
                    retries += 1

    def clean_docker(self):
        client = docker.from_env()
        containers = client.containers.list(filters={"name": self.name})
        for container in containers:
            if container.name == self.name:
                subprocess.run("docker rm -f " + self.name, shell=True, check=False)
        images = client.images.list(name=self.image)
        if len(images) != 0:
            client.images.remove(image=self.image, force=True)

    def query_status(self):
        with XRDSSTTest() as app:
            status_controller = StatusController()
            status_controller.app = app
            status_controller.load_config = (lambda: self.config)

            status_controller._default()

            # Must not throw exception, must produce output, test with global status only -- should be ALWAYS present
            # in the configuration that integration test will be run, even when it is still failing as security server
            # has only recently been started up.
            assert status_controller.app._last_rendered[0][1][0].count('LAST') == 1
            assert status_controller.app._last_rendered[0][1][0].count('NEXT') == 1

    def step_init(self):
        base = BaseController()
        init = InitServerController()
        configuration = base.initialize_basic_config_values(self.config["security_server"][0], self.config)
        status = init.check_init_status(configuration)
        assert status.is_anchor_imported is False
        assert status.is_server_code_initialized is False
        init.initialize_server(self.config)
        status = init.check_init_status(configuration)
        assert status.is_anchor_imported is True
        assert status.is_server_code_initialized is True

    def step_timestamp_init(self):
        with XRDSSTTest() as app:
            timestamp_controller = TimestampController()
            timestamp_controller.app = app
            timestamp_controller.load_config = (lambda: self.config)
            timestamp_controller.init()

    def step_token_login(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.config)
        token_controller.login()

    def step_token_init_keys(self):
        token_controller = TokenController()
        token_controller.load_config = (lambda: self.config)
        token_controller.init_keys()

    def step_cert_download_csrs(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            result = cert_controller.download_csrs()
            assert len(result) == 2
            assert result[0].fs_loc != result[1].fs_loc

            return [
                ('sign', next(csr.fs_loc for csr in result if csr.key_type == 'SIGN')),
                ('auth', next(csr.fs_loc for csr in result if csr.key_type == 'AUTH')),
            ]

    def step_acquire_certs(self, downloaded_csrs):
        tca_sign_url = find_test_ca_sign_url(self.config['security_server'][0]['configuration_anchor'])
        cert_files = []
        for down_csr in downloaded_csrs:
            cert = perform_test_ca_sign(tca_sign_url, down_csr[1], down_csr[0])
            cert_file = down_csr[1] + ".signed.pem"
            cert_files.append(cert_file)
            with open(cert_file, "w") as out_cert:
                out_cert.write(cert)

        return cert_files

    def apply_cert_config(self, signed_certs):
        self.config['security_server'][0]['certificates'] = signed_certs

    def step_cert_import(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            cert_controller.import_()

    def step_cert_register(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            cert_controller.register()

    def step_cert_activate(self):
        with XRDSSTTest() as app:
            cert_controller = CertController()
            cert_controller.app = app
            cert_controller.load_config = (lambda: self.config)
            cert_controller.activate()

    def step_subsystem_add_client(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            client_controller.load_config = (lambda: self.config)
            client_controller.add()

    def step_subsystem_register(self):
        with XRDSSTTest() as app:
            client_controller = ClientController()
            client_controller.app = app
            client_controller.load_config = (lambda: self.config)
            client_controller.register()

    def step_add_service_description(self, client_id):
        with XRDSSTTest() as app:
            service_controller = ServiceController()
            service_controller.app = app
            service_controller.load_config = (lambda: self.config)
            service_controller.add_description()
            service_description = get_service_description(self.config, client_id)
            assert service_description["disabled"] is True

    def step_enable_service_description(self, client_id):
        with XRDSSTTest() as app:
            service_controller = ServiceController()
            service_controller.app = app
            service_controller.load_config = (lambda: self.config)
            service_controller.enable_description()
            service_description = get_service_description(self.config, client_id)
            assert service_description["disabled"] is False

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # Uninitialized security server can already have functioning API interface and status query must function
        self.query_status()
        self.step_init()

        self.query_status()
        self.step_timestamp_init()

        self.query_status()
        self.step_token_login()

        self.query_status()
        self.step_token_init_keys()

        self.query_status()

        # certificates
        downloaded_csrs = self.step_cert_download_csrs()
        signed_certs = self.step_acquire_certs(downloaded_csrs)

        self.apply_cert_config(signed_certs)
        self.query_status()

        self.step_cert_import()
        self.query_status()

        self.step_cert_import()
        self.query_status()

        self.step_cert_register()
        self.query_status()

        self.step_cert_activate()
        self.query_status()

        # Wait for global configuration status updates
        waitfor(lambda: auth_cert_registration_global_configuration_update_received(self.config), self.retry_wait, self.max_retries)
        self.query_status()

        # subsystems
        self.step_subsystem_add_client()
        self.query_status()

        self.step_subsystem_register()
        self.query_status()

        client = get_client(self.config)
        client_id = client['id']

        # service descriptions
        self.step_add_service_description(client_id)
        self.query_status()

        self.step_enable_service_description(client_id)
        self.query_status()
