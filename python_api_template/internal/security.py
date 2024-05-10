from fastapi import Security
from fastapi.security.api_key import APIKeyHeader

from python_api_template.common.schemas.api_token import TokenModel

from .config.settings import global_settings


def get_token_api_key(
    token_api_key_header: str = Security(
        APIKeyHeader(name="X-API-Key", auto_error=False)
    ),
) -> TokenModel:
    """
    Check and retrieve authentication information from api_key.

    :param token_api_key_header API key provided by Authorization[X-API-Key] header
    :type token_api_key_header: str
    :return: Information attached to provided api_key or None if api_key is
    invalid or does not allow access to called API
    :rtype: TokenModel | None
    """
    valid_tokens = [global_settings.app.test_token, "forbidden"]
    if token_api_key_header not in valid_tokens:
        return TokenModel(sub=None)
    return TokenModel(sub=token_api_key_header)
