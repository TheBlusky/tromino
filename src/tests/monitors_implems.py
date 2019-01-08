import asyncio
import inspect
import logging
import os
import unittest

from models.monitor import MonitorModel
from models.parameter import ParameterModel
from monitors import load_monitors


def new_loop(f):
    asyncio.get_event_loop().stop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return f


def async_test(f):
    return lambda *args, **kwargs: asyncio.new_event_loop().run_until_complete(
        f(*args, **kwargs)
        if inspect.iscoroutinefunction(f)
        else asyncio.coroutine(f)(*args, **kwargs)
    )


class MonitorsImplemsTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.ERROR)

    @async_test
    async def test_00_flush(self):
        await ParameterModel.flush()
        await MonitorModel.flush()

    @async_test
    async def test_01_init(self):
        all_monitors = load_monitors()
        nb_files = len(os.listdir(f"{os.path.dirname(__file__)}/../monitors/implems/"))
        self.assertEqual(len(all_monitors), nb_files - 1)

    @new_loop
    @async_test
    async def test_02(self):
        all_monitors = load_monitors()
        for mon_name in all_monitors:
            await all_monitors[mon_name].test_me(self)
