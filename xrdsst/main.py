import logging
import sys
import traceback
import networkx
import urllib3

from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from typing import Callable
from xrdsst.controllers.auto import AutoController
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.cert import CertController
from xrdsst.controllers.client import ClientController
from xrdsst.controllers.service import ServiceController
from xrdsst.controllers.status import StatusController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.token import TokenController
from xrdsst.controllers.user import UserController
from xrdsst.controllers.endpoint import EndpointController
from xrdsst.core.util import revoke_api_key
from xrdsst.core.validator import validate_config_init, validate_config_timestamp_init, validate_config_token_login, \
    validate_config_token_init_keys, validate_config_cert_import, validate_config_cert_register, validate_config_cert_activate, \
    validate_config_client_add_or_register, validate_config_service_desc, validate_config_service_access, \
    validate_config_service_desc_service, validate_config_service_desc_service_endpoints, \
    validate_config_service_desc_service_endpoints_access
from xrdsst.models import TokenInitStatus, TokenStatus, PossibleAction
from xrdsst.resources.texts import texts

META = init_defaults('output.json', 'output.tabulate')
META['output.json']['overridable'] = True
META['output.tabulate']['overridable'] = True

# Operation dependency graph representation for simple topological ordering
OP_GRAPH = networkx.DiGraph()
OP_DEPENDENCY_LIST = []

OP_INIT = "INIT"
OP_TOKEN_LOGIN = "TOKEN\nLOGIN"
OP_TIMESTAMP_ENABLE = "TIMESTAMPING"
OP_GENKEYS_CSRS = "KEYS AND CSR\nGENERATION"
OP_IMPORT_CERTS = "CERTIFICATE\nIMPORT"
OP_REGISTER_AUTH_CERT = "REGISTER\nAUTH CERT"
OP_ACTIVATE_AUTH_CERT = "ACTIVATE\nAUTH CERT"
OP_ADD_CLIENT = "ADD CLIENT"
OP_REGISTER_CLIENT = "REGISTER CLIENT"
OP_UPDATE_CLIENT = "UPDATE CLIENT"
OP_ADD_SERVICE_DESC = "ADD SERVICE\nDESCRIPTION"
OP_ENABLE_SERVICE_DESC = "ENABLE SERVICE\nDESCRIPTION"
OP_ADD_SERVICE_ACCESS = "ADD SERVICE\nACCESS"
OP_UPDATE_SERVICE = "UPDATE\nSERVICE"
OP_ADD_ENDPOINTS = "ADD\nENDPOINT"
OP_ADD_ENDPOINT_ACCESS = "ADD ENDPOINTS\nACCESS"


# Operations supported and known at the dependency graph level
class OPS:
    INIT = OP_INIT
    TOKEN_LOGIN = OP_TOKEN_LOGIN
    TIMESTAMP_ENABLE = OP_TIMESTAMP_ENABLE
    GENKEYS_CSRS = OP_GENKEYS_CSRS
    IMPORT_CERTS = OP_IMPORT_CERTS
    REGISTER_AUTH_CERT = OP_REGISTER_AUTH_CERT
    ACTIVATE_AUTH_CERT = OP_ACTIVATE_AUTH_CERT
    ADD_CLIENT = OP_ADD_CLIENT
    REGISTER_CLIENT = OP_REGISTER_CLIENT
    UPDATE_CLIENT = OP_UPDATE_CLIENT
    ADD_SERVICE_DESC = OP_ADD_SERVICE_DESC
    ENABLE_SERVICE_DESC = OP_ENABLE_SERVICE_DESC
    ADD_SERVICE_ACCESS = OP_ADD_SERVICE_ACCESS
    UPDATE_SERVICE = OP_UPDATE_SERVICE
    ADD_ENDPOINTS = OP_ADD_ENDPOINTS
    ADD_ENDPOINT_ACCESS = OP_ADD_ENDPOINT_ACCESS


