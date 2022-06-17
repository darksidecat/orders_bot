import asyncio

from pytest import fixture

from app.config import load_config

from .fixtures.db import *
from .fixtures.repo import *


@fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
def config():
    return load_config(env_file=".env.test")
