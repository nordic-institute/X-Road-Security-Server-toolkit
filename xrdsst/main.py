import logging
import os
import subprocess
import traceback

import yaml
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal

from xrdsst.controllers.base import BaseController
from xrdsst.controllers.timestamp import TimestampController
from xrdsst.controllers.init import InitServerController
from xrdsst.controllers.token import TokenController

META = init_defaults('output.json', 'output.tabulate')
META['output.json']['overridable'] = True
META['output.tabulate']['overridable'] = True


def revoke_api_key(app):
    if len(app.argv) > 1:
        api_key_id = app.Meta.handlers[0].api_key_id
        if api_key_id:
            config_file = app.Meta.handlers[0].config_file
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
                    process = subprocess.run(cmd, shell=True, check=False, capture_output=True)
                    log_info('API key for security server ' + security_server['name'] + ' revoked successfully')


def log_info(message):
    logging.info(message)
    print(message)


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
        handlers = [BaseController, TimestampController, TokenController, InitServerController]


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

            if app.debug is True:
                traceback.print_exc()

        except CaughtSignal as err:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % err)
            app.exit_code = 0


if __name__ == '__main__':
    main()
