import sys

import aiohttp
from exceptions import InvalidCustomConf
import re
from mattermost.notify import NOTIFICATION_ERROR
from monitors.utils import monitor_register
from monitors.monitor import Monitor
from bs4 import BeautifulSoup
from aioresponses import aioresponses


@monitor_register(name="fnac")
class FnacMonitor(Monitor):
    async def refresh(self):
        conf = await self.get_custom_conf()
        url = f"https://fnac.com/a12500548/{conf['product']}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await self.notify(
                        "Error, unable to perform Fnac request",
                        notification_type=NOTIFICATION_ERROR,
                    )
                    return sys.maxsize
                html = await resp.read()
        soup = BeautifulSoup(html, "html.parser")
        div_content = soup.findAll("div", {'class': 'f-priceBox'})[0].text
        price = float(re.sub(r"[^0-9.]", "", div_content.replace("€", ".")))
        return price

    async def compare(self, old_state, new_state):
        conf = await self.get_custom_conf()
        if new_state is None:
            return
        if old_state is None:
            await self.notify(f"https://fnac.com/a12500548/{conf['product']}/ est à {new_state}€")
            return
        if max(old_state - new_state, new_state - old_state) > 1:
            await self.notify(f"https://fnac.com/a12500548/{conf['product']}/ est à {new_state}€")
            return
        await self.notify(f"https://fnac.com/a12500548/{conf['product']}/ est à {new_state}€ (inchangé)")

    @classmethod
    async def validate_custom_conf(cls, conf):
        if len(conf) != 2:
            raise InvalidCustomConf
        if "product" not in conf:
            raise InvalidCustomConf

    @classmethod
    @aioresponses()
    async def test_me(cls, test_case, mocked):
        pass
