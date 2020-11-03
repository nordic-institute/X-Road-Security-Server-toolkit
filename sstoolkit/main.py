from cement import App, TestApp
from cement.core.exc import CaughtSignal

from .core.exc import SSToolkitError
from .controllers.base import Base


class SSToolkit(App):
    """Security Server Toolkit primary application."""

    class Meta:
        label = 'sstoolkit'

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
        ]


class SSToolkitTest(TestApp, SSToolkit):
    """A sub-class of SSToolkit that is better suited for testing."""

    class Meta:
        label = 'sstoolkit'


def main():
    with SSToolkit() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except SSToolkitError as e:
            print('SSToolkitError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
