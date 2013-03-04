# Pau Freixes, pfreixes@gmail.com
# 2012-12

from diagnosql.backends import *
from diagnosql.backends.interface import backends, ServiceUnavailable, FunctionNotImplemented


from configobj import ConfigObj

import getopt
import sys
import time
import os

class BadParams(Exception):
    pass

class TestFunctionFailed(Exception):
    pass

class TestCollection:
    """
    TestCollection joins a set of test that they has been
    write each one at one function and registered with
    add_test.

    Each set of test can be run over serveral backend and
    compare all of them.

    To run all tests you can use run_tests

    > class TestDemo(TestCollection):
    >     def __init__(self, backend):
    >         TestDemo.__init__(self, backend)
    >         self.add(self.test_insert, 1000, None, reset=True)
    >         self.add(self.test_insert, 100000, None)
    >
    >     def test_insert(self, registers):
    >         for i in range(0, registers):
    >             self.insert({"_id" : i)})
    >         return registers
    >
    >     def test_query(self, registers):
    >         # test query  the first 10% of documents
    >         for i in range(0, (registers * 10 / 100 )):
    >             doc = self.get(i)
    >             if doc == None:
    >                 raise TestFunctionFailed("Get %d failed" % i)
    >         
    >         # to figure out CPD
    >         return (registers * 10 / 100 )
    >
    > t = TestDemo()
    > print run(t)
    """
    def __init__(self, backend, name = "TestCollection", verbose = False):
        self._tests = []
        self.backend = backend
        self.name = name
        self.verbose = verbose

    def log(self, msg):
        """
        Prints log information
        """
        if self.verbose == True:
            print "[%s] %s" % (self.name, msg)



    def add(self, function, registers, args, start_stop = False, reset = False):
        """
        Register one function test for this backend, the number
        of registers into the data base will be used to figure out the Cost
        per Document, args is one array of several arguments that they will be 
        given to function test. Use start_stop to restart database before to do the
        test. Use reset flag to "erase" all registers before to do the test.
        """
        self._tests.append((start_stop,
                            function,
                            registers,
                            args,
                            reset))

    def run(self):
        """
        Run all tests registered for this backend
        """
        results = []
        for test in self._tests:

            stop_start, function, reg_input, args, reset = test

            if stop_start == True:
                try:
                    self.backend.stop()
                except FunctionNotImplemented:
                    self.log("Stop function hasnt been implemented, skipping test")
                    continue

                try:
                    self.backend.start()
                except FunctionNotImplemented:
                    self.log("Start function hasnt been implemented, skipping test")
                    continue


            if reset == True:
                try:
                    self.backend.reset()
                except FunctionNotImplemented:
                    self.log("Reset function hasnt been implemented, skipping test")
                    continue

            try:

                if args != None:
                    args_ = [reg_input] + args
                else:
                    args_ = [reg_input]

                ts_before = time.time()
                try:
                    reg_output = function(*args_)
                except FunctionNotImplemented, e:
                    raise TestFunctionFailed("One backend function is missing implemented to make this test")
                ts_after = time.time()

                try:
                    disk_usage = self.backend.disk_usage() 
                except FunctionNotImplemented, e:
                    self.log("disk_usage function hasnt been implemented")
                    disk_usage = 0

                try:
                    memory_usage = self.backend.memory_usage() 
                except FunctionNotImplemented, e:
                    self.log("memory_usage function hasnt been implemented")
                    memory_usage = 0

          
            
                # save metrics
                ts_used = ts_after - ts_before
                results.append({ "backend" : self.backend.name,
                                 "name" : function.__name__,
                                 "#in reg" : reg_input,
                                 "#out reg" : reg_output,
                                 "time" : ts_used ,
                                 "disk" : disk_usage,
                                 "memory" : memory_usage})

            except TestFunctionFailed, e:
                results.append({ "backend" : self.backend.name,
                                 "name" : function.__name__,
                                 "#in reg" : reg_input,
                                 "error" : str(e)})



        return results

