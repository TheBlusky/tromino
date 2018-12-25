from mattermost import helpers
from mattermost.handlers.abstract import AbstractHandler
from monitors.implems import all_monitors
from monitors.monitor import Monitor


class MonitorHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info(
            "`/tromino monitor [ types_list | create_monitor | mon-{name} ]`"
        )

    async def handle_command(self):
        if len(self.command) == 0:
            return await self.handle_help()
        elif self.command[0] == "types_list":
            return await MonitorTypesListHandler(
                self.command[1:], show_help=self.show_help
            ).do_command()
        elif self.command[0] == "create_monitor":
            return await MonitorCreateHandler(
                self.command[1:], show_help=self.show_help
            ).do_command()
        elif self.command[0].startswith("mon-"):
            return await MonitorDetailsHandler(
                [self.command[0][4:]] + self.command[1:], show_help=self.show_help
            ).do_command()
        else:
            return helpers.error(f"Unknown command: {self.command[0]}")


class MonitorTypesListHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info(
            "`/tromino monitor types_list` : Give all monitors plugins installed."
        )

    async def handle_command(self):
        m_list = "\n".join([f"- {m}" for m in all_monitors])
        return helpers.error(f"Monitors types:\n{m_list}")


class MonitorCreateHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info(
            "`/tromino monitor create_monitor {name} {type} {interval] [arg1=value1 arg2=value2...}`"
        )

    async def handle_command(self):
        if len(self.command) < 3:
            return await self.handle_help()
        monitor_conf = {
            "name": self.command[0],
            "type": self.command[1],
            "interval": int(self.command[2]),
        }
        custom_conf = {
            a.split("=")[0]: "=".join(a.split("=")[1:]) for a in self.command[3:]
        }
        monitor = await Monitor.create(monitor_conf, custom_conf)
        await monitor.job_start()
        return helpers.success(f"Monitor `{self.command[0]}` created")


class MonitorDetailsHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info("`/tromino monitor mon-{name} [remove]`")

    async def handle_command(self):
        if self.command[0] not in Monitor.monitor_instances:
            return helpers.error(f"Unknown monitor: {self.command[0]}")
        monitor = Monitor.monitor_instances[self.command[0]]
        if len(self.command) == 1:
            return await self.handle_help()
        elif self.command[1] == "remove":
            await monitor.remove()
            return helpers.success(f"Monitor `{self.command[0]}` removed")
        else:
            return helpers.error(f"Unknown command: {self.command[0]}")
