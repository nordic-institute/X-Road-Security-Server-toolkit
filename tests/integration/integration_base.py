import json
import os
import subprocess
import time
import unittest

import docker
import git

from xrdsst.core.definitions import ROOT_DIR


# Make less of many evils and use one abstract test class base for encapsulating rather involved Docker setup.
from xrdsst.controllers.base import BaseController


class IntegrationTestBase(unittest.TestCase):
    __test__ = False
    api_key = "a2e9dea1-de53-4ebc-a750-6be6461d91f0"
    api_key_env = "TOOLKIT_API_KEY"
    configuration_anchor = "tests/resources/configuration-anchor.xml"
    credentials = "xrd:secret"
    credentials_env = "TOOLKIT_ADMIN_CREDENTIALS"
    git_repo = 'https://github.com/nordic-institute/X-Road.git'
    local_folder = os.path.join(ROOT_DIR, "tests/integration/X-Road")
    branch_name = 'develop'
    docker_folder = local_folder + '/Docker/securityserver'
    image = 'xroad-security-server:latest'
    url = 'https://localhost:4000/api/v1/api-keys'
    header = 'Content-Type: application/json'
    max_retries = 300
    retry_wait = 1  # in seconds
    name = None
    config = None

    def set_env_variable(self):
        os.environ[self.credentials_env] = self.credentials
        os.environ[self.api_key_env] = self.api_key

    def init_config(self):
        self.config = {
            'admin_credentials': self.credentials_env,
            'logging': {'file': '/var/log/xrdsst_test.log', 'level': 'INFO'},
            'ssh_access': {'user': 'SSH_USER', 'private_key': 'SSH_PRIVATE_KEY'},
            'security_server':
                [{'name': 'ss',
                  'url': 'https://CONTAINER_HOST:4000/api/v1',
                  'fqdn': 'client_only',
                  'api_key': self.api_key_env,
                  'api_key_url': self.url,
                  'configuration_anchor': os.path.join(ROOT_DIR, self.configuration_anchor),
                  'owner_dn_country': 'FI',
                  'owner_dn_org': 'NIIS',
                  'owner_member_class': 'ORG',
                  'owner_member_code': '111',
                  'security_server_code': 'SS',
                  'software_token_id': 0,
                  'software_token_pin': '1234',
                  'clients': [{
                      'member_class': 'ORG',
                      'member_code': '111',
                      'subsystem_code': 'BUS',
                      'connection_type': 'HTTP',
                      'service_descriptions': [{
                          'url': 'https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/modules/openapi-generator-gradle-plugin/samples/local-spec/petstore-v3.0.yaml',
                          'rest_service_code': 'Petstore',
                          'type': 'OPENAPI3',
                          'access': ['DEV:security-server-owners'],
                          'url_all': False,
                          'timeout_all': False,
                          'ssl_auth_all': False,
                          'services': [
                              {
                                  'service_code': 'Petstore',
                                  'access': ['DEV:security-server-owners'],
                                  'timeout': 120,
                                  'ssl_auth': False,
                                  'url': 'http://petstore.xxx'
                              }
                          ],
                          'endpoints': [{
                              'path': '/testPath',
                              'method': 'POST',
                              'access': ['DEV:security-server-owners']
                          }]
                      }]
                  }]
                }]
        }
        self.name = self.config["security_server"][0]["name"]
        return self.config

    def load_config(self):
        return self.config

    def set_api_key(self, api_key):
        os.environ[self.api_key_env] = api_key

    def set_ip_url(self, ip_address):
        local_url = self.config["security_server"][0]["url"]
        container_ip_url = local_url.replace("CONTAINER_HOST", ip_address)
        self.config["security_server"][0]["url"] = container_ip_url

    def setUp(self):
        self.set_env_variable()
        self.init_config()
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
        del os.environ[self.credentials_env]
        del os.environ[self.api_key_env]
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
                    cmd = "curl -X POST -u " + self.credentials + " --silent " + self.url + " --data \'" + json.dumps(BaseController._TRANSIENT_API_KEY_ROLES) + \
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
