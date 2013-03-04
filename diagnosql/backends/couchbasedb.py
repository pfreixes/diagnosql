# Pau Freixes, pfreixes@gmail.com
# 2012-12

from diagnosql.backends import interface

import couchbase
import json
import datetime
import time

class CouchBaseDb(interface.BackendInterface):
    

    def __init__(self, name, config, verbose = False):

        interface.BackendInterface.__init__(self, name, verbose = verbose)

        host = config.get('hostname')
        port = int(config.get('port'))
        self.bucket_name = config.get('bucket')
        self.username = config.get('username')
        self.password = config.get('password')
        self.view_doc = config.get('view_doc')
        self._first_id = self._next_id = 1

        try:
            self.connection = couchbase.Couchbase("%s:%d" % (host, port),
                                                  self.username,
                                                  self.password)
            self.bucket = self.connection[self.bucket_name]
        except Exception, e:
            self.log("Error connecting to %s:%d" % (host, port))
            self.log(str(e))
            raise interface.ServiceUnavailable()
        except couchbase.exception.BucketUnavailableException:
            self.log("Bucket %s is unavailable" % self.bucket_name)
            raise interface.ServiceUnavailable()


    def start(self):
        raise interface.FunctionNotImplemented()

    def stop(self):
        raise interface.FunctionNotImplemented()

    def insert(self, document):
        id = self._next_id 
        self.bucket.set(str(id), 0, 0, document)
        self._next_id = id + 1
        return id

    def update(self, id, fields):
        """
        Current backend update implementation gets
        more time to retrieve first the original
        document.
        """
        original = self.get(id)
        original.update(fields)
        self.bucket.replace(str(id), 0, 0, json.dumps(original))

    def get(self, id):
        return json.loads(self.bucket.get(str(id))[2])
        
    def query(self, field, value):
        # query is performed by views
        try:
            return self.bucket.view("_design/%s/%s" % (self.view_doc, field), key=value)
        except Exception, e:
            self.log("Query can't be run, missing view ?....")
            raise interface.FunctionNotImplemented()

    def query_range(self, field, from_, to):
        # query is performed by views
        try:
            return self.bucket.view("_design/%s/%s" % (self.view_doc, field),
                             start_key=from_,
                             end_key=to)
        except Exception, e:
            self.log("Query can't be run, missing view ?....")
            raise interface.FunctionNotImplemented()



    def reset(self):
        """
        Just delete all documents that has been created
        """
        for id in range(self._first_id, self._next_id):
            self.bucket.delete(str(id))

        self._first_id = self._next_id = 1

    def disk_usage(self):
        raise interface.FunctionNotImplemented()

    def memory_usage(self):
        raise interface.FunctionNotImplemented()


interface.implements("CouchBaseDb", CouchBaseDb)
