
from nose.tools import raises, nottest, timed

class ExceptionForTest(Exception):
    pass

def will_succeed():
    return True

def will_fail():
    raise ExceptionForTest('failed as expected')

def fn_interrupted():
    raise KeyboardInterrupt

def will_hang():
    import sys,time
    time.sleep(sys.maxsize)
    
def will_busyhang():
    while True:
        pass
    
def will_busyhang_uninterruptible():
    #import signal
    #signal.signal(signal.SIGINT, signal.SIG_IGN)
    #signal.signal(signal.SIGQUIT, signal.SIG_IGN)
    #while True:
    #    pass
    while True:
        try:
            pass
        except BaseException:
            pass
    
def identity(x):
    return x

def busy_identity(x):
    import time
    delay = 0.01
    start = time.time()
    while time.time() - start < delay:
        pass
    return x 

def random_int(seed=None):
    import random,sys
    
    if seed is not None:
        random.seed(seed)
    
    return random.randint(0,sys.maxsize)

def get_process_index():
    import os, time
    time.sleep(1) # this ensures that each task gets its own worker
    return os.environ['WM_PROCESS_INDEX']

class CommonWorkManagerTests:
    MED_TEST_SIZE=256
    
    def test_submit(self):
        future = self.work_manager.submit(will_succeed)
        future.get_result()
            
    def test_submit_many(self):
        futures = self.work_manager.submit_many([(will_succeed,(),{}) for i in range(self.MED_TEST_SIZE)])
        for future in futures:
            future.get_result()
            
    def test_as_completed(self):
        input = set(range(self.MED_TEST_SIZE))
        futures = [self.work_manager.submit(identity, args=(i,)) for i in range(self.MED_TEST_SIZE)]
        output = set(future.get_result() for future in self.work_manager.as_completed(futures))
        assert input == output

    def test_submit_as_completed(self):
        task_generator = ((busy_identity, (i,), {}) for i in range(self.MED_TEST_SIZE))
        input = set(range(self.MED_TEST_SIZE))
        output = set(future.get_result() for future in self.work_manager.submit_as_completed(task_generator, 10))
        assert input == output

    def test_wait_any(self):
        input = set(range(self.MED_TEST_SIZE))
        futures = [self.work_manager.submit(identity, args=(i,)) for i in range(self.MED_TEST_SIZE)]
        output = self.work_manager.wait_any(futures).get_result()
        assert output in input
        
    def test_wait_all(self):
        input = set(range(self.MED_TEST_SIZE))
        futures = [self.work_manager.submit(identity, args=(i,)) for i in range(self.MED_TEST_SIZE)]
        output = set(future.get_result() for future in self.work_manager.wait_all(futures))
        assert input == output
        
    @raises(ExceptionForTest)
    def test_exception_raise(self):
        future = self.work_manager.submit(will_fail)
        future.get_result()
        
    def test_exception_retrieve(self):
        future = self.work_manager.submit(will_fail)
        exc = future.get_exception()
        assert exc.args[0] == 'failed as expected'


class CommonParallelTests:
    def test_random_seq(self):
        tasks = [(random_int,(),{}) for n in range(self.MED_TEST_SIZE)]
        futures = self.work_manager.submit_many(tasks)
        self.work_manager.wait_all(futures)
        result_list = [future.get_result() for future in futures]
        result_set = set(result_list)
        assert len(result_list) == len(result_set)
        
    def test_random_seq_improper_seeding(self):
        tasks = [(random_int,(1979,),{}) for n in range(self.MED_TEST_SIZE)]
        futures = self.work_manager.submit_many(tasks)
        self.work_manager.wait_all(futures)
        result_list = [future.get_result() for future in futures]
        result_set = set(result_list)
        
        assert len(result_list) != len(result_set)
    