CONFIG_FILE = "/etc/diagnosql.conf"

def print_result(result, test_name, backend_name, human_readable = True, precision = 2):
    print "Result for : %s" % test_name
    print "Backend type : %s" % backend_name
    print "|%-030s|%+010s|%+08s|%+08s|%+08s|%+08s|" % ("Function", "#in reg", "Time", "#out reg", "Disk MB", "Mem MB")
    print "-"*79
    for r in result:
        if "error" in r:
            print "|%-030s|%+10s|%+031s|" % (r["name"], r["#in reg"], r["error"])
        else:
            time = "%0.2f" % r["time"]
            print "|%-030s|%+10s|%+08s|%+08s|%+08s|%+08s|" % (r["name"], r["#in reg"], time, r["#out reg"], r["disk"], r["memory"])

def usage(filename):
    print "%s usage" % filename
    print "\t-s stop and start each backend before and after each test"
    print "\t-v make me verbose"
    print "\t-c /path/to/config/file default config file at %s" % CONFIG_FILE
    print "\t-h Get this usage resume"
    print "\t--test=test_name run this test only, one section of config file"
    print "\t--list-backends get a list of sort of backends supproted and exit inmediatly"
    print "\t--list-tests get a list of tests and exit inmediatly"
      
def run(test_cls):

    config_file = CONFIG_FILE
    specific_test = None
    stop_start = False
    list_tests = False
    verbose = False

    try:
        optlist, args = getopt.getopt(sys.argv[1:], "vshc:", [ "list-backends", "list-tests", "test="])
    except getopt.GetoptError, e:
        print str(e)
        raise BadParams

    for opt in optlist:
        if opt[0] == "-c":
            config_file = opt[1]
            if config_file == '':
                raise BadParams
        elif opt[0] == "-h":
            raise BadParams
        elif opt[0] == "-v":
            verbose = True
        elif opt[0] == "--test":
            specific_test = opt[1]
        elif opt[0] == "--list-backends":
            b = backends()
            names = [ b[k].backend_type for k in b]
            print "Backends Availables : %s" % names
            sys.exit(0)
        elif opt[0] == "--list-tests":
            list_tests = True

    # read config file and pass all tests
    if os.path.exists(config_file) == False:
        print "File %s can't be found, use -c to give one alternate path" % config_file
        sys.exit(0)

    print "Reading %s" % config_file
    config = ConfigObj(config_file)
    if list_tests:
        for section_name in config.sections:
            print "Test: %s" % section_name
        sys.exit(0)

    if specific_test in config:
        section = config[specific_test]
        backend_cls = backends(section["backend_type"])
        try:
            backend_obj = backend_cls(specific_test, section)
            test_obj = test_cls(backend_obj, verbose = verbose)
            result = test_obj.run()
            print_result(result, specific_test, section["backend_type"])
        except ServiceUnavailable:
            print "Service for this Test can't be found ... skiping"
    elif specific_test != None:
        print "%s Cant be found ...." % specific_test
    else:
        print "Detected %d tests" % len(config.sections)
        for section_name in config.sections:
            section = config[section_name]
            if ("skip" in section) and section.as_bool("skip") == True:
                continue

            backend_cls = backends(section["backend_type"])
            try:
                backend_obj = backend_cls(section_name, section, verbose = verbose)
                test_obj = test_cls(backend_obj, verbose = verbose)
                if stop_start == True:
                    try:
                        backend_obj.start()
                    except FunctionNotImplemented:
                        print "Service can't go up? start method not implemented"
                print "Running %s test" % section_name
                result = test_obj.run()
                print_result(result, section_name, section["backend_type"])       

                if stop_start == True:
                    try:
                        backend_obj.stop()
                    except FunctionNotImplemented:
                        print "Service can't go down, stop method not implemented"
            except ServiceUnavailable:
                print "Service for this Test can't be found ... skiping"

