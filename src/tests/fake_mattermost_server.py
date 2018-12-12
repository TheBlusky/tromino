from aiohttp import web


class Notifications:
    notifications = []

    @classmethod
    def send_notification(cls, notif):
        Notifications.notifications.append(notif)

    @classmethod
    def read_notifications(cls):
        stock = [n for n in Notifications.notifications]
        Notifications.notifications = []
        return stock


async def handle_notify(request):
    data = await request.json()
    Notifications.send_notification({a: data[a] for a in data})
    return web.json_response({})
