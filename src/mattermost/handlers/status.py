from mattermost import helpers
from mattermost.handlers.abstract import AbstractHandler


class StatusHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info("`/tromino status`: Display server status")

    async def handle_command(self):
        return helpers.success("Status: ok")
