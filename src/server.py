import shlex

from aiohttp import web
from aiohttp.web_runner import AppRunner
from mattermost.handlers.base import BaseHandler


async def handle_mattermost(request):
    data = await request.post()
    if "command" not in data:
        return web.json_response(
            {
                "response_type": "ephemeral",
                "text": "[Tromino Error] No command received",
            }
        )
    if data["command"] != "/tromino":
        return web.json_response(
            {
                "response_type": "ephemeral",
                "text": "[Tromino Error] Slash command should be `/tromino`",
            }
        )
    command = shlex.split(data["text"])
    info = await BaseHandler(command).do_command()
    return web.json_response(info)


async def get_app():
    app = web.Application()
    app.add_routes([web.post("/mattermost/", handle_mattermost)])
    return app


async def run_server():  # pragma: no cover
    runner = AppRunner(await get_app())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
