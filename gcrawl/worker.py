#! /usr/bin/env python

import qless
from . import logger
from gevent.pool import Pool
from gevent import sleep, Greenlet
from gevent import monkey; monkey.patch_all()

class Worker(object):
    def __init__(self, queue, workers, host='localhost', port=6379, hostname=None, interval=60):
        self.client   = qless.client(host=host, port=port, hostname=hostname)
        self.queue    = self.client.queue(queue)
        self.workers  = workers
        self.interval = interval
    
    def run(self):
        pool = Pool(self.workers)
        while True:
            # Wait until a worker is available
            pool.wait_available()
            # Now, try to get a new job
            job = self.queue.pop()
            if job:
                logger.info('Starting job %s in %s' % (job.jid, job.queue))
                pool.start(Greenlet(job.process))
                logger.info('Completing job %s in %s' % (job.jid, job.queue))
            else:
                logger.info('No jobs. Sleeping %s' % self.interval)
                sleep(self.interval)
