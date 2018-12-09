import motor.motor_asyncio


class Database:
    database = None

    @classmethod
    def get_collection(cls, collection):
        if Database.database is None:
            client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongo:27017")
            Database.database = client.tromino
        return Database.database[collection]
