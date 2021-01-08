import urllib3

from cement import ex

from xrdsst.api import ClientsApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.models import ClientAdd, Client, ConnectionType
from xrdsst.rest.rest import ApiException
from xrdsst.resources.texts import texts


class ClientController(BaseController):
    class Meta:
        label = 'client'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['client.controller.description']

    @ex(help="Add client subsystem", arguments=[])
    def add(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.add_client(self.load_config())

    def add_client(self, configuration):
        self.init_logging(configuration)
        for security_server in configuration["security_server"]:
            BaseController.log_info('Starting client add process for security server: ' + security_server['name'])
            ss_configuration = self.initialize_basic_config_values(security_server, configuration)
            for client in security_server["clients"]:
                self.remote_add_client(ss_configuration, client)

    @staticmethod
    def remote_add_client(ss_configuration, client_conf):
        conn_type = BaseController.convert_swagger_enum(ConnectionType, client_conf['connection_type'])
        client = Client(member_class=client_conf['member_class'],
                        member_code=client_conf['member_code'],
                        subsystem_code=client_conf['subsystem_code'],
                        connection_type=conn_type)

        client_add = ClientAdd(client=client, ignore_warnings=True)
        clients_api = ClientsApi(ApiClient(ss_configuration))
        try:
            response = clients_api.add_client(body=client_add)
            BaseController.log_info("Added client subsystem " + partial_client_id(client_conf) + " (got full id " + response.id + ")")
        except ApiException as err:
            if err.status == 409:
                BaseController.log_info("Client for '" + partial_client_id(client_conf) + "' already exists.")
            else:
                BaseController.log_api_error('ClientsApi->add_client', err)


def partial_client_id(client_conf):
    return str(client_conf['member_class']) + ":" + \
           str(client_conf['member_code']) + ":" + \
           str(client_conf['subsystem_code'])