VALIDATORS = {
    OPS.INIT: validate_config_init,
    OPS.TIMESTAMP_ENABLE: validate_config_timestamp_init,
    OPS.TOKEN_LOGIN: validate_config_token_login,
    OPS.GENKEYS_CSRS: validate_config_token_init_keys,
    OPS.IMPORT_CERTS: validate_config_cert_import,
    OPS.REGISTER_AUTH_CERT: validate_config_cert_register,
    OPS.ACTIVATE_AUTH_CERT: validate_config_cert_activate,
    OPS.ADD_CLIENT: validate_config_client_add_or_register,
    OPS.REGISTER_CLIENT: validate_config_client_add_or_register,
    OPS.UPDATE_CLIENT: validate_config_client_add_or_register,
    OPS.ADD_SERVICE_DESC: validate_config_service_desc,
    OPS.ENABLE_SERVICE_DESC: validate_config_service_desc,
    OPS.ADD_SERVICE_ACCESS: validate_config_service_access,
    OPS.UPDATE_SERVICE: validate_config_service_desc_service,
    OPS.ADD_ENDPOINTS: validate_config_service_desc_service_endpoints,
    OPS.ADD_ENDPOINT_ACCESS: validate_config_service_desc_service_endpoints_access
}

# Initialize operational dependency graph for the security server operations
def opdep_init(app):
    def add_op_node(g, op: str, controller, operation: Callable, **kwargs):
        g.add_node(op, controller=controller, operation=operation, servers={}, **kwargs)

    def is_done_initialization(ssn):
        sins = OP_GRAPH.nodes[OPS.INIT]['servers'][ssn]['status'].server_init_status

        return \
            sins.has_anchor and sins.has_server_code and \
            sins.has_server_owner and sins.token_init_status == TokenInitStatus.INITIALIZED

    def is_done_tsa(ssn):
        tsas = OP_GRAPH.nodes[OPS.TIMESTAMP_ENABLE]['servers'][ssn]['status'].timestamping_status
        return tsas and len(tsas) > 0

    def is_done_token_login(ssn):
        tins = OP_GRAPH.nodes[OPS.TOKEN_LOGIN]['servers'][ssn]['status'].token_status
        return tins.logged_in and TokenStatus.OK == tins.status

    def is_done_token_keys_and_csrs(ssn):
        sss = OP_GRAPH.nodes[OPS.GENKEYS_CSRS]['servers'][ssn]['status']

        keys_done = (
                (sss.status_keys.has_toolkit_sign_key and sss.status_keys.has_toolkit_auth_key) or
                (sss.status_keys.has_sign_key and sss.status_keys.has_auth_key)
        )

        csrs_done = (
                (sss.status_csrs.has_toolkit_sign_csr and sss.status_csrs.has_toolkit_auth_csr) or
                (sss.status_certs.has_sign_cert and sss.status_certs.has_auth_cert)
        )

        return keys_done and csrs_done

    def is_done_cert_import(ssn):
        sss = OP_GRAPH.nodes[OPS.IMPORT_CERTS]['servers'][ssn]['status']
        return sss.status_certs.has_sign_cert and sss.status_certs.has_auth_cert

    def is_done_auth_cert_register(ssn):
        sss = OP_GRAPH.nodes[OPS.REGISTER_AUTH_CERT]['servers'][ssn]['status']
        return (
                sss.status_certs.has_auth_cert and
                sss.status_certs.auth_cert_actions and
                PossibleAction.UNREGISTER in sss.status_certs.auth_cert_actions
        )

    def is_done_auth_cert_activate(ssn):
        sss = OP_GRAPH.nodes[OPS.ACTIVATE_AUTH_CERT]['servers'][ssn]['status']
        return (
                sss.status_certs.has_auth_cert and
                sss.status_certs.auth_cert_actions and
                PossibleAction.DISABLE in sss.status_certs.auth_cert_actions
        )

    g = OP_GRAPH

    add_op_node(g, OPS.ACTIVATE_AUTH_CERT, CertController, CertController.activate, is_done=is_done_auth_cert_activate)
    add_op_node(g, OPS.REGISTER_AUTH_CERT, CertController, CertController.register, is_done=is_done_auth_cert_register)
    add_op_node(g, OPS.IMPORT_CERTS, CertController, CertController.import_, is_done=is_done_cert_import)
    add_op_node(g, OPS.GENKEYS_CSRS, TokenController, TokenController.init_keys, is_done=is_done_token_keys_and_csrs)
    add_op_node(g, OPS.TIMESTAMP_ENABLE, TimestampController, TimestampController.init, is_done=is_done_tsa)
    add_op_node(g, OPS.INIT, InitServerController, InitServerController._default, is_done=is_done_initialization)
    add_op_node(g, OPS.TOKEN_LOGIN, TokenController, TokenController.login, is_done=is_done_token_login)
    # End-user operations without binary /done/ criteria.
    add_op_node(g, OPS.ADD_CLIENT, ClientController, ClientController.add, is_done=(lambda ssn: True))
    add_op_node(g, OPS.REGISTER_CLIENT, ClientController, ClientController.register, is_done=(lambda ssn: True))
    add_op_node(g, OPS.UPDATE_CLIENT, ClientController, ClientController.update, is_done=(lambda ssn: True))
    add_op_node(g, OPS.ADD_SERVICE_DESC, ServiceController, ServiceController.add_description, is_done=(lambda ssn: True))
    add_op_node(g, OPS.ENABLE_SERVICE_DESC, ServiceController, ServiceController.enable_description, is_done=(lambda ssn: True))
    add_op_node(g, OPS.ADD_SERVICE_ACCESS, ServiceController, ServiceController.add_access, is_done=(lambda ssn: True))
    add_op_node(g, OPS.UPDATE_SERVICE, ServiceController, ServiceController.update_parameters, is_done=(lambda ssn: True))
    add_op_node(g, OPS.ADD_ENDPOINTS, EndpointController, EndpointController.add, is_done=(lambda ssn: True))
    add_op_node(g, OPS.ADD_ENDPOINT_ACCESS, EndpointController, EndpointController.add_access, is_done=(lambda ssn: True))

    g.add_edge(OPS.REGISTER_AUTH_CERT, OPS.ACTIVATE_AUTH_CERT)
    g.add_edge(OPS.IMPORT_CERTS, OPS.REGISTER_AUTH_CERT)
    g.add_edge(OPS.INIT, OPS.TOKEN_LOGIN)
    g.add_edge(OPS.INIT, OPS.TIMESTAMP_ENABLE)
    g.add_edge(OPS.TOKEN_LOGIN, OPS.GENKEYS_CSRS)
    g.add_edge(OPS.GENKEYS_CSRS, OPS.IMPORT_CERTS)
    g.add_edge(OPS.ACTIVATE_AUTH_CERT, OPS.ADD_CLIENT)
    g.add_edge(OPS.ADD_CLIENT, OPS.REGISTER_CLIENT)
    g.add_edge(OPS.REGISTER_CLIENT, OPS.UPDATE_CLIENT)
    g.add_edge(OPS.ADD_CLIENT, OPS.ADD_SERVICE_DESC)
    g.add_edge(OPS.ADD_SERVICE_DESC, OPS.ENABLE_SERVICE_DESC)
    g.add_edge(OPS.ADD_SERVICE_DESC, OPS.ADD_SERVICE_ACCESS)
    g.add_edge(OPS.ADD_SERVICE_DESC, OPS.UPDATE_SERVICE)
    g.add_edge(OPS.ADD_SERVICE_DESC, OPS.ADD_ENDPOINTS)
    g.add_edge(OPS.ADD_ENDPOINTS, OPS.ADD_ENDPOINT_ACCESS)

    topologically_sorted = list(networkx.topological_sort(g))
    app.OP_GRAPH = g
    app.OP_DEPENDENCY_LIST = topologically_sorted

    # Do not presume autoconfig, activated on explicit invocation.
    app.auto_apply = False


