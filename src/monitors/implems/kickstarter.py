from monitors.utils import monitor_register
from monitors.monitor import Monitor


@monitor_register(name="kickstarter")
class KickstarterMonitor(Monitor):
    pass
