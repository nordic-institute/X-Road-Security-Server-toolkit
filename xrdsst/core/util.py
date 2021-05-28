import logging
import os
import subprocess
from xrdsst.core.conf_keys import ConfKeysSecServerClients
import yaml


def get_admin_credentials(security_server, config):
    admin_credentials_env_variable = security_server["admin_credentials"] if security_server.get("admin_credentials", "") else config["admin_credentials"]
    admin_credentials = os.getenv(admin_credentials_env_variable, "")
    return admin_credentials


def get_ssh_key(security_server, config):
    ssh_key_env_variable = security_server["ssh_private_key"] if security_server.get("ssh_private_key", "") else config["ssh_access"]["private_key"]
    ssh_key = os.getenv(ssh_key_env_variable, "")
    return ssh_key


def get_ssh_user(security_server, config):
    ssh_user_env_variable = security_server["ssh_user"] if security_server.get("ssh_user", "") else config["ssh_access"]["user"]
    ssh_user = os.getenv(ssh_user_env_variable, "")
    return ssh_user


# Returns toolkit default AUTHENTICATION key label, given security server configuration
def default_auth_key_label(security_server):
    return security_server['name'] + '-default-auth-key'


# Returns toolkit default SIGNING key label, given security server configuration
def default_sign_key_label(security_server):
    return security_server['name'] + '-default-sign-key'


def default_member_sign_key_label(security_server, client):
    return default_sign_key_label(security_server) + "_" \
           + client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CLASS] + "_" \
           + str(client[ConfKeysSecServerClients.CONF_KEY_SS_CLIENT_MEMBER_CODE])


# Returns human readable controller invocation operation for given operation graph and its named node.
def op_node_to_ctr_cmd_text(g, node_name):
    node = g.nodes[node_name]
    if not node.get('controller'):
        return ''

    ccl = node.get('controller')
    cop = node.get('operation')

    try:
        cop_name = getattr(cop, '__name__')
    except AttributeError:
        # Care for the annoying magic mocks... _extract_mock_name() is only in Python 3.7 apparently.
        cop_name = cop.__dict__['_mock_name']

    ctr_label = ccl.Meta.label
    # Correct with default settings and conventions + saves lot of hassle from AST/inspect.
    op_label = (cop_name.replace('_', '-').rstrip('-') if not cop_name.startswith('_') else '')

    return ctr_label + ((' ' + op_label) if op_label else '')


# Throws SyntaxWarning if /value/ is not among those in Swagger enum definition, returns same value otherwise.
def convert_swagger_enum(_type, value):
    valid_values = list(filter(lambda x: x.isupper(), vars(_type)))
    if value not in valid_values:
        raise SyntaxWarning("value '" + value + "' not in " + str(valid_values))
    return value


# Do fast (or slow :)) connection test for /ss_url/, allowing to set socket timeout, default is set to 1 second.
# Returns tuple (is_connectable: bool, error_msg: str).
def is_ss_connectable(ss_url, sock_timeout=1):
    from socket import SOCK_STREAM, SHUT_RDWR, socket, AF_INET, error
    from urllib.parse import urlparse
    from urllib.error import URLError
    from xrdsst.api_client.extensions import limit_rate

    def has_protocol_host_port(url):
        try:
            result = urlparse(url)
            return (
                    all([result.scheme, result.netloc]) and
                    len(result.netloc.split(':')) == 2 and
                    result.netloc.split(':')[1].isnumeric()
            )
        except URLError:
            return False

    if not has_protocol_host_port(ss_url):  # For security server deployments, port seems pure necessity
        return False, "Unparsable scheme://host:port for '{}'.".format(ss_url)

    url_netloc = urlparse(ss_url).netloc
    parts = url_netloc.split(':')
    host, port = parts[0], int(parts[1])

    limit_rate('/'.join(ss_url.split('/')[:3]))
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(sock_timeout)
        s.connect((host, port))
        s.send("HTTP 1.1 /\n".encode('utf-8'))  # Just enough to get back error
        s.recv(1)
        s.shutdown(SHUT_RDWR)
        s.close()
        return True, ''
    except error as err:
        return False, os.strerror(err.errno) if err.errno else str(err)


def revoke_api_key(app):
    if len(app.argv) > 1:
        api_key_id = app.Meta.handlers[0].api_key_id
        if api_key_id:
            config_file = app.pargs.configfile if app.pargs.configfile else app.Meta.handlers[0].config_file
            if not os.path.exists(config_file):
                config_file = os.path.join("..", config_file)
            with open(config_file, "r") as yml_file:
                config = yaml.safe_load(yml_file)
            for ssn in api_key_id.keys():
                logging.debug('Revoking API key for security server ' + ssn)
                for security_server in config["security_server"]:
                    if ssn == security_server["name"]:
                        credentials = get_admin_credentials(security_server, config)
                        ssh_key = get_ssh_key(security_server, config)
                        ssh_user = get_ssh_user(security_server, config)
                        url = security_server["api_key_url"]
                        curl_cmd = "curl -X DELETE -u " + credentials + " --silent " + url + "/" + str(api_key_id[ssn][0]) + " -k"
                        cmd = "ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i \"" + \
                              ssh_key + "\" " + ssh_user + "@" + api_key_id[ssn][1] + " \"" + curl_cmd + "\""
                        exitcode, data = subprocess.getstatusoutput(cmd)
                        api_key_token = app.api_keys[ssn]
                        if exitcode == 0:
                            log_info("API key '" + api_key_token + "' for security server " + ssn + " revoked.")
                        else:
                            logging.warning("Revocation of API key '" + api_key_token + "' for security server ' + ssn + ' failed")


def log_info(message):
    logging.info(message)
    print(message)
