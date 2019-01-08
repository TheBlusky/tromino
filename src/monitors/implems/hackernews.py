import aiohttp
from mattermost.notify import NOTIFICATION_RAW, NOTIFICATION_ERROR
from monitors.utils import monitor_register
from monitors.monitor import Monitor
from bs4 import BeautifulSoup


@monitor_register(name="hackernews")
class HackernewsMonitor(Monitor):
    async def refresh(self):
        url = "https://news.ycombinator.com/"
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await self.notify(
                        "Error, unable to perform hackernews request",
                        notification_type=NOTIFICATION_ERROR,
                    )
                    return []
                html = await resp.read()

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all("table", attrs={"class": "itemlist"})[0]
        items = table.find_all("tr", attrs={"class": "athing"})
        state = [
            {
                "subject": item.find("a", attrs={"class": "storylink"}).text,
                "link": item.find("a", attrs={"class": "storylink"})["href"],
                "rank": item.find("span", attrs={"class": "rank"}).text,
                "domain": (
                    item.find("span", attrs={"class": "sitestr"}).text
                    if item.find("span", attrs={"class": "sitestr"})
                    else None
                ),
            }
            for item in items[0:15]
        ]
        return state

    async def compare(self, old_state, new_state):
        if new_state is None:  # should not happen
            new_state = []
        for item in new_state[::-1]:
            if item["link"] not in [old_item["link"] for old_item in old_state]:
                message = {
                    "attachments": [
                        {
                            "title": f"{item['rank']} {item['subject']}",
                            "title_link": item["link"],
                        }
                    ]
                }
                await self.notify(message, notification_type=NOTIFICATION_RAW)

    @classmethod
    def validate_custom_conf(cls, conf):
        pass
