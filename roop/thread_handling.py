from threading import Thread
import roop.globals
def thread_with_return_value(target, counter, args=(), kwargs={}):
    def wrapper(c):
        roop.globals.results.append([c , target(*args, **kwargs)])
    thread = Thread(target=wrapper, args=(counter, ))
    return thread 

def create_thread(target, counter, args):
    return thread_with_return_value(target, counter, args)

def get_result_from_thread(thread):
    return thread
