from exceptions import MonitorAlreadyExists
from models.database import Database


class MonitorModel:
    @classmethod
    async def create(cls, monitor_conf, custom_conf):
        collection = Database.get_collection("monitors")
        document = await collection.find_one(
            {"monitor_conf": {"name": monitor_conf["name"]}}
        )
        if document is not None:
            raise MonitorAlreadyExists()
        document_data = {
            "monitor_conf": monitor_conf,
            "custom_conf": custom_conf,
            "state": None,
        }
        await collection.insert_one(document_data)
        return MonitorModel(document_data)

    @classmethod
    async def retrieve(cls, name):
        collection = Database.get_collection("monitors")
        document = await collection.find_one({"monitor_conf": {"name": name}})
        return MonitorModel(document)

    @classmethod
    async def get_all(cls):
        collection = Database.get_collection("monitors")
        monitor_models = []
        async for document in collection.find():
            monitor_models.append(MonitorModel(document))
        return monitor_models

    def __init__(self, document):
        self.document = document

    async def custom_conf(self, value=None):
        collection = Database.get_collection("monitors")
        self.document = await collection.find_one(
            {"monitor_conf.name": self.document["monitor_conf"]["name"]}
        )
        if value is None:
            return self.document["custom_conf"]
        else:
            self.document = await collection.update_one(
                {
                    {"monitor_conf.name": self.document["monitor_conf"]["name"]},
                    {"$set": {"custom_conf": value}},
                }
            )

    async def monitor_conf(self, value=None):
        collection = Database.get_collection("monitors")
        self.document = await collection.find_one(
            {"monitor_conf.name": self.document["monitor_conf"]["name"]}
        )
        if value is None:
            return self.document["monitor_conf"]
        else:
            self.document = await collection.update_one(
                {
                    {"monitor_conf.name": self.document["monitor_conf"]["name"]},
                    {"$set": {"monitor_conf": value}},
                }
            )
