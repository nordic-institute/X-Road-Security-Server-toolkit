import atexit
import copy
import functools
import inspect
import json
import re
import sys

import networkx
import os
import logging
import random
import string
import subprocess
import xrdsst
import yaml

from cement import Controller
from cement.utils.version import get_version_banner
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from definitions import ROOT_DIR
from xrdsst.core.conf_keys import validate_conf_keys, ConfKeysSecurityServer, ConfKeysRoot
from xrdsst.core.excplanation import Excplanatory
from xrdsst.core.util import op_node_to_ctr_cmd_text, RE_API_KEY_HEADER, get_admin_credentials, get_ssh_key, get_ssh_user
from xrdsst.core.version import get_version
from xrdsst.resources.texts import texts
from xrdsst.configuration.configuration import Configuration
from xrdsst.rest.rest import ApiException

BANNER = texts['app.description'] + ' ' + get_version() + '\n' + get_version_banner()


class BaseController(Controller):
    _TRANSIENT_API_KEY_ROLES = ['XROAD_SYSTEM_ADMINISTRATOR', 'XROAD_SERVICE_ADMINISTRATOR', 'XROAD_SECURITY_OFFICER', 'XROAD_REGISTRATION_OFFICER']
    _DEFAULT_CONFIG_FILE = "config/xrdsst.yml"
    _RE_API_KEY = re.compile(r"""
        ([a-f0-9]{8}-
        [a-f0-9]{4}-)
        ([a-f0-9]{4})-  # UUID version + 3 hexdecimal digits, only part retained
        ([a-f0-9]{4}-  # Do no validate first character separately
        [a-f0-9]{12})
    """, re.VERBOSE | re.IGNORECASE)

    class Meta:
        label = 'base'
        stacked_on = 'base'
        description = texts['app.description']
        arguments = [
            (['-v', '--version'], {'action': 'version', 'version': BANNER})
        ]

    @staticmethod
    def api_key_scrambler(log_record):
        log_record.msg = re.sub(BaseController._RE_API_KEY, '********-****-\\2-****-************', str(log_record.msg))  # clear ~108 bits from ~120
        return 1

    @staticmethod
    def get_server_status(api_config, ss_config):
        return xrdsst.core.api_util.status_server(api_config, ss_config)  # Allow somewhat sane mocking.

    config_file = os.path.join(ROOT_DIR, _DEFAULT_CONFIG_FILE)
    config = None
    api_key_id = {}

    def _pre_argument_parsing(self):
        parser = self._parser
        # Top level configuration file specification only
        if (issubclass(BaseController, self.__class__)) and issubclass(self.__class__, BaseController):
            parser.add_argument('-c', '--configfile',
                                help=texts['root.parameter.configfile.description'],
                                metavar='file',
                                default=os.path.join(ROOT_DIR, BaseController._DEFAULT_CONFIG_FILE))

    def create_api_key(self, config, roles_list, security_server):
        self.log_debug('Creating API key for security server: ' + security_server['name'])
        roles = list(roles_list)
        admin_credentials = get_admin_credentials(security_server, config)
        ssh_key = get_ssh_key(security_server, config)
        ssh_user = get_ssh_user(security_server, config)
        curl_cmd = "curl -X POST -u " + admin_credentials + " --silent " + \
                   security_server["api_key_url"] + " --data \'" + json.dumps(roles).replace('"', '\\"') + "\'" + \
                   " --header \'Content-Type: application/json\' -k"
        cmd = 'ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "{}" {}@{} "{}"'.format(
            ssh_key, ssh_user, self.security_server_address(security_server), curl_cmd
        )
        if os.path.isfile(ssh_key):
            try:
                exitcode, data = subprocess.getstatusoutput(cmd)
                if exitcode == 0:
                    api_key_json = json.loads(data)
                    self.api_key_id[security_server['name']] = api_key_json["id"], self.security_server_address(security_server)
                    self.log_info('API key \"' + api_key_json["key"] + '\" for security server ' + security_server['name'] +
                                  ' created.')
                    return api_key_json["key"]
                else:
                    self.log_api_error('BaseController->create_api_key:', 'API key creation for security server ' \
                                       + security_server['name'] + ' failed (exit_code =' + str(exitcode) + ', data =' + str(data))
            except Exception as err:
                self.log_api_error('BaseController->create_api_key:', err)
        else:
            raise Exception("SSH private key file does not exists")

    # Returns true if controller is being invoked in autoconfiguration mode.
    def is_autoconfig(self):
        return self.app.auto_apply

    # Returns operation graph node, deduced from call frame at given depth,
    def _op_node(self, depth):
        if not issubclass(self.__class__, BaseController):  # Nothing but error.
            return None

        operation = getattr(self.__class__, inspect.stack()[depth].function)
        g = self.app.OP_GRAPH

        for g_node in g:
            node = g.nodes[g_node]
            if node.get('operation') == operation:
                return g_node

        return None

    # Returns operational dependency chain for caller that is itself controller command.
    # Calling convention: immediately from the controller command function that invoked by Cement.
    def op_path(self):
        if not issubclass(self.__class__, BaseController):  # Nothing but error.
            return None

        op_node = self._op_node(2)
        if not op_node:
            return []

        return networkx.shortest_path(self.app.OP_GRAPH, self.app.OP_DEPENDENCY_LIST[0], op_node)

    # Updates operation graph with server-side /operation statuses/ AND /API config/ for security servers configured.
    def update_op_statuses(self, active_config):
        g = self.app.OP_GRAPH
        for g_node in g:
            node = g.nodes[g_node]
            if node.__contains__('servers'):
                node['servers'].clear()

        for security_server in active_config["security_server"]:
            ssn = security_server['name']
            api_config = self.create_api_config(security_server, active_config)
            status = self.get_server_status(api_config, security_server)

            for g_node in g:
                node = g.nodes[g_node]
                node['servers'][ssn] = {'api_config': api_config, 'status': status}

    # Given active configuration and full operation path to single operation, returns regrouped configuration and
    # the detailed reachability status for those configured servers for which last operation on the path is unreachable.
    def regroup_server_ops(self, active_config, op_full_path):
        self.update_op_statuses(active_config)

        reachable_config = copy.deepcopy(active_config)  # Retains only security servers with reachable end-operation.
        # NB! Depending on server status, these (un)reachable operations will not necessarily be successive.
        reachable_ops = {}
        unreachable_ops = {}
        skipped_servers = []

        for security_server in active_config["security_server"]:
            ssn = security_server['name']
            g_server_node = self.app.OP_GRAPH.nodes[self.app.OP_DEPENDENCY_LIST[0]]['servers'][ssn]
            conn_status = g_server_node['status'].connectivity_status
            reachable_ops[ssn] = []
            unreachable_ops[ssn] = []

            for oop in op_full_path[:-1]:
                performed = self.app.OP_GRAPH.nodes[oop]['is_done'](ssn)
                (reachable_ops if performed else unreachable_ops)[ssn].append(oop)

            if len(unreachable_ops[ssn]) > 0 or not conn_status[0]:
                for rssc in reachable_config["security_server"]:
                    if ssn == rssc['name']:
                        skipped_servers.append(rssc)
                        reachable_config['security_server'].remove(rssc)

        skip_details = {}  # Python 3.6+ retains insertion order, as desired here.
        for skipped_server in skipped_servers:
            skip_details[skipped_server['name']] = {
                'reachable_ops': reachable_ops[skipped_server['name']],
                'unreachable_ops': unreachable_ops[skipped_server['name']]
            }

        return reachable_config, skip_details

    # Given active configuration and full operation path to single operation, returns configuration exclusively with
    # security servers which have valid operation configuration defined.
    def validate_op_config(self, active_config):
        from xrdsst.main import VALIDATORS

        validating_config = copy.deepcopy(active_config)  # Keep security servers with validating operation config only.
        op_node = self._op_node(2)
        op_cmd_text = op_node_to_ctr_cmd_text(self.app.OP_GRAPH, op_node)
        skipped_servers = []
        errors = {}

        for security_server in active_config["security_server"]:
            ssn = security_server['name']
            errors[ssn] = []
            if not VALIDATORS[op_node](security_server, op_cmd_text, errors[ssn]):
                for ss in validating_config["security_server"]:
                    if ssn == ss['name']:
                        skipped_servers.append(ss)
                        validating_config['security_server'].remove(ss)

        skip_details = {}  # Python 3.6+ retains insertion order, as desired here.
        for skipped_server in skipped_servers:
            skip_details[skipped_server['name']] = {
                'errors': errors[skipped_server['name']]
            }

        return validating_config, skip_details

    # Render arguments differ for back-ends, one approach.
    def render(self, render_data):
        if self.is_output_tabulated():
            self.app.render(render_data, headers="firstrow", tablefmt="fancy_grid")
        else:
            self.app.render(render_data)

    def is_output_tabulated(self):
        return self.app.output.Meta.label == 'tabulate'

    def get_api_key(self, conf, security_server):
        # Use API key configured for security server, if valid.
        ss_api_key = security_server.get(ConfKeysSecurityServer.CONF_KEY_API_KEY)
        has_valid_ss_api_key = RE_API_KEY_HEADER.fullmatch(ss_api_key)
        if has_valid_ss_api_key:
            self.log_debug("Using existing API key for security server: '" + security_server['name'] + "'")
            return ss_api_key

        # Use temporary API key, if already created for any operation.
        if self.app.api_keys.get(security_server.get(ConfKeysSecurityServer.CONF_KEY_NAME)):
            return self.app.api_keys[security_server[ConfKeysSecurityServer.CONF_KEY_NAME]]

        # Fallback attempt to create the (temporary) API key, if there seems to be SSH access configured.
        api_key = None
        config = conf if conf else self.config

        if security_server.get(ConfKeysSecurityServer.CONF_KEY_API_KEY):
            try:
                api_key = 'X-Road-apikey token=' + self.create_api_key(config, BaseController._TRANSIENT_API_KEY_ROLES, security_server)
                self.app.api_keys[security_server[ConfKeysSecurityServer.CONF_KEY_NAME]] = api_key
            except Exception as err:
                self.log_api_error('BaseController->get_api_key:', err)

        return api_key

    @staticmethod
    def init_logging(configuration):
        curr_handlers = logging.getLogger().handlers
        if curr_handlers:
            if any(map(lambda h: h.level != logging.NOTSET, curr_handlers)):  # Skip init ONLY if ANY handler levels set.
                return

        exit_messages = ['']
        logging.getLogger().handlers = []

        auto_log_file_name = str(Path.home()) + "/" + texts['app.label'] + "-" + \
                             datetime.now().strftime("%Y%m%d-%H%M-%S") + \
                             '-' + ''.join(random.choice(string.ascii_lowercase) for _ in range(4)) + '.log'

        log_format = "%(asctime)-15s: %(levelname)s - %(message)s"
        log_level = "INFO"
        log_file_name = auto_log_file_name
        auto_log = not configuration.get("logging") or not configuration.get("logging").get("file")
        if configuration.get("logging"):
            log_file_name = configuration["logging"].get("file", log_file_name)
            log_level = configuration["logging"].get("level", log_level)

        try:
            exists = os.path.exists(log_file_name)
            if exists and os.path.isdir(log_file_name):
                raise IsADirectoryError
            # 2nd condition allows for relative log file path spec
            if os.path.exists(os.path.dirname(log_file_name)) or not os.path.dirname(log_file_name):
                logging.basicConfig(filename=log_file_name, level=log_level, format=log_format)
        except IsADirectoryError:
            exit_messages.append("Log configuration referred to directory: '" + log_file_name + "'.")
            log_file_name = auto_log_file_name
            auto_log = True
        except PermissionError:
            exit_messages.append("Was unable to log into '" + log_file_name + "'.")
            log_file_name = auto_log_file_name
            auto_log = True

        if auto_log:
            if not logging.getLogger().handlers:  # auto_log enabled due to errors, needs setting up
                logging.basicConfig(filename=log_file_name, level=log_level, format=log_format)
            exit_messages.append("Activities logged into '" + log_file_name + "'.")
            atexit.register(lambda: print(*exit_messages, sep='\n'))

        for handler in logging.getLogger().handlers:
            handler.addFilter(BaseController.api_key_scrambler)
            handler.setLevel(log_level)

    def load_config(self, baseconfig=None):
        # Add errors to /dict_err_lists/ at given key for /sec_server_configs/ that do not have required /key/ defined.
        def require_conf_key(key, sec_server_configs, dict_err_lists):
            for i in range(0, len(sec_server_configs)):
                if not sec_server_configs[i].get(key) or not sec_server_configs[i][key]:
                    dict_err_lists[key].append(
                        "security_server[" + str(i + 1) + "]" + " missing required '" + key + "' definition."
                    )

        # Add errors to /dict_err_lists/ if /sec_server_configs/ does not have UNIQUE /key/ VALUE for all entries.
        def require_unique_conf_keys(key, sec_server_configs, dict_err_lists):
            values = {x[key] for x in sec_server_configs}
            if len(values) == len(sec_server_configs):
                return

            key_counts = {x: 0 for x in values}
            for x in sec_server_configs:
                key_counts[x[key]] += 1

            duplicates = [x for x in key_counts.keys() if key_counts[x] > 1]
            detected = set()
            for z in range(0, len(sec_server_configs)):
                # Append all duplicated value occurence messages in sequence
                if sec_server_configs[z][key] in duplicates and sec_server_configs[z][key] not in detected:
                    for y in range(0, len(sec_server_configs)):
                        if str(sec_server_configs[z][key]) == str(sec_server_configs[y][key]):
                            dict_err_lists[key].append(
                                ConfKeysRoot.CONF_KEY_ROOT_SERVER + "[" + str(y + 1) + "] '" + key +
                                "' value '" + str(sec_server_configs[y][key]) + "' is non-unique."
                            )
                    detected.add(str(sec_server_configs[z][key]))

        if not baseconfig:
            baseconfig = self.app.pargs.configfile
            self.config_file = baseconfig

        if not os.path.exists(baseconfig):
            self.log_info(texts['message.file.not.found'].format(baseconfig))
            self.app.close(os.EX_CONFIG)
            return None

        try:
            with open(baseconfig, "r") as yml_file:
                self.config = yaml.safe_load(yml_file)
            self.config_file = baseconfig
        except IOError as io_err:
            self.log_info(io_err)
            self.log_info(texts["message.file.unreadable"].format(baseconfig))
            self.app.close(os.EX_CONFIG)
            return None
        except yaml.YAMLError as other_yaml_err:
            self.log_info(texts["message.config.unparsable"].format(other_yaml_err))
            self.app.close(os.EX_CONFIG)
            return None

        # Perform the basic (key-level only) configuration validation.
        if self.config:
            conf_key_errors = validate_conf_keys(self.config)
            for conf_key_error in conf_key_errors:
                padding = (len(conf_key_error[0]) - len(conf_key_error[1]) - 1)
                print(conf_key_error[0], 'NOT AMONG', file=sys.stderr)
                for known_key in sorted(conf_key_error[2]):
                    print(' ' * (len(conf_key_error[1]) + padding + 1), known_key, file=sys.stderr)
                print('', file=sys.stderr)

            if conf_key_errors:
                self.log_info("Invalid configuration keys encountered in '{}'.".format(self.config_file))
                self.app.close(os.EX_CONFIG)
                return None

        # Without server definitions, exit -- can become conditional when/if interactive mode is implemented & enabled.
        if not self.config or not self.config.get(ConfKeysRoot.CONF_KEY_ROOT_SERVER):
            if self.is_output_tabulated():  # Totally ineffectual, do not log.
                print(texts['message.config.serverless'].format(baseconfig), file=sys.stderr)
            self.app.close(os.EX_CONFIG)
            return None

        # Defined security servers HAVE TO have non-empty name and url defined!
        conf_security_servers = self.config[ConfKeysRoot.CONF_KEY_ROOT_SERVER]
        errors = {ConfKeysSecurityServer.CONF_KEY_NAME: [], ConfKeysSecurityServer.CONF_KEY_URL: []}
        require_conf_key(ConfKeysSecurityServer.CONF_KEY_NAME, conf_security_servers, errors)
        require_conf_key(ConfKeysSecurityServer.CONF_KEY_URL, conf_security_servers, errors)

        if errors[ConfKeysSecurityServer.CONF_KEY_NAME] or errors[ConfKeysSecurityServer.CONF_KEY_URL]:
            print(*errors[ConfKeysSecurityServer.CONF_KEY_NAME], sep='\n', file=sys.stderr)
            print(*errors[ConfKeysSecurityServer.CONF_KEY_URL], sep='\n', file=sys.stderr)
            self.app.close(os.EX_CONFIG)
            return None

        # Potential live disaster recipe is when configured security servers' 'name' or 'url' somewhere collude
        # in the provided configuration file. So do the extra check and refuse to run if such situation detected.
        require_unique_conf_keys(ConfKeysSecurityServer.CONF_KEY_NAME, conf_security_servers, errors)
        require_unique_conf_keys(ConfKeysSecurityServer.CONF_KEY_URL, conf_security_servers, errors)

        if errors[ConfKeysSecurityServer.CONF_KEY_NAME] or errors[ConfKeysSecurityServer.CONF_KEY_URL]:
            print(*errors[ConfKeysSecurityServer.CONF_KEY_NAME], sep='\n', file=sys.stderr)
            print(*errors[ConfKeysSecurityServer.CONF_KEY_URL], sep='\n', file=sys.stderr)
            self.app.close(os.EX_CONFIG)
            return None

        return self.config

    def create_api_config(self, security_server, config=None):
        api_key = self.get_api_key(config, security_server)
        if not api_key:
            return None

        api_config = Configuration()
        api_config.api_key['Authorization'] = api_key
        api_config.host = security_server["url"]
        api_config.verify_ssl = False
        return api_config

    # Produces INFO level log and console printout about unconfigured servers details when executing single operation
    # (last operation in given /full_op_path/).
    def log_skipped_op_deps_unmet(self, full_op_path, unconfigured_servers):
        op_text = functools.partial(op_node_to_ctr_cmd_text, self.app.OP_GRAPH)
        for ssn in unconfigured_servers:
            conn_status = self.app.OP_GRAPH.nodes[full_op_path[-1]]['servers'][ssn]['status'].connectivity_status
            if not conn_status[0]:
                skip_msg = texts['message.skipped'].format(ssn) + ": no connectivity ({}).".format(str(conn_status[1]))
                self.log_info(skip_msg)
                continue
            hr_reachable = list(map(op_text, unconfigured_servers[ssn]['reachable_ops']))
            hr_unreachable = list(map(op_text, unconfigured_servers[ssn]['unreachable_ops']))
            skip_msg = \
                texts['message.skipped'].format(ssn) + ":" + \
                ((" has " + str(hr_reachable) + " performed but also") if hr_reachable else '') + \
                " needs " + str(hr_unreachable) + \
                " completion before continuing with requested ['" + op_text(full_op_path[-1]) + "']"
            self.log_info(skip_msg)

    def log_skipped_op_conf_invalid(self, invalid_conf_servers):
        for ssn in invalid_conf_servers.keys():
            skip_msg = \
                texts['message.skipped'].format(ssn) + ":\n" + (' ' * 8) + \
                ("\n" + (' ' * 8)).join(invalid_conf_servers[ssn]['errors'])
            self.log_info(skip_msg)

    @staticmethod
    def log_keyless_servers(ss_api_conf_tuple):
        for security_server, ss_apic in [t for t in ss_api_conf_tuple if t[1] is None]:
            BaseController.log_info(texts['message.server.keyless'].format(security_server['name']))

    @staticmethod
    def log_api_error(msg, exception):
        if issubclass(exception.__class__, ApiException):
            # Ignore the rudimental /msg/
            excplanatory = Excplanatory(exception)
            print(excplanatory.to_multiline_string(), file=sys.stderr)
            return

        # Clueless of root causes.
        logging.error("Exception calling " + msg + ": " + str(exception))
        print("Exception calling " + msg + ": " + str(exception), file=sys.stderr)

    @staticmethod
    def log_info(message):
        logging.info(message)
        print(message)

    @staticmethod
    def log_debug(message):
        logging.debug(message)

    @staticmethod
    def security_server_address(security_server):
        """
        Returns IP/host name of security server, deduced from its configured URL

        :param security_server security server configuration section
        :return: IP/host deduced from security server URL
        """
        return urlparse(security_server['url']).netloc.split(':')[0]  # keep the case, unlike with '.hostname'
