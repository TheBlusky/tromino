from datetime import datetime

from monitors.utils import monitor_register
from monitors.monitor import Monitor


@monitor_register(name="dummytime")
class DummyTimeMonitor(Monitor):
    async def refresh(self):
        return str(datetime.now())

    async def compare(self, old_state, new_state):
        if old_state is None:
            message = "First compare"
        elif new_state is None:
            message = "No newstate, should not happen !"
        else:
            old_time = datetime.strptime(old_state, "%Y-%m-%d %H:%M:%S.%f")
            new_time = datetime.strptime(new_state, "%Y-%m-%d %H:%M:%S.%f")
            message = f"Since last refresh, {(new_time - old_time).seconds} seconds has passed."
        await self.notify(message)

    @classmethod
    async def validate_custom_conf(cls, conf):
        pass

    @classmethod
    async def test_me(cls, test_case):
        from tests.fake_monitor import FakeMonitor

        class MockedDummyTimeMonitor(FakeMonitor, DummyTimeMonitor):
            pass

        mocked = MockedDummyTimeMonitor({}, {})

        mocked.notifications_flush()
        await mocked.compare(None, None)
        notifications = mocked.notifications_retrieve()
        test_case.assertEqual(len(notifications), 1)
        test_case.assertEqual(notifications[0]["data"], "First compare")

        mocked.notifications_flush()
        await mocked.compare(await mocked.refresh(), None)
        notifications = mocked.notifications_retrieve()
        test_case.assertEqual(len(notifications), 1)
        test_case.assertEqual(
            notifications[0]["data"], "No newstate, should not happen !"
        )

        mocked.notifications_flush()
        some_time = await mocked.refresh()
        await mocked.compare(some_time, some_time)
        notifications = mocked.notifications_retrieve()
        test_case.assertEqual(len(notifications), 1)
        test_case.assertTrue(notifications[0]["data"].startswith("Since last refresh"))

        mocked.notifications_flush()