def less_verbose_urllib():
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)  # If not true, then still the only way
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XRDSST(App):
    """X-Road Security Server Toolkit primary application."""

    class Meta:
        label = texts['app.label']

        hooks = [
            ('pre_setup', opdep_init),
            ('pre_setup', lambda app: less_verbose_urllib()),
            ('pre_close', revoke_api_key)
        ]

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = ['yaml', 'json', 'tabulate']

        meta_defaults = META

        # set default output format
        output_handler = 'tabulate'

        # register handlers
        handlers = [BaseController, StatusController, ClientController, CertController, TimestampController,
                    TokenController, InitServerController, AutoController, ServiceController, UserController,
                    EndpointController]

    api_keys = {}  # Keep key references for autoconfiguration and eventual revocation


class XRDSSTTest(TestApp, XRDSST):
    """A sub-class of XRDSST that is better suited for testing."""

    class Meta:
        label = texts['app.label'] + "-test"

        exit_on_close = False

        handlers = XRDSST.Meta.handlers

    api_keys = {}  # Keep key references for autoconfiguration and eventual revocation

def main_excepthook(type_, value, traceback_):
    if type_ == urllib3.exceptions.MaxRetryError:  # Retried traceback lengths otherwise multiple screens.
        url = str(value.reason.pool._protocol) + "://" + str(value.pool.host) + ":" + str(value.pool.port) + value.url
        message = "Could not connect to API endpoint " + url + ", retries exceeded."
        print(message, file=sys.stderr)
    else:
        sys.__excepthook__(type_, value, traceback_)


def main():
    sys.excepthook = main_excepthook

    with XRDSST() as app:
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
