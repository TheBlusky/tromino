import asyncio
import inspect
import logging
import os
import unittest

from exceptions import (
    InvalidInterval,
    InvalidName,
    InvalidType,
    TooMuchArgument,
    JobAlreadyStarted,
    JobNotStarted,
)
from models.monitor import MonitorModel
from models.parameter import ParameterModel
from monitors import load_monitors
from monitors.monitor import Monitor


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

    @new_loop
    @async_test
    async def test_02_fun_with_dummy(self):
        monitors = await Monitor.load_all()
        self.assertEqual(len(monitors), 0)
        dummy_1 = await Monitor.create(
            {"name": "dummy1", "type": "dummytime", "interval": 1}, {"foo": "bar"}
        )
        self.assertEqual((await dummy_1.get_custom_conf())["foo"], "bar")
        await dummy_1.set_custom_conf({"foo": "baz"})
        self.assertEqual((await dummy_1.get_custom_conf())["foo"], "baz")
        try:
            await Monitor.create(
                {"name": "dummy2", "type": "dummytime", "interval": "1"}, {"foo": "bar"}
            )
            self.assertTrue(False)  # pragma: no cover
        except InvalidInterval:
            pass
        try:
            await Monitor.create(
                {"name": "dummy_2", "type": "dummytime", "interval": 1}, {"foo": "bar"}
            )
            self.assertTrue(False)  # pragma: no cover
        except InvalidName:
            pass
        try:
            await Monitor.create(
                {"name": "dummy2", "type": "no_type", "interval": 1}, {"foo": "bar"}
            )
            self.assertTrue(False)  # pragma: no cover
        except InvalidType:
            pass
        try:
            await Monitor.create(
                {
                    "name": "dummy2",
                    "type": "dummytime",
                    "interval": 1,
                    "dummy": "dummy",
                },
                {"foo": "bar"},
            )
            self.assertTrue(False)  # pragma: no cover
        except TooMuchArgument:
            pass
        await dummy_1.job_start()
        try:
            await dummy_1.job_start()
            self.assertTrue(False)  # pragma: no cover
        except JobAlreadyStarted:
            pass
        dummy_1.job_stop()
        try:
            dummy_1.job_stop()
            self.assertTrue(False)  # pragma: no cover
        except JobNotStarted:
            pass

    @new_loop
    @async_test
    async def test_03_retrieval(self):
        Monitor.monitor_instances = {}
        monitors = await Monitor.load_all()
        self.assertEqual(len(monitors), 1)
        dummy_1 = monitors["dummy1"]
        await dummy_1.remove()
        Monitor.monitor_instances = {}
        monitors = await Monitor.load_all()
        self.assertEqual(len(monitors), 0)
