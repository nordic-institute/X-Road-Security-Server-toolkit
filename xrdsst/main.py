from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal

from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.token import TokenController
from xrdsst.controllers.base import BaseController

META = init_defaults('output.json', 'output.tabulate')
META['output.json']['overridable'] = True
META['output.tabulate']['overridable'] = True


class XRDSST(App):
    """X-Road Security Server Toolkit primary application."""

    class Meta:
        label = 'xrdsst'

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = ['yaml', 'json', 'tabulate']

        meta_defaults = META

        # set default output format
        output_handler = 'tabulate'

        # register handlers
        handlers = [BaseController, InitServerController, TokenController]


class XRDSSTTest(TestApp, XRDSST):
    """A sub-class of XRDSST that is better suited for testing."""

    class Meta:
        label = 'xrdsst'


def main():
    with XRDSST() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
