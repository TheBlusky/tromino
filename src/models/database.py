import asyncio

import motor.motor_asyncio


class Database:
    database = None
    loop = None

    @classmethod
    def get_collection(cls, collection):
        if Database.database is None or id(Database.loop) != id(
            asyncio.get_event_loop()
        ):
            client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongo:27017")
            Database.database = client.tromino
            Database.loop = asyncio.get_event_loop()
        return Database.database[collection]
