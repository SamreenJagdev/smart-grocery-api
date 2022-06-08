import os
from pymongo import MongoClient


class DBService:
    @staticmethod
    def getDB():
        return MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))

    def getInstance():
        return DBService.getDB().get_database(name=os.getenv("MONGODB_DATABASE"))
