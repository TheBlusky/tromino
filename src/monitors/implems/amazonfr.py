import sys

import aiohttp

from exceptions import InvalidCustomConf
from mattermost.notify import NOTIFICATION_RAW, NOTIFICATION_ERROR
from monitors.utils import monitor_register
from monitors.monitor import Monitor
from bs4 import BeautifulSoup
from aioresponses import aioresponses


@monitor_register(name="amazonfr")
class AmazonFrMonitor(Monitor):
    async def refresh(self):
        conf = await self.get_custom_conf()
        url = f"https://www.amazon.fr/gp/product/{conf['product']}/"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "TE": "Trailers",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await self.notify(
                        "Error, unable to perform leboncoin request",
                        notification_type=NOTIFICATION_ERROR,
                    )
                    return sys.maxsize
                html = await resp.read()
        soup = BeautifulSoup(html, "html.parser")

    async def compare(self, old_state, new_state):
        conf = await self.get_custom_conf()
        if new_state is None:
            return
        if old_state is None:
            return
        if new_state < conf["surveyprice"] < old_state:
            await self.notify(f"https://www.amazon.fr/gp/product/{conf['product']}/ est au prix souhaité !!!")

    @classmethod
    async def validate_custom_conf(cls, conf):
        if len(conf) != 2:
            raise InvalidCustomConf
        if "product" not in conf:
            raise InvalidCustomConf
        if "surveyprice" not in conf:
            raise InvalidCustomConf
        if not conf["surveyprice"].isdigit():
            raise InvalidCustomConf
        url = f"https://www.amazon.fr/gp/product/{conf['product']}/"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "TE": "Trailers",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise InvalidCustomConf

    @classmethod
    @aioresponses()
    async def test_me(cls, test_case, mocked):
        pass
