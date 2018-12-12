from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestServer
import server
from tests import fake_mattermost_server
from tests.fake_mattermost_server import Notifications


class MattermostTestCase(AioHTTPTestCase):
    async def get_server(self, app):
        return TestServer(app, scheme="http", host="127.0.0.1", port=8080)

    async def get_application(self):
        app = await server.get_app()
        app.add_routes([web.post("/notify/", fake_mattermost_server.handle_notify)])
        return app

    @unittest_run_loop
    async def test_01_routes(self):
        resp = await self.client.request("GET", "/mattermost/")
        self.assertEqual(resp.status, 405)
        resp = await self.client.request("POST", "/mattermost/")
        self.assertEqual(resp.status, 200)
        resp_json = await resp.json()
        self.assertEqual(resp_json["response_type"], "ephemeral")
        self.assertEqual(resp_json["text"], "[Tromino Error] No command received")

    @unittest_run_loop
    async def test_02_setup(self):
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={
                "command": "/tromino",
                "text": f"config setup http://127.0.0.1:8080/notify/",
            },
        )
        self.assertEqual(resp.status, 200)
        resp_json = await resp.json()
        self.assertEqual(
            resp_json["text"],
            "Tromino just launched some fireworks. If you did see it, it means everything is correctly configured",
        )
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(
            notifications[0]["text"],
            ":fireworks::fireworks::fireworks::fireworks::fireworks:",
        )
