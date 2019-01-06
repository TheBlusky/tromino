import asyncio
import logging
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestServer
import scheduler
import server
import mattermost.notify as notify
from exceptions import UnknownNotificationType
from models.monitor import MonitorModel
from models.parameter import ParameterModel
from tests import fake_mattermost_server
from tests.fake_mattermost_server import Notifications


class MattermostTestCase(AioHTTPTestCase):
    async def setUpAsync(self):
        logging.basicConfig(level=logging.ERROR)

    async def get_server(self, app):
        return TestServer(app, scheme="http", host="127.0.0.1", port=8080)

    async def get_application(self):
        app = await server.get_app()
        app.add_routes([web.post("/notify/", fake_mattermost_server.handle_notify)])
        return app

    @unittest_run_loop
    async def test_00_flush(self):
        await ParameterModel.flush()
        await MonitorModel.flush()

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

    @unittest_run_loop
    async def test_03_base_help(self):
        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/not_tromino", "text": f""}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("[Tromino Error]"))

        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f""}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino ["))
        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f"help"}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino ["))
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"do_not_exist"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("Unknown command"))

    @unittest_run_loop
    async def test_04_config(self):
        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f"config"}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino config ["))
        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f"help config"}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino config ["))
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"config do_not_exist"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("Unknown command"))
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"config setup"},
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            (await resp.json())["text"], "Error, need an incomming webhook url"
        )
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"help config setup"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith("`/tromino config setup [")
        )
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"config setup k://NOT_AN_URL"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("something went wrong:"))

        Notifications.read_notifications()  # flush
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

    @unittest_run_loop
    async def test_05_monitor(self):
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"help monitor TOTOTOTO"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith("Unknown command: TOTOTOTO")
        )

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"help monitor"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino monitor ["))

        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f"monitor"}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino monitor ["))

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"help monitor types_list"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith("`/tromino monitor types_list")
        )

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"monitor types_list"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("Monitors types:"))

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"help monitor create_monitor"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith("`/tromino monitor create_monitor")
        )

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"monitor create_monitor dummytest"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith("`/tromino monitor create_monitor")
        )

        # Create scheduler
        scheduler.clean_scheduler()
        scheduler.scheduler = scheduler.create_scheduler()
        scheduler.scheduler.start()

        Notifications.read_notifications()
        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={
                "command": "/tromino",
                "text": f"monitor create_monitor dummytest dummytime 1",
            },
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual((await resp.json())["text"], "Monitor `dummytest` created")

        await asyncio.sleep(5)
        notifications = Notifications.read_notifications()
        self.assertEqual(notifications[0]["text"], "First compare")
        self.assertIn(len(notifications), [4, 5, 6])
        for i in range(1, len(notifications)):
            self.assertTrue(notifications[i]["text"].startswith("Since last refresh"))

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"help monitor mon-dummytest"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino monitor"))

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"monitor mon-XXX"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("Unknown monitor"))

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"monitor mon-dummytest TOTOTO"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("Unknown command: "))

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={
                "command": "/tromino",
                "text": f"monitor mon-dummytest set-channel dummychannel",
            },
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith(
                "Monitor `dummytest` changed channel"
            )
        )
        Notifications.read_notifications()  # Flush
        await asyncio.sleep(5)
        notifications = Notifications.read_notifications()
        self.assertIn(len(notifications), [4, 5, 6])
        for notification in notifications:
            self.assertEqual(notification["channel"], "dummychannel")

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"monitor mon-dummytest set-channel"},
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue(
            (await resp.json())["text"].startswith(
                "Monitor `dummytest` changed channel"
            )
        )
        Notifications.read_notifications()  # Flush
        await asyncio.sleep(5)
        notifications = Notifications.read_notifications()
        self.assertIn(len(notifications), [4, 5, 6])
        for notification in notifications:
            self.assertNotIn("channel", notification)

        resp = await self.client.request(
            "POST",
            "/mattermost/",
            data={"command": "/tromino", "text": f"monitor mon-dummytest remove"},
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual((await resp.json())["text"], "Monitor `dummytest` removed")

        await asyncio.sleep(5)  # Wait for alive job to finish
        Notifications.read_notifications()
        await asyncio.sleep(5)
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)

        # Clean scheduler
        scheduler.clean_scheduler()

    @unittest_run_loop
    async def test_06_status(self):
        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f"help status"}
        )
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())["text"].startswith("`/tromino status"))
        resp = await self.client.request(
            "POST", "/mattermost/", data={"command": "/tromino", "text": f"status"}
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual((await resp.json())["text"], "Status: ok")

    @unittest_run_loop
    async def test_10_notify(self):
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
        await notify.notify("Toto", notification_type=notify.NOTIFICATION_ERROR)
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 1)

        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
        await notify.notify("Toto", notification_type=notify.NOTIFICATION_SUCCESS)
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 1)

        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
        await notify.notify("Toto", notification_type=notify.NOTIFICATION_HELP)
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 1)

        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
        await notify.notify({"text": "Toto"}, notification_type=notify.NOTIFICATION_RAW)
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 1)

        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
        try:
            await notify.notify({"text": "Toto"}, notification_type=-12)
            self.assertTrue(False)  # pragma: no cover
        except UnknownNotificationType:
            pass
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)

        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
        await notify.notify("Toto", overwrite_url=None)
        notifications = Notifications.read_notifications()
        self.assertEqual(len(notifications), 0)
