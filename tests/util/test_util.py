import json
import os
import time
from urllib.parse import urlparse
import requests
from xrdsst.controllers.base import BaseController
from xrdsst.models import ConnectionType

# Waits until boolean function returns True within number of retried delays or raises error
def waitfor(boolf, delay, retries):
    count = 0
    while count < retries and not boolf():
        time.sleep(delay)
        count += 1

    if count >= retries:
        raise Exception("Exceeded retry count " + str(retries) + " with delay " + str(delay) + "s.")


# Returns TEST CA signed certificate in PEM format.
def perform_test_ca_sign(test_ca_sign_url, certfile_loc, _type):
    certfile = open(certfile_loc, "rb")  # opening for [r]eading as [b]inary
    cert_data = certfile.read()
    certfile.close()

    response = requests.post(
        test_ca_sign_url,
        {'type': _type},
        files={
            'certreq': (os.path.basename(certfile_loc), cert_data, 'application/x-x509-ca-cert')
        }
    )

    # Test CA returns plain PEMs only
    return response.content.decode("ascii")


# Returns service descriptions for given client
def get_service_description(config, client_id):
    service_description = requests.get(
        config["security_server"][0]["url"] + "/clients/" + client_id + "/service-descriptions",
        None,
        headers={'Authorization': config["security_server"][0]["api_key"], 'accept': 'application/json'},
        verify=False)
    service_description_json = json.loads(str(service_description.content, 'utf-8').strip())
    return service_description_json[0]


# Returns client
def get_client(config):
    conn_type = BaseController.convert_swagger_enum(ConnectionType, config['security_server'][0]['clients'][0]['connection_type'])
    member_class = config['security_server'][0]['clients'][0]['member_class']
    member_code = config['security_server'][0]['clients'][0]['member_code']
    subsystem_code = config['security_server'][0]['clients'][0]['subsystem_code']
    client = requests.get(
        config["security_server"][0]["url"] + "/clients",
        {'member_class': member_class,
         'member_code': member_code,
         'subsystem_code': subsystem_code,
         'connection_type': conn_type},
        headers={'Authorization': config["security_server"][0]["api_key"], 'accept': 'application/json'},
        verify=False)
    client_json = json.loads(str(client.content, 'utf-8').strip())
    return client_json[0]


# Deduce possible TEST CA URL from configuration anchor
def find_test_ca_sign_url(conf_anchor_file_loc):
    prefix = "/testca"
    port = 8888
    suffix = "/sign"
    with open(conf_anchor_file_loc, 'r') as anchor_file:
        xml_fragment = list(filter(lambda s: s.count('downloadURL>') == 2, anchor_file.readlines())).pop()
        internal_conf_url = xml_fragment.replace("<downloadURL>", "").replace("</downloadURL>", "").strip()
        parsed_url = urlparse(internal_conf_url)
        host = parsed_url.netloc.split(':')[0]
        protocol = parsed_url.scheme
        return protocol + "://" + host + ":" + str(port) + prefix + suffix


# Check for auth cert registration update receival
def auth_cert_registration_global_configuration_update_received(config):
    def registered_auth_key(key):
        return BaseController.default_auth_key_label(config["security_server"][0]) == key['label'] and \
               'REGISTERED' == key['certificates'][0]['status']

    result = requests.get(
        config["security_server"][0]["url"] + "/tokens/" + str(config["security_server"][0]['software_token_id']),
        None,
        headers={
            'Authorization': config["security_server"][0]["api_key"],
            'accept': 'application/json'
        },
        verify=False
    )

    if result.status_code != 200:
        raise Exception("Failed registration status check, status " + str(result.status_code) + ": " + str(result.reason))

    response = json.loads(result.content)
    registered_auth_keys = list(filter(registered_auth_key, response['keys']))
    return True if registered_auth_keys else False
