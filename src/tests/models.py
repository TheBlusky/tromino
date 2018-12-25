import asyncio
import inspect
import logging
import unittest
from models.monitor import MonitorModel
from models.parameter import ParameterModel


def async_test(f):
    def wrapper(*args, **kwargs):
        if inspect.iscoroutinefunction(f):
            future = f(*args, **kwargs)
        else:
            coroutine = asyncio.coroutine(f)
            future = coroutine(*args, **kwargs)
        asyncio.get_event_loop().run_until_complete(future)

    return wrapper


class ModelsTestCase(unittest.TestCase):
    loop = None

    def setUp(self):
        logging.basicConfig(level=logging.ERROR)
        if not ModelsTestCase.loop:
            ModelsTestCase.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(ModelsTestCase.loop)

    @async_test
    async def test_00_flush(self):
        await ParameterModel.flush()
        await MonitorModel.flush()

    @async_test
    async def test_01_XXX(self):
        pass
