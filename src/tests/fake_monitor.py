from mattermost.notify import NOTIFICATION_SUCCESS


class FakeMonitor:
    def __init__(self, monitor_conf, custom_conf):
        self.monitor_conf = monitor_conf
        self.custom_conf = custom_conf
        self.notifications = []

    async def notify(self, data, notification_type=NOTIFICATION_SUCCESS):
        self.notifications.append(
            {"data": data, "notification_type": notification_type}
        )

    def notifications_flush(self):
        self.notifications = []

    def notifications_retrieve(self):
        return self.notifications
