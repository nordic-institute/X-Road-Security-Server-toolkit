from xrdsst.api import TokensApi
from xrdsst.api_client.api_client import ApiClient


def remote_get_token(ss_configuration, security_server):
    token_id = security_server['software_token_id']
    token_api = TokensApi(ApiClient(ss_configuration))
    token = token_api.get_token(token_id)
    return token