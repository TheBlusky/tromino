import asyncio
import inspect
import logging
import unittest

from exceptions import MonitorAlreadyExists, NoSuchMonitor
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
    async def test_01_monitors(self):
        monitor1 = await MonitorModel.create(
            monitor_conf={"name": "monitor1"}, custom_conf={}
        )
        try:
            await MonitorModel.create(monitor_conf={"name": "monitor1"}, custom_conf={})
            self.assertTrue(False)  # pragma: no cover
        except MonitorAlreadyExists:
            pass
        monitor2 = await MonitorModel.create(
            monitor_conf={"name": "monitor2"}, custom_conf={}
        )
        monitor1_retrieved = await MonitorModel.retrieve("monitor1")
        self.assertCountEqual(
            [(await m.monitor_conf())["name"] for m in (await MonitorModel.get_all())],
            ["monitor1", "monitor2"],
        )

        await monitor1.monitor_conf({"name": "monitor1", "foo": "bar"})
        self.assertEqual((await monitor1_retrieved.monitor_conf())["foo"], "bar")
        self.assertNotIn("foo", await monitor2.monitor_conf())

        await monitor1.custom_conf({"foo": "bar"})
        self.assertEqual((await monitor1_retrieved.custom_conf())["foo"], "bar")
        self.assertNotIn("foo", await monitor2.custom_conf())

        await monitor1.state("foo")
        self.assertEqual(await monitor1_retrieved.state(), "foo")
        self.assertEqual(await monitor2.state(), None)

        await monitor1.remove()
        try:
            await monitor1.monitor_conf()
            self.assertTrue(False)  # pragma: no cover
        except NoSuchMonitor:
            pass
        try:
            await monitor1_retrieved.monitor_conf()
            self.assertTrue(False)  # pragma: no cover
        except NoSuchMonitor:
            pass
        await monitor2.monitor_conf()
        try:
            await monitor1.custom_conf()
            self.assertTrue(False)  # pragma: no cover
        except NoSuchMonitor:
            pass
        try:
            await monitor1_retrieved.custom_conf()
            self.assertTrue(False)  # pragma: no cover
        except NoSuchMonitor:
            pass
        await monitor2.custom_conf()
        try:
            await monitor1.state()
            self.assertTrue(False)  # pragma: no cover
        except NoSuchMonitor:
            pass
        try:
            await monitor1_retrieved.state()
            self.assertTrue(False)  # pragma: no cover
        except NoSuchMonitor:
            pass
        await monitor2.state()
