import asyncio
import inspect
import logging
import os
import unittest

from exceptions import MonitorAlreadyExists, NoSuchMonitor, ParameterAlreadyExists
from models.monitor import MonitorModel
from models.parameter import ParameterModel
from monitors import load_monitors


def async_test(f):
    return lambda *args, **kwargs: asyncio.new_event_loop().run_until_complete(
        f(*args, **kwargs)
        if inspect.iscoroutinefunction(f)
        else asyncio.coroutine(f)(*args, **kwargs)
    )


class MonitorsTestCase(unittest.TestCase):
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

    @async_test
    async def test_02_fun_with_dummy(self):
        pass
