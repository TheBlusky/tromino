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
        print(message)
        await self.notify(message)

    @classmethod
    def validate_custom_conf(cls, conf):
        pass
