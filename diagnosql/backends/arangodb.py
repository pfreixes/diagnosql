# Pau Freixes, pfreixes@gmail.com
# 2012-12

from diagnosql.backends import interface

from arango import create
from requests import exceptions

import bson.son as son
import datetime
import time

class ArangoDb(interface.BackendInterface):

    def __init__(self, name, config, verbose = False):

        interface.BackendInterface.__init__(self, name, verbose = verbose)

        host = config.get('hostname')
        port = int(config.get('port'))
        self.collection_name = config.get('collection')

        try:
            self.connection = create(host=host, port=port)
        except exceptions.ConnectionError:
            self.log("Error connecting to %s:%d" % (host, port))
            raise interface.ServiceUnavailable()

        self.collection = getattr(self.connection, self.collection_name)


    def start(self):
        raise interface.FunctionNotImplemented()

    def stop(self):
        raise interface.FunctionNotImplemented()

    def insert(self, document):
        d = self.collection.documents.create(document)
        return d.id

    def update(self, id, fields):
        self.collection.documents.update(id, fields)

    def get(self, id):
        self.log("get method is not implemented, going to all documents")
        for doc in self.collection.documents():
            if doc.id == id:
                return doc
        
    def query(self, field, value):
        raise interface.FunctionNotImplemented()

    def query_range(self, field, from_, to):
        raise interface.FunctionNotImplemented()


    def reset(self):
        """
        Reset on ArangoDb means delete and create collection
        """
        self.collection.delete()
        self.collection.create(waitForSync=True)

    def disk_usage(self):
        raise interface.FunctionNotImplemented()

    def memory_usage(self):
        raise interface.FunctionNotImplemented()
  

interface.implements("ArangoDb", ArangoDb)
