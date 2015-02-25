import gevent

from gevent.queue import Queue
from gevent import monkey
monkey.patch_socket()

# from utils.log import logger


class Worker(object):
    def __init__(self, workers_number, results_type="extend_list"):
        '''
        array_results: The return value of the function may be the [] array
        And extend all arrays into the array_results
        If the results_type is "extend_list", so each result is a list,
            and extend them
        If is "add_element" ,so each result is a element ,and add each element
            to the list
        '''
        self.workers_number = workers_number
        self.tasks = Queue()
        self.array_results = []
        self.results_type = results_type

    def put_tasks(self, all_tasks):
        '''
        The boss put all tasks into queue
        '''
        for one_task in all_tasks:
            self.tasks.put_nowait(one_task)

    def generate_boss(self, all_tasks):
        '''
        '''
        self.all_tasks_number = len(all_tasks)
        boss = [gevent.spawn(self.put_tasks, all_tasks)]
        return boss

    def get_tasks(self, worker_id, func, *args, **kwargs):
        '''
        The worker get all tasks from queue, and run the
        corresponding function
        '''
        while not self.tasks.empty():
            task = self.tasks.get()
            progress = self.show_progress()
            ret = func(task, progress, *args, **kwargs)
            if ret and self.results_type == "extend_list":
                self.array_results.extend(ret)
            elif ret and self.results_type == "add_element":
                self.array_results.append(ret)
            # logger.info("The worker %s has got task %s " % (worker_id, task))

    def generate_workers(self, func, *args, **kwargs):
        '''
        Generate workers array
        '''
        workers = [gevent.spawn(self.get_tasks, worker_id,
                   func, *args, **kwargs)
                   for worker_id in xrange(1, self.workers_number + 1)]
        return workers

    def joinall(self, boss, workers):
        all_spawns = boss + workers
        gevent.joinall(all_spawns)

    def return_results(self):
        '''
        Return the array results
        '''
        return self.array_results

    def show_progress(self):
        '''
        Show the progress in two ways
        1. current_task / all_task
        2. the percentage
        '''
        self.current_tasks_id = self.tasks.qsize()
        progress_one = '%s/%s' % (self.current_tasks_id, self.all_tasks_number)

        progress_percentage = 1 - float(self.current_tasks_id)\
            / float(self.all_tasks_number)
        progress_two = "%s" % (progress_percentage * 100)
        progress = [progress_one, progress_two]
        return progress

    def pack(self, all_tasks, func, *args, **kwargs):
        '''
        Pack all steps into one function
        '''
        boss = self.generate_boss(all_tasks)
        workers = self.generate_workers(func, *args, **kwargs)
        self.joinall(boss, workers)
        return self.return_results()
