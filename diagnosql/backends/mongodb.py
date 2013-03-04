# Pau Freixes, pfreixes@gmail.com
# 2012-12

from diagnosql.backends import interface

from pymongo import Connection, errors

import bson.son as son
import datetime
import time

class MongoDb(interface.BackendInterface):

    def __init__(self, name, config, verbose = False):

        interface.BackendInterface.__init__(self, name, verbose = verbose)

        host = config.get('hostname')
        port = int(config.get('port'))
        self.database_name = config.get('database')
        self.collection_name = config.get('collection')

        # suport for resident and virtual memory profiling
        self.mem_type_for_profile = config.get("mem_type_for_profile", "virtual")

        try:
            self.connection = Connection(host, port)
        except errors.AutoReconnect:
            self.log("Error connecting to %s:%d" % (host, port))
            raise interface.ServiceUnavailable()

        self.collection = self.connection[self.database_name][self.collection_name]


    def start(self):
        raise interface.FunctionNotImplemented()

    def stop(self):
        raise interface.FunctionNotImplemented()

    def insert(self, document):
        id = self.collection.insert(document)
        return id

    def update(self, id, fields):
        self.collection.update({"_id": id}, {"$set": fields })

    def get(self, id):
        return self.collection.find_one({"_id": id})
        
    def query(self, field, value):
        docs = self.collection.find({field: value})
        l_docs = [ x  for x in docs]
        return l_docs

    def query_range(self, field, from_, to):
        docs = self.collection.find({field: { "$gte" : from_, "$lte" : to}})
        l_docs = [ x  for x in docs]
        return l_docs


    def reset(self):
        """
        Reset on MongoDB means delete and create collection
        """
        self.connection[self.database_name].drop_collection(self.collection_name)
        self.connection[self.database_name].create_collection(self.collection_name)
        self.collection = self.connection[self.database_name][self.collection_name]

    def disk_usage(self):
        data = self.connection[self.database_name].command("dbstats")
        storage_size = int(data['storageSize']) / 1024 / 1024
        return storage_size

    def memory_usage(self):
        data = self.connection.admin.command(son.SON([('serverStatus', 1)]))

        if self.mem_type_for_profile == "resident":
            return int(data['mem']['resident']) 
        else:
            return int(data['mem']['virtual']) 
  

interface.implements("MongoDb", MongoDb)
