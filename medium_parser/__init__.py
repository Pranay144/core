# isort: off
from .uncache import uncache

import aiohttp_client_cache

create_cache_key = aiohttp_client_cache.cache_keys.create_key

def custom_key(*args, **kwargs) -> str:
    logger.trace("Using custom implementation of cache key")
    post_id = post_id_correlation.get()
    logger.trace(f"Getting current correlation: {post_id}")
    if post_id == "UNKNOWN_ID":
        logger.trace("Correlation not found, generating new one")
        return create_cache_key(*args, **kwargs)
    return post_id

aiohttp_client_cache.cache_keys.create_key = custom_key
uncache(["aiohttp_client_cache.cache_keys"])
# isort: on
import os
from aiohttp_retry import ExponentialRetry
from contextvars import ContextVar
from typing import Optional

import jinja2
from aiohttp_client_cache import SQLiteBackend
from dotenv import load_dotenv
from loguru import logger

medium_session = SQLiteBackend(
    "medium_cache",
    allowed_methods=("GET", "POST"),
    allowed_codes=(200,),
    include_headers=False,
    expire_after=-1,
    cache_control=False,
)
retry_options = ExponentialRetry(attempts=3)

from . import exceptions as exceptions
from . import exceptions as medium_parser_exceptions

post_id_correlation: ContextVar[Optional[str]] = ContextVar("post_id_correlation", default="UNKNOWN_ID")
jinja_env = jinja2.Environment(enable_async=True)

load_dotenv()

MEDIUM_AUTH_COOKIES = os.getenv("MEDIUM_AUTH_COOKIES")

if not MEDIUM_AUTH_COOKIES:
    for _ in range(10):
        logger.error("No auth cookies for Medium was found. Paywaled content is not available !!! Exit")
        # input("Enter to continue")
    raise ValueError("No auth cookies. Check MEDIUM_AUTH_COOKIES variable")
