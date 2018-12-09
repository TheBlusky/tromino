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
    print(f"Command received: {command}")
    info = await BaseHandler(command).do_command()
    return web.Response(**info)


async def run_server():
    app = web.Application()
    app.add_routes([web.post("/mattermost/", handle_mattermost)])
    runner = AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
