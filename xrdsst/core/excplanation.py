# The attempt to provide helpful interpretation for the security server error messages
# originating from proxies. Main inspiration for this is "How to Interpret Security Server
# Proxy Error Messages?" page at https://confluence.niis.org/pages/viewpage.action?pageId=53445058

import functools
import json
import re
from json.decoder import JSONDecodeError

from requests.status_codes import codes

from xrdsst.resources.texts import server_error_map, ascii_art, server_hint_map
from xrdsst.rest.rest import ApiException


# /Explained Exception/, with current implementation revolving around ApiException interpretations.
class Excplanatory:
    def __init__(self, exception):
        self.exc = exception

        # Controller/API call relationship text, API call text or /empty/ when not applicable.
        self.controller_api_call_text = ''

        # The component context string, if applicable (current criteria involves errors from client/server proxies)
        self.component_context_text = ''

        self.explanation = ''  # Educated guess of what is going on.
        self.hints = []  # Possible hints for root cause, solving tips, anything else helpful.

        self._init()

    def _init(self):
        if not issubclass(self.exc.__class__, ApiException):
            return

        api_err_txt, api_call_txt, hints = api_ex_to_messages(self.exc)

        self.controller_api_call_text = api_call_txt
        self.explanation = api_err_txt
        self.hints = hints

        has_proxy_error = api_err_txt.__contains__("Server.ClientProxy") or api_err_txt.__contains__("Server.ServerProxy")

        if has_proxy_error:
            self.component_context_text = ['\n'] + list(map(lambda x: (' ' * 2) + x, ascii_art['message_flow'])) + ['\n']

    def to_multiline_string(self):
        lines = list(filter(
            lambda x: not not x,
            [self.controller_api_call_text, self.explanation, self.component_context_text]
        ))

        if self.hints:
            lines.extend([(' ' * 4) + 'POSSIBLE HINTS', (' ' * 4) + '--------------', self.hints])

        if not lines:
            lines.append(str(self.exc))

        return '\n'.join(map(lambda x: x if isinstance(x, str) else '\n'.join(x), lines))


def http_status_code_to_text(code):
    # There are ordinarily several textual representations given by /requests/.
    # Opt for the longest ones, as shortest ones even include ... emoticons!
    def cmp_texts(x, y):
        return (len(x) + len(re.sub('[a-z]', '', x))) - (len(y) + len(re.sub('[a-z]', '', y)))

    code_texts = sorted(
        list(filter(lambda x: codes[x] == code, codes.__dict__)),
        key=functools.cmp_to_key(cmp_texts),
        reverse=True
    )

    return code_texts[0] if code_texts else ''


def map_api_error(api_ex):
    if not issubclass(api_ex.__class__, ApiException):  # Never happens
        return "Uninterpreted error class '" + str(api_ex.__class__) + "', textual representation " + str(api_ex)

    api_response_status = api_ex.status
    api_response_status_text = http_status_code_to_text(api_response_status)

    if api_ex.body:
        try:
            body_json = json.loads(api_ex.body)
        except JSONDecodeError:
            # SOAP REST/XML responses from service provider without further processing, adapters should convert most.
            return api_ex.body, []

        if body_json.get('error'):
            if body_json.get('error').get('code'):
                # Textual, if present, e.g. {"status":400,"error":{"code":"pin_incorrect"}}'
                error_code = body_json['error']['code']
                # Sometimes provided, e.g. '{"status":500,"error":{"code":"core.MalformedServerConf","metadata":["Server conf is not initialized!"]}'
                error_meta = body_json['error'].get('metadata', '')

                code_meta_eng = (
                    "  {0} ({1}), error_code '{2}'\n".format(api_response_status_text, api_response_status, error_code) +
                    (((' ' * 2) + str(error_meta) + '\n') if error_meta else '') +
                    (((' ' * 2) + server_error_map.get(error_code)) if server_error_map.get(error_code) else '')
                )

                error_hints = server_hint_map.get(error_code, [])

                return code_meta_eng, error_hints

    return '', []


def api_ex_to_messages(exception):
    if not issubclass(exception.__class__, ApiException) or not getattr(exception, 'api_call', None):
        return '', '', []

    mod_call = exception.api_call.get('module_func', '')
    ctr_call = exception.api_call.get('controller_func', '')
    ctr_mod_call = mod_call + ((" <- " + ctr_call) if ctr_call else '')

    api_call_txt = (
        "FAILED\n  {0} {1} @ {2}".format(exception.api_call.get('method'), exception.api_call.get('resource_path'), ctr_mod_call)
    )

    api_err_txt, err_hints = map_api_error(exception)

    return api_err_txt, api_call_txt, err_hints
