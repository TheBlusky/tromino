import aiohttp
import logging

from exceptions import UnknownNotificationType
from mattermost import helpers
from models.parameter import ParameterModel

NOTIFICATION_ERROR = 0
NOTIFICATION_SUCCESS = 1
NOTIFICATION_HELP = 2
NOTIFICATION_RAW = 3


async def notify(
    data,
    notification_type=NOTIFICATION_SUCCESS,
    username=None,
    overwrite_url=False,
    channel=None,
):
    if notification_type == NOTIFICATION_ERROR:
        to_send = helpers.error(data)
    elif notification_type == NOTIFICATION_SUCCESS:
        to_send = helpers.success(data)
    elif notification_type == NOTIFICATION_HELP:
        to_send = helpers.info(data)
    elif notification_type == NOTIFICATION_RAW:
        to_send = data
    else:
        raise UnknownNotificationType
    if username:
        to_send["username"] = username
    url = None
    if overwrite_url is not False:
        url = overwrite_url
    else:
        webhook_url_parameter = await ParameterModel.retrieve("webhook_url")
        if webhook_url_parameter:
            url = webhook_url_parameter.value
    if not url:
        logging.warning(
            "Unconfigure webhook, please add a slash command and use `/tromino config setup `WEBHOOK URL`"
        )
        return
    if channel:
        to_send = {**to_send, "channel": channel}
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.post(url, json=to_send) as resp:
            if resp.status != 200:  # pragma: no cover
                logging.warning(
                    f"Notification sent, but response status code is {resp.status}"
                )
