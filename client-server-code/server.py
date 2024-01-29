import threading

from methods.SimpleMethod import SimpleMethod
from methods.JSONPathMethod import JSONPathMethod
from methods.TablesMethod import TablesMethod

if __name__ == '__main__':
    paths = [ '../data/airlines.json', 
            '../data/gists.json', 
            '../data/historical-events.json',
            '../data/movies.json',
            '../data/reddit.json',
            '../data/nasa.json']
    
    method1 = JSONPathMethod()
    thread1 = threading.Thread(target=method1.serve_example, args=(paths, 50051))
    thread1.start()

    method2 = SimpleMethod()
    thread2 = threading.Thread(target=method2.serve_example, args=(paths, 50052))
    thread2.start()

    method3 = TablesMethod()
    thread3 = threading.Thread(target=method3.serve_example, args=(paths, 50053))
    thread3.start()


    thread1.join()
    thread2.join()
    thread3.join()

