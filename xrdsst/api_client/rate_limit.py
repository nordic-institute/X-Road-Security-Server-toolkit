import datetime
import logging
import threading
import time

_SS_RATE_LIMIT_SECOND = 20
_SS_RATE_LIMIT_MINUTE = 600
_SS_API_CLIENT_CALLS = {}  # host : { 'calls' : List(datetime), 'lock' : Lock }
_RATELIMITER_LOCK = threading.Lock()


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
