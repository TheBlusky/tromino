class AbstractHandler:
    def __init__(self, command, show_help=False, extras={}):
        self.command = command
        self.show_help = show_help
        self.extras = extras

    async def handle_help(self):  # pragma: no cover
        raise NotImplemented

    async def handle_command(self):  # pragma: no cover
        raise NotImplemented

    async def do_command(self):
        if len(self.command) == 0 and self.show_help:
            return await self.handle_help()
        return await self.handle_command()
