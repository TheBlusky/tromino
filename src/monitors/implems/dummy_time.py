from datetime import datetime

from monitors.utils import monitor_register
from monitors.monitor import Monitor


@monitor_register(name="dummytime")
class DummyTimeMonitor(Monitor):
    def refresh(self):
        return str(datetime.now())

    def compare(self, old_state, new_state):
        old_time = datetime.strptime(old_state, "%Y-%m-%d %H:%M:%S.%f")
        new_time = datetime.strptime(new_state, "%Y-%m-%d %H:%M:%S.%f")
        print(1)
        self.notify(
            f"Since last refresh, {(new_time - old_time).seconds} seconds has passed."
        )

    @classmethod
    def validate_custom_conf(cls, conf):
        pass
