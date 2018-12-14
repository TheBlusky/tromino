import logging

from mattermost import helpers
from mattermost.handlers.abstract import AbstractHandler
from mattermost.notify import notify
from models.parameter import ParameterModel


class ConfigHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info("`/tromino config [setup]`")

    async def handle_command(self):
        if len(self.command) == 0:
            return await self.handle_help()
        elif self.command[0] == "setup":
            return await ConfigSetupHandler(
                self.command[1:], show_help=self.show_help
            ).do_command()
        else:
            return helpers.error(f"Unknown command: {self.command[0]}")


class ConfigSetupHandler(AbstractHandler):
    async def handle_help(self):
        return helpers.info(
            "`/tromino config setup [MATTERMOST INCOMING WEBHOOK URL]`: Setup tromino for the first time"
        )

    async def handle_command(self):
        if len(self.command) != 1:
            return helpers.error(f"Error, need an incomming webhook url")
        webhook_url = self.command[0]
        await ParameterModel.retrieve("webhook_url")
        try:
            await notify(
                ":fireworks::fireworks::fireworks::fireworks::fireworks:",
                overwrite_url=webhook_url,
            )
        except Exception as e:
            return helpers.error(f"something went wrong: {type(e)}")
        old_webhook_url = await ParameterModel.retrieve("webhook_url")
        if old_webhook_url:
            await old_webhook_url.change_value(webhook_url)
            logging.warning("WEBHOOK_URL value changed")
        else:
            await ParameterModel.create("webhook_url", webhook_url)
            logging.warning("WEBHOOK_URL value created")
        return helpers.success(
            "Tromino just launched some fireworks. If you did see it, it means everything is correctly configured"
        )
