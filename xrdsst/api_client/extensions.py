# Extra provisions for generated API client. Currently include:
#  * call rate limiter
#  * exception extender

import datetime
import inspect
import logging
import threading
import time

_SS_RATE_LIMIT_SECOND = 20
_SS_RATE_LIMIT_MINUTE = 600
_SS_API_CLIENT_CALLS = {}  # host : { 'calls' : List(datetime), 'lock' : Lock }
_RATELIMITER_LOCK = threading.Lock()

# Delays call to schemed_host if rate limit has been reached.
def limit_rate(schemed_host):
    def _excess_rates(schemed_host):
        calls = _SS_API_CLIENT_CALLS[schemed_host]['calls']

        atm = datetime.datetime.now()
        min_calls = list(filter(lambda dt: (atm - dt) < datetime.timedelta(seconds=60), calls))
        sec_calls = list(filter(lambda dt: (atm - dt) < datetime.timedelta(seconds=1), calls))

        calls.clear()
        calls.extend(min_calls)

        limit_sec_exceeded = len(sec_calls) >= _SS_RATE_LIMIT_SECOND
        limit_min_exceeded = len(min_calls) >= _SS_RATE_LIMIT_MINUTE

        return limit_sec_exceeded, limit_min_exceeded

    with _RATELIMITER_LOCK:
        if not _SS_API_CLIENT_CALLS.get(schemed_host):
            _SS_API_CLIENT_CALLS[schemed_host] = {}
            _SS_API_CLIENT_CALLS[schemed_host]['lock'] = threading.Lock()
            _SS_API_CLIENT_CALLS[schemed_host]['calls'] = []

    with _SS_API_CLIENT_CALLS[schemed_host]['lock']:
        sleep_time = 0
        if any(_excess_rates(schemed_host)):
            time.sleep(1)
            sleep_time += 1

        if sleep_time > 0:
            logging.debug("Rate limit nap of " + str(sleep_time) + " seconds for '" + schemed_host + "'.")

        _SS_API_CLIENT_CALLS[schemed_host]['calls'].append(datetime.datetime.now())


# Extends the traceless ApiException with information available at API call site.
def extended_api_ex(
    api_ex, api_client,
    resource_path, method, path_params=None,
    query_params=None, header_params=None, body=None, post_params=None,
    files=None, response_type=None, auth_settings=None,
    _return_http_data_only=None, collection_formats=None,
    _preload_content=True, _request_timeout=None):

    api_ex.api_call = {
        'method': method,
        'resource_path': resource_path,
        'path_params': path_params,
        'query_params': query_params,
        'header_params': header_params
    }

    # IFF call is made from controller, add the controller -> API call schematic.
    l_cs = inspect.stack()
    len_l_cs = len(l_cs)
    si = 0
    is_controller_module = (lambda x: x.filename.split('/')[-3:-1] == ['xrdsst', 'controllers'])
    while si < len_l_cs and not is_controller_module(l_cs[si]):
        si += 1

    if is_controller_module(l_cs[si]):
        api_ex.api_call['controller_func'] = str(l_cs[si].filename.split('/')[-1]) + "#" + str(l_cs[si].function)
        api_ex.api_call['module_func'] = str(l_cs[si - 1].filename.split('/')[-1]) + "#" + str(l_cs[si - 1].function)

    return api_ex
