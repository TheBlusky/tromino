import aiohttp
import re
from bs4 import BeautifulSoup

from exceptions import InvalidCustomConf
from mattermost.notify import NOTIFICATION_RAW, NOTIFICATION_ERROR
from monitors.utils import monitor_register
from monitors.monitor import Monitor


@monitor_register(name="kickstarter")
class KickstarterMonitor(Monitor):
    async def refresh(self):
        conf = await self.get_custom_conf()
        url = f"https://www.kickstarter.com/projects/{conf['project']}/"
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await self.notify(
                        "Error, unable to perform kickstarter request",
                        notification_type=NOTIFICATION_ERROR,
                    )
                    return []
                html = await resp.read()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("title").text
        updates = int(
            soup.find("a", attrs={"data-content": "updates"}).find("span").text
        )
        comments = int(
            soup.find("data", attrs={"itemprop": "Project[comments_count]"})[
                "data-value"
            ]
        )
        faqs = int(soup.find("a", attrs={"data-content": "faqs"}).find("span").text)
        money_text = soup.find("span", attrs={"class": "money"}).text
        money = int(re.sub("[^0-9]", "", money_text))
        unit = re.sub("[0-9, ]", "", money_text)
        image = soup.find("meta", attrs={"property": "og:image"})["content"]
        state = {
            "title": title,
            "updates": updates,
            "comments": comments,
            "faqs": faqs,
            "money": money,
            "unit": unit,
            "image": image,
        }
        return state

    async def compare(self, old_state, new_state):
        if old_state is None:
            old_state = {
                "title": "",
                "updates": 0,
                "comments": 0,
                "faqs": 0,
                "money": 0,
                "unit": "",
                "image": "",
            }
        if new_state is None:  # should not happen
            new_state = {
                "title": "",
                "updates": 0,
                "comments": 0,
                "faqs": 0,
                "money": 0,
                "unit": "",
                "image": "",
            }
        conf = await self.get_custom_conf()
        fields = []
        if "updates" in conf and old_state["updates"] != new_state["updates"]:
            fields.append(
                {
                    "short": True,
                    "title": "updates",
                    "value": f"{old_state['updates']} -> {new_state['updates']}",
                }
            )
        if "comments" in conf and old_state["comments"] != new_state["comments"]:
            fields.append(
                {
                    "short": True,
                    "title": "comments",
                    "value": f"{old_state['comments']} -> {new_state['comments']}",
                }
            )
        if "faqs" in conf and old_state["faqs"] != new_state["faqs"]:
            fields.append(
                {
                    "short": True,
                    "title": "faqs",
                    "value": f"{old_state['faqs']} -> {new_state['faqs']}",
                }
            )
        money_ratio_min = min(old_state["money"], new_state["money"])
        money_ratio_max = max(old_state["money"], new_state["money"])
        money_ratio = money_ratio_max / money_ratio_min if money_ratio_min != 0 else 1
        money_inc = (money_ratio - 1) * 100
        if "money" in conf and money_inc > 10:
            fields.append(
                {
                    "short": True,
                    "title": "money",
                    "value": f"{old_state['unit']} {old_state['money']} "
                    f"-> "
                    f"{new_state['unit']} {new_state['money']}",
                }
            )
        if fields:
            message = {
                "attachments": [
                    {
                        "title": new_state["title"],
                        "title_link": f"https://www.kickstarter.com/projects/{conf['project']}/",
                        "fields": fields,
                        "image_url": new_state["image"],
                    }
                ]
            }
            await self.notify(message, notification_type=NOTIFICATION_RAW)

    @classmethod
    async def validate_custom_conf(cls, conf):
        for key in conf:
            if key not in ["project", "updates", "comments", "faqs", "money"]:
                raise InvalidCustomConf
            if not isinstance(conf[key], str):
                raise InvalidCustomConf
        if "project" not in conf:
            raise InvalidCustomConf
        url = f"https://www.kickstarter.com/projects/{conf['project']}/"
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise InvalidCustomConf

    @classmethod
    async def test_me(cls, test_case):
        print("Kickstarter tested")
