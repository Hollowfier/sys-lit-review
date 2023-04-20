import pymongo

class MongoDB(object):
    uri = 'mongodb://localhost:27017/'
    db = None
    
    @staticmethod
    def initialize():
        client = pymongo.MongoClient(MongoDB.uri)
        MongoDB.db = client['aislr_database']
        
    @staticmethod
    def insert_one(collection, data):
        MongoDB.db[collection].insert_one(data)
        
    @staticmethod
    def insert_many(collection, data):
        MongoDB.db[collection].insert_many(data)
        
    @staticmethod
    def find(collection, query):
        return MongoDB.db[collection].find(query)
        
    @staticmethod
    def find_one(collection, query):
        return MongoDB.db[collection].find_one(query)