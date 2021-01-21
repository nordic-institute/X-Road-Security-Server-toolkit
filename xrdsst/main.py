import logging
import os
import subprocess
import traceback
import networkx
import yaml
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.token import TokenController

META = init_defaults('output.json', 'output.tabulate')
META['output.json']['overridable'] = True
META['output.tabulate']['overridable'] = True

# Operation dependency graph representation for simple topological ordering
OP_GRAPH = networkx.DiGraph()
OP_DEPENDENCY_LIST = []


# Operations supported and known at the dependency graph level
class OPS:
    INIT = "INIT"
    TOKEN_LOGIN = "TOKEN\nLOGIN"
    TIMESTAMP_ENABLE = "TIMESTAMPING"
    GENKEYS_CSRS = "KEYS AND CSR\nGENERATION"
    IMPORT_CERTS = "CERTIFICATE\nIMPORT"


OP_INIT = "INIT"
OP_TOKEN_LOGIN = "TOKEN\nLOGIN"
OP_TIMESTAMP_ENABLE = "TIMESTAMPING"
OP_GENKEYS_CSRS = "KEYS AND CSR\nGENERATION"
OP_IMPORT_CERTS = "CERTIFICATE\nIMPORT"


# Initialize operational dependency graph for the security server operations
def opdep_init(app):
    graph = OP_GRAPH
    graph.add_node(OPS.GENKEYS_CSRS,
                   controller=TokenController, operation=TokenController.init_keys,
                   configured=False)
    graph.add_node(OPS.TIMESTAMP_ENABLE,
                   controller=TimestampController, operation=TimestampController.init,
                   configured=False)
    graph.add_node(OPS.INIT,
                   controller=InitServerController, operation=InitServerController._default,
                   configured=False)
    graph.add_node(OPS.TOKEN_LOGIN,
                   controller=TokenController, operation=TokenController.login,
                   configured=False)

    graph.add_node(OPS.IMPORT_CERTS)
    graph.add_edge(OPS.INIT, OPS.TOKEN_LOGIN)
    graph.add_edge(OPS.INIT, OPS.TIMESTAMP_ENABLE)
    graph.add_edge(OPS.TOKEN_LOGIN, OPS.GENKEYS_CSRS)
    graph.add_edge(OPS.GENKEYS_CSRS, OPS.IMPORT_CERTS)

    topologically_sorted = list(networkx.topological_sort(graph))
    app.OP_GRAPH = graph
    app.OP_DEPENDENCY_LIST = topologically_sorted


def revoke_api_key(app):
    if len(app.argv) > 1:
        api_key_id = app.Meta.handlers[0].api_key_id
        if api_key_id:
            config_file = app.pargs.configfile if app.pargs.configfile else app.Meta.handlers[0].config_file
            api_key_default = app.Meta.handlers[0].api_key_default
            if not os.path.exists(config_file):
                config_file = os.path.join("..", config_file)
            with open(config_file, "r") as yml_file:
                config = yaml.load(yml_file, Loader=yaml.FullLoader)
            for security_server in config["security_server"]:
                if security_server["api_key"] == api_key_default:
                    log_info('Revoking API key for security server ' + security_server['name'])
                    curl_cmd = "curl -X DELETE -u " + config["api_key"][0]["credentials"] + " --silent " + \
                               config["api_key"][0]["url"] + "/" + str(api_key_id[security_server['name']]) + " -k"
                    cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
                          config["api_key"][0]["key"] + "\" root@" + security_server["name"] + " \"" + curl_cmd + "\""
                    subprocess.run(cmd, shell=True, check=False, capture_output=True)
                    log_info('API key for security server ' + security_server['name'] + ' revoked successfully')


def log_info(message):
    logging.info(message)
    print(message)


class XRDSST(App):
    """X-Road Security Server Toolkit primary application."""

    class Meta:
        label = 'xrdsst'

        hooks = [
            ('pre_setup', opdep_init)
        ]

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = ['yaml', 'json', 'tabulate']

        meta_defaults = META

        # set default output format
        output_handler = 'tabulate'

        # register handlers
        handlers = [BaseController, ClientController, CertController, TimestampController, TokenController, InitServerController]


class XRDSSTTest(TestApp, XRDSST):
    """A sub-class of XRDSST that is better suited for testing."""

    class Meta:
        label = 'xrdsst'

        exit_on_close = False


def main():
    with XRDSST() as app:
        app.hook.register('pre_close', revoke_api_key)
        try:
            app.run()
        except AssertionError as err:
            print('AssertionError > %s' % err.args[0])
            app.exit_code = 1

            if app.debug is True:
                traceback.print_exc()

        except CaughtSignal as err:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % err)
            app.exit_code = 0


if __name__ == '__main__':
    main()
