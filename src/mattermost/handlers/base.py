from mattermost import helpers
from mattermost.handlers.abstract import AbstractHandler
from mattermost.handlers.config import ConfigHandler
from mattermost.handlers.monitor import MonitorHandler
from mattermost.handlers.status import StatusHandler


class BaseHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.help("`/tromino [status | config | monitoring]`")

    async def handle_command(self):
        if len(self.command) == 0:
            return await self.handle_help()
        elif self.command[0] == "status":
            return await StatusHandler(
                self.command[1:], show_help=self.show_help
            ).do_command()
        elif self.command[0] == "config":
            return await ConfigHandler(
                self.command[1:], show_help=self.show_help
            ).do_command()
        elif self.command[0] == "monitor":
            return await MonitorHandler(
                self.command[1:], show_help=self.show_help
            ).do_command()
        elif self.command[0] == "help":
            return await BaseHandler(self.command[1:], show_help=True).do_command()
        else:
            return helpers.error(f"Unknown command: {self.command[0]}")
