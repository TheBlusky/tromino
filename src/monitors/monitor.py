from exceptions import (
    JobAlreadyStarted,
    JobNotStarted,
    InvalidInterval,
    InvalidName,
    InvalidType,
    TooMuchArgument,
)
from mattermost.notify import notify, NOTIFICATION_SUCCESS
from models.monitor import MonitorModel
from monitors.implems import all_monitors
import scheduler


class Monitor:
    monitor_instances = {}

    @classmethod
    async def create(cls, monitor_conf, custom_conf):
        Monitor.validate_monitor_conf(monitor_conf)
        monitor_class = all_monitors[monitor_conf["type"]]
        monitor_class.validate_custom_conf(custom_conf)
        model = await MonitorModel.create(monitor_conf, custom_conf)
        monitor = monitor_class(model)
        Monitor.monitor_instances[monitor_conf["name"]] = monitor
        return monitor

    @classmethod
    async def load_all(cls):
        for model in await MonitorModel.get_all():
            monitor_class = all_monitors[model["monitor_conf"]["type"]]
            monitor = monitor_class(model)
            Monitor.monitor_instances[model["monitor_conf"]["name"]] = monitor
        return Monitor.monitor_instances

    def __init__(self, model):
        self.job = None
        self.model = model

    async def notify(self, data, notification_type=NOTIFICATION_SUCCESS):
        username = (await self.get_monitor_conf())["name"]
        await notify(data, notification_type=notification_type, username=username)

    def get_custom_conf(self):
        return self.model.custom_conf()

    def set_custom_conf(self, conf):
        self.validate_custom_conf(conf)
        self.model.custom_conf(conf)

    async def get_monitor_conf(self):
        return await self.model.monitor_conf()

    async def set_monitor_conf(self, conf):
        self.validate_monitor_conf(conf)
        self.model.monitor_conf(conf)

    @classmethod
    def validate_monitor_conf(cls, conf):
        if (
            "interval" not in conf
            or type(conf["interval"]) is not int
            or conf["interval"] < 0
        ):
            raise InvalidInterval
        if (
            "name" not in conf
            or conf["name"] in Monitor.monitor_instances
            or not conf["name"].isalnum()
        ):
            raise InvalidName
        if "type" not in conf or conf["type"] not in all_monitors:
            raise InvalidType
        if len(conf) > 3:
            raise TooMuchArgument

    async def job_start(self):
        if self.job_is_started():
            raise JobAlreadyStarted
        interval = (await self.get_monitor_conf())["interval"]
        print("interval", interval)
        self.job = scheduler.scheduler.add_job(self.do_job, "interval", seconds=interval)

    def job_stop(self):
        if not self.job_is_started():
            raise JobNotStarted
        self.job.remove()
        self.job = None

    def job_is_started(self):
        return self.job is not None

    async def do_job(self):
        # Todo: log it
        # Todo: try catch
        # Todo: Execution time
        print("GOOOOOOO")
        old_state = (await self.get_monitor_conf())["state"]
        new_state = await self.refresh()
        await self.compare(old_state, new_state)
        await self.set_monitor_conf("state", new_state)

    # To be implemented in implems

    def refresh(self):
        raise NotImplemented

    def compare(self, old_state, new_state):
        raise NotImplemented

    @classmethod
    def validate_custom_conf(cls, conf):
        raise NotImplemented
