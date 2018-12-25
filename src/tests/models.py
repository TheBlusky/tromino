import asyncio
import inspect
import logging
import unittest
from models.monitor import MonitorModel
from models.parameter import ParameterModel


def async_test(f):
    return lambda *args, **kwargs: asyncio.new_event_loop().run_until_complete(
        f(*args, **kwargs)
        if inspect.iscoroutinefunction(f)
        else asyncio.coroutine(f)(*args, **kwargs)
    )


class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.ERROR)

    @async_test
    async def test_00_flush(self):
        await ParameterModel.flush()
        await MonitorModel.flush()

    @async_test
    async def test_01_XXX(self):
        pass
