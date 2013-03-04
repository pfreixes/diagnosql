About Diagnosql
---------------

Diagnosql is a framework to test one document data paradigm over one set of
NoSql - and sql - backends.

Current only JSON or document oriented backends are suported, another none
full converge backends over document data paradigm will be supported like
redis, mysql.


Backends suppoted
--------------

Current backends suported are :

  * MongoDB
  * ArangoDB ( partial supported )
  * CouchBase ( partial supported )
  * Redis (not supported yet)
  * MySql (not supported yet)

Prepare your test
-----------

You know how is your data model, not only how your documents are build, also 
how fields will be filled.

```
class TestDemo(TestCollection):
    def __init__(self, backend):
        testcollection.TestCollection.__init__(self, backend, "Test", verbose)
        self.add(self.test_insert, 1000, None, reset=True)
        self.add(self.test_insert, 100000, None)
    
    def test_insert(self, registers):
        self.log("Test insert over %d" % registers)
        for i in range(0, registers):
            self.insert({"_id" : i)})
        return registers
    
    def test_query(self, registers):
        # test query  the first 10% of documents
        self.log("Test query over %%10 of registers")
        for i in range(0, (registers * 10 / 100 )):
            doc = self.get(i)
            if doc == None:
                raise TestFunctionFailed("Get %d failed" % i)
             
        # to figure out CPD
        return (registers * 10 / 100 )
    
try:
    testcollection.run(TestDemo)
except testcollection.BadParams:
    testcollection.usage(__file__)
    sys.exit(0)

```
Each test should have a configuration file  where it have to describe a
set of backends where it will be performed.

```
[couchdbase localhost]
backend_type = CouchBaseDb
hostname = localhost
port = 8091
bucket = default
username = diagnosql
password = diagnosql
view_doc = dev_diagnosql


[mongodb localhost]
backend_type = MongoDb
hostname = localhost
port = 27017
database = diagnosql
collection = diagnosql
```


And Run
-------------

Diagnosql will run your data model over a set of documents, and it will figure out
how many seconds each backend gets to perform each function test

```
diagnosql@b0:~$ ./test.py --test="mongodb localhost" -c test.cfg
Reading test.cfg
Result for : arangodb localhost
Backend type : ArangoDb
|Function                      |   #in reg|    Time|#out reg| Disk MB|  Mem MB|
-------------------------------------------------------------------------------
|test_insert                   |     1000|    0.50|    1000|       3|    1077|
|test_query                   |      1000|    0.70|    1000|       3|    1077|
|test_insert                   |   100000|    5.50|    1000|     151|    1077|
|test_query                   |    100000|    0.80|    1000|     151|    1077|
	
```

Usage
-------
```
diagnosql@b0:~$ ./test.py -h
./test.py usage
	-s stop and start each backend before and after each test
	-v make me verbose
	-c /path/to/config/file default config file at /etc/diagnosql.conf
	-h Get this usage resume
	--test=test_name run this test only, one section of config file
	--list-backends get a list of sort of backends supproted and exit inmediatly
	--list-tests get a list of tests and exit inmediatly
```
