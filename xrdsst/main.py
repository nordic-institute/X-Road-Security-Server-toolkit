import networkx
import traceback

from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal

from xrdsst.controllers.base import BaseController
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
    GENKEYS_CSRS ="KEYS AND CSR\nGENERATION"
    IMPORT_CERTS ="CERTIFICATE\nIMPORT"


OP_INIT="INIT"
OP_TOKEN_LOGIN="TOKEN\nLOGIN"
OP_TIMESTAMP_ENABLE="TIMESTAMPING"
OP_GENKEYS_CSRS="KEYS AND CSR\nGENERATION"
OP_IMPORT_CERTS="CERTIFICATE\nIMPORT"


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

    ts=list(networkx.topological_sort(graph))
    app.OP_GRAPH = graph
    app.OP_DEPENDENCY_LIST = ts


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
        handlers = [BaseController, TimestampController, TokenController, InitServerController]


class XRDSSTTest(TestApp, XRDSST):
    """A sub-class of XRDSST that is better suited for testing."""

    class Meta:
        label = 'xrdsst'

        exit_on_close = False


def main():
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
