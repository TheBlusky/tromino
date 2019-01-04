import aiohttp
import json
from exceptions import InvalidCustomConf
from mattermost.notify import NOTIFICATION_RAW, NOTIFICATION_ERROR
from monitors.utils import monitor_register
from monitors.monitor import Monitor
from bs4 import BeautifulSoup


@monitor_register(name="leboncoin")
class LeboncoinMonitor(Monitor):
    async def refresh(self):
        conf = await self.get_custom_conf()
        url = "https://www.leboncoin.fr/recherche/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=1)
        ) as session:
            async with session.get(url, params=conf, headers=headers) as resp:
                if resp.status != 200:
                    await self.notify(
                        "Erreur, impossible de faire une requête leboncoin",
                        notification_type=NOTIFICATION_ERROR,
                    )
                    return []
                html = await resp.read()

        soup = BeautifulSoup(html, "html.parser")
        script_dirty = str(
            [
                script
                for script in soup.find_all("script")
                if "window.FLUX_STATE" in str(script)
            ][0]
        )
        script_post = "=".join(script_dirty.split("=")[1:])
        script_clean = "</script>".join(script_post.split("</script>")[:-1])
        script_json = json.loads(script_clean)
        state = script_json["adSearch"]["data"]["ads"]
        return state

    async def compare(self, old_state, new_state):
        if new_state is None:  # should not happen
            new_state = []
        compared_date = (
            old_state[0]["index_date"] if old_state else "0000-00-00 00:00:00"
        )
        for ad in new_state[::-1]:
            if ad["index_date"] > compared_date:
                image = (
                    ad["images"]["thumb_url"] if "thumb_url" in ad["images"] else None
                )
                price = f'{ad["price"][0]}€' if "price" in ad and ad["price"] else "N/A"
                location = ad["location"]["city_label"]
                subject = ad["subject"]
                url = ad["url"]
                message = {
                    "attachments": [
                        {
                            "title": subject,
                            "title_link": url,
                            "fields": [
                                {"short": True, "title": "Prix", "value": price},
                                {
                                    "short": True,
                                    "title": "Localisation",
                                    "value": location,
                                },
                            ],
                            "image_url": image,
                        }
                    ]
                }
                await self.notify(message, notification_type=NOTIFICATION_RAW)

    @classmethod
    def validate_custom_conf(cls, conf):
        for key in conf:
            if not isinstance(conf[key], str):
                raise InvalidCustomConf
