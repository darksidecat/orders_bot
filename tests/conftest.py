import asyncio

from pytest import fixture

from app.config import load_config

from .fixtures.db import *
from .fixtures.repo import *


@fixture(scope="session")
def config():
    return load_config(env_file=".env.test")
