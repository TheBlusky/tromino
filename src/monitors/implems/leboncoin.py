from monitors.utils import monitor_register
from monitors.monitor import Monitor


@monitor_register(name="leboncoin")
class LeboncoinMonitor(Monitor):
    pass
