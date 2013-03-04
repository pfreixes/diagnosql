# Pau Freixes, pfreixes@gmail.com
# 2012-12

import time


class ServiceUnavailable(Exception):
    pass

class FunctionNotImplemented(Exception):
    pass

class BackendInterface:
    backend_type = None
    _registered_interfaces = {}

    def __init__(self, name, verbose = False):
        self.name = name
        self.verbose = verbose

    def log(self, msg):
        """
        Prints log information
        """
        if self.verbose == True:
            print "[%s] (%s) %s" % (self.name, self.backend_type, msg)

    def start(self):
        """
        Start bakend daemon
        """
        raise FunctionNotImplemented()

    def stop(self):
        """
        Stop backend daemon
        """
        raise FunctionNotImplemented()

    def insert(self, document):
        """
        Insert one document at backend 
        """
        raise FunctionNotImplemented()

    def update(self, id, fields):
        """
        Update one document at backend 
        """
        raise FunctionNotImplemented()

    def delete(self, document):
        """
        Delete one document at backend 
        """
        raise FunctionNotImplemented()

    def get(self, id):
        """
        Return one document by id
        """
        raise FunctionNotImplemented()


    def query(self, field, value):
        """
        Query one subset of documents at backend 
        """
        raise FunctionNotImplemented()

    def query_range(self, field, from_, to):
        """
        Query one subset of documents at backend with
        one field between from_ and to
        """
        raise FunctionNotImplemented()


    def reset(self):
        """
        Reset data backend used in previous tesets
        """
        raise FunctionNotImplemented()

    def disk_usage(self):
        """
        Returns how many space is bussy for the backend in MB
        """
        raise FunctionNotImplemented()

    def memory_usage(self):
        """
        Returns how many main memory is bussy for the backend in MB
        """
        raise FunctionNotImplemented()
 

def backends(backend_type = None):
    if backend_type != None:
        return BackendInterface._registered_interfaces[backend_type]
      
    return BackendInterface._registered_interfaces

def implements(backend_type, cls):
    BackendInterface._registered_interfaces[backend_type] = cls
    cls.backend_type = backend_type
