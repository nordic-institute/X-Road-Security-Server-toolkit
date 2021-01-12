import unittest
import time
import subprocess
import os
import json
import git
import docker
import requests
import urllib3

from definitions import ROOT_DIR
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.token import TokenController
from xrdsst.main import XRDSSTTest

# Returns TEST CA signed certificate in PEM format.
def perform_test_ca_sign(test_ca_sign_url, certfile_loc, type):
    certfile = open(certfile_loc, "rb")  # opening for [r]eading as [b]inary
    cert_data = certfile.read()
    certfile.close()

    response = requests.post(
        test_ca_sign_url,
        {'type': type},
        files={
            'certreq': (os.path.basename(certfile_loc), cert_data, 'application/x-x509-ca-cert')
        }
    )

    # Test CA returns plain PEMs only
    return response.content.decode("ascii")

# Deduce possible TEST CA URL from configuration anchor
def find_test_ca_sign_url(conf_anchor_file_loc):
    prefix = "/testca"
    port = 8888
    suffix = "/sign"
    with open(conf_anchor_file_loc, 'r') as anchor_file:
        xml_fragment = list(filter(lambda s: s.count('downloadURL>') == 2, anchor_file.readlines())).pop()
        internal_conf_url = xml_fragment.replace("<downloadURL>", "").replace("</downloadURL>", "").strip()
        from urllib.parse import urlparse
        parsed_url = urlparse(internal_conf_url)
        host = parsed_url.netloc.split(':')[0]
        protocol = parsed_url.scheme
        return protocol + "://" + host + ":" + str(port) + prefix + suffix


class TestXRDSST(unittest.TestCase):

    configuration_anchor = "tests/resources/configuration-anchor.xml"
    credentials = "xrd:secret"
    git_repo = 'https://github.com/nordic-institute/X-Road.git'
    local_folder = os.path.join(ROOT_DIR, "tests/integration/X-Road")
    branch_name = 'develop'
    docker_folder = local_folder + '/Docker/securityserver'
    image = 'xroad-security-server:latest'
    url = 'https://localhost:4000/api/v1/api-keys'
    roles = '[\"XROAD_SYSTEM_ADMINISTRATOR\",\"XROAD_SECURITY_OFFICER\"]'
    header = 'Content-Type: application/json'
    max_retries = 60
    curl_retry_wait_seconds = 5
    name = None
    config = None

    def load_config(self):
        self.config = {
            'logging': [{'file': '/var/log/xrdsst_test.log', 'level': 'INFO'}],
            'api_key': [{'url': self.url,
                         'key': 'key',
                         'roles': 'XROAD_SYSTEM_ADMINISTRATOR'}],
            'security_server':
                [{'name': 'ss',
                  'url': 'https://localhost:8000/api/v1',
                  'api_key': 'X-Road-apikey token=a2e9dea1-de53-4ebc-a750-6be6461d91f0',
                  'configuration_anchor': os.path.join(ROOT_DIR, self.configuration_anchor),
                  'owner_dn_country': 'EE',
                  'owner_dn_org': 'ORG',
                  'owner_member_class': 'GOV',
                  'owner_member_code': '1234',
                  'security_server_code': 'SS',
                  'software_token_id': 0,
                  'software_token_pin': '1234'}]}
        self.name = self.config["security_server"][0]["name"]
        return self.config

    def set_api_key(self, api_key):
        self.config["security_server"][0]["api_key"] = 'X-Road-apikey token=' + api_key

    def setUp(self):
        self.load_config()
        self.clean_docker()
        self.clone_repo()
        client = docker.from_env()
        self.build_image(client)
        self.run_container(client)
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
        else:
            for container in containers:
                if container.status != 'running':
                    container.restart()

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
                    time.sleep(self.curl_retry_wait_seconds)
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

    def apply_subsystem_config(self):
        clients = [{
            'member_class': 'GOV',
            'member_code': '1234',
            'subsystem_code': 'BUS',
            'connection_type': 'HTTP'
        }]
        self.config['security_server'][0]['clients'] = clients

    def step_subsystem_add(self):
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

    def test_run_configuration(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.step_init()
        self.step_timestamp_init()
        self.step_token_login()
        self.step_token_init_keys()

        # certificates
        downloaded_csrs = self.step_cert_download_csrs()
        signed_certs = self.step_acquire_certs(downloaded_csrs)
        self.apply_cert_config(signed_certs)
        self.step_cert_import()
        self.step_cert_register()
        self.step_cert_activate()

        # subsystems
        self.apply_subsystem_config()
        self.step_subsystem_add()
        self.step_subsystem_register()
