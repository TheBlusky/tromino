from exceptions import ParameterAlreadyExists
from models.database import Database


class ParameterModel:
    @classmethod
    async def create(cls, param_name, value):
        collection = Database.get_collection("config")
        document = await collection.find_one({"param_name": param_name})
        if document is not None:
            raise ParameterAlreadyExists()
        document_data = {"param_name": param_name, "value": value}
        await collection.insert_one(document_data)
        return ParameterModel(document_data)

    @classmethod
    async def retrieve(cls, param_name):
        collection = Database.get_collection("config")
        document = await collection.find_one({"param_name": param_name})
        return document and ParameterModel(document)

    def __init__(self, document):
        self.param_name = document["param_name"]
        self.value = document["value"]

    async def change_value(self, new_value):
        collection = Database.get_collection("config")
        await collection.update_one(
            {"param_name": self.param_name}, {"$set": {"value": new_value}}
        )
        self.value = new_value
