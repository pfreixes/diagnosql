#!/usr/bin/python

# Pau Freixes, pfreixes@gmail.com
# 2012-12
#
# Set of test to check how faster is one data pradigm
# over n backends described at test.cfg
#
# $ python test.py -c test.cfg

from diagnosql import testcollection

import datetime
import time
import random
import copy
import sys

class Test(testcollection.TestCollection):

    def __init__(self, backend, verbose = False):
        testcollection.TestCollection.__init__(self, backend, "TestOriol", verbose)
        for amount in (1000, 10000, 100000, 1000000):
            self.add(self.test_insert, amount, None, start_stop = False, reset = True)
            self.add(self.test_update, amount, None, start_stop = False, reset = False)
            self.add(self.test_query_id, amount, None, start_stop = False, reset = False)
            self.add(self.test_query_subset_from, amount, None, start_stop = False, reset = False)
            self.add(self.test_query_subset_to, amount, None, start_stop = False, reset = False)
            self.add(self.test_query_subset_ts, amount, None, start_stop = False, reset = False)

        # prepare data paradigm
        self.doc_model = { 'state': { 'ts': 0, 'state':'', 'reason':'' },
                      'redis_content_id':'',
                      'headers': [],
                      'body': '',
                      'dsn':{'action':'', 'status':'', 'diagnostic-code':'', 'arrival-date':'', 'reporting-MTA':'', 'final-recipient':'','original-recipient':''},
                      'transport':'',
                      'delay':'',
                      'delays': {},
                      'return-path':'',
                      'verp': False,
                      'timestamp': 0,
                      'from': {'name':'', 'email':''},
                      'to': [ {'name':'', 'email':''}, {'name':'', 'email':''}],
                      'msg_id': '', 
                      'open': 0, 
                      'click': 0, 
                      'bounce': 0, 
                      'error': '',
                      'error_code': '',
                      'queue_id': ''
                  }

    def _generate_fields_ranges(self, amount):
        # used to genereate field ranges
        # with one amount

        # timestamp will be used to query and it will be sparsed in a 
        # equiprobable way
        base_ts = datetime.datetime.combine(datetime.date.today(), datetime.time())
        time_gap = 86400 / amount
        doc_per_time_gap = 1
        while time_gap == 0:
            doc_per_time_gap = doc_per_time_gap * 2
            time_gap = 86400 / (amount / doc_per_time_gap )

        # from and to :
        # The from values has a short set of values and to values
        # has a long set of values
        log_b10 = 1
        while log_b10**10 < amount:
            log_b10 = log_b10 + 1
        max_from = 2 * ( log_b10 * 2 )
        max_to = amount / 2

        return base_ts, time_gap, doc_per_time_gap, max_from, max_to


    def test_insert(self, amount):
        self.log("test_insert %d registers" % amount)
        self._ids = []
        base_ts, time_gap, doc_per_time_gap, max_from, max_to = self._generate_fields_ranges(amount)
        for i in range(0, amount):
            doc_model = copy.deepcopy(self.doc_model)
            doc_model["ts"] = time.mktime(base_ts.timetuple()) + (time_gap * i)
            doc_model["from"] = {'name': str(i % max_from) , 'email': str(i % max_from)}
            doc_model["to"] = [{'name': str(i % max_to) , 'email': str(i % max_to)}]
            id = self.backend.insert(doc_model)
            self._ids.append(id) # be carefull with large amounts of data

        return amount
            

    def test_update(self, amount):
        self.log("test_update %d registers" % amount)
        for id in self._ids:
            self.backend.update(id, {"body" : "test body"})

        return len(self._ids)

    def test_query_id(self, amount):
        to_query = (amount * 2) / 100
        self.log("test_query_id %d over %d registers" % (to_query, amount))
        for i in range(0, to_query):
            id = self._ids[random.randint(0, len(self._ids)-1)]
            doc = self.backend.get(id)
            if doc is None:
                raise testcollection.TestFunctionFailed("Document %d cant be found" %  id)

        return to_query
 
    def test_query_subset_from(self, amount):
        _, _, _, max_from, _ = self._generate_fields_ranges(amount)
        from_ = random.randint(0, max_from)
        self.log("test_query_subset_from over %d registers" % amount)
        docs = self.backend.query("from.email", str(from_))
        if len(docs) == 0:         
            raise testcollection.TestFunctionFailed("No results !!!")
        self.log("test_query_subset_from found %d registers" % len(docs))

        return len(docs)
        
    def test_query_subset_to(self, amount):
        _, _, _, _, max_to = self._generate_fields_ranges(amount)
        to = random.randint(0, max_to)
        self.log("test_query_subset_to over %d registers" % amount)
        docs = self.backend.query("to.email", str(to))
        if len(docs) == 0:         
            raise testcollection.TestFunctionFailed("No results !!!")
        self.log("test_query_subset_to found %d registers" % len(docs))

        return len(docs)

    def test_query_subset_ts(self, amount):
        base_ts, _, _, _, _ = self._generate_fields_ranges(amount)
        window_time = random.randint(0, 24)
        from_time = time.mktime(base_ts.timetuple()) + ( window_time * 60 * 60)
        to_time = time.mktime(base_ts.timetuple()) + ( window_time * 60 * 60) + 3600
        self.log("test_query_subset_ts over %d registers" % amount)
        docs = self.backend.query_range("ts", from_time, to_time)
        if len(docs) == 0:         
            raise testcollection.TestFunctionFailed("No results !!!")
        self.log("test_query_subset_ts found %d registers" % len(docs))

        return len(docs)


if __name__ == "__main__":
    try:
        testcollection.run(Test)
    except testcollection.BadParams:
        testcollection.usage(__file__)
        sys.exit(0)
