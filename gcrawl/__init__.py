#! /usr/bin/env python

import urllib3
import requests
from .page import Page
from gevent import sleep

import logging
logging.basicConfig()
logger = logging.getLogger('gcrawl')
logger.setLevel(logging.INFO)

class Crawl(object):
    # The headers that we'd like to use when making requests
    headers = {}
    
    @staticmethod
    def crawl(job):
        # @Matt, this is where you'd describe your qless job. For
        # example, you'd probably so something like this. This would
        # allow you to spawn up a bunch of these, and really saturate
        # all the CPU without worrying about network IO stuff
        c = Crawl(job['seed'], job['allow_subdomains'], job['max_pages'])
        results = c.run()
        with file('%s-dump' % job.jid, 'w+') as f:
            import cPickle as pickle
            pickle.dump(results, f)
        
        job.complete()
    
    def __init__(self, seed, allow_subdomains=False, max_pages=10, allow_redirects=False):
        self.requests         = [seed]
        self.results          = []
        self.crawled          = 0
        self.allow_subdomains = allow_subdomains
        self.max_pages        = max_pages
        self.allow_redirects  = allow_redirects
    
    def before(self):
        '''This is executed before we run the main crawl loop'''
        pass
    
    def run(self):
        self.before()
        while self.requests and self.crawled < self.max_pages:
            url = self.pop()
            try:
                logger.info('Requesting %s' % url)
                page = Page(requests.get(url, headers=self.headers, allow_redirects=self.allow_redirects))
                
                # Should we append these results?
                r = self.got(page)
                if r:
                    self.results.append(r)
                
                if self.count(page):
                    self.crawled += 1
                
                sleep(self.delay(page))
            except Exception as e:
                logger.exception('Failed to request %s' % next)
        
        self.after()
        return self.results
    
    def after(self):
        '''This is executed after we run the main crawl loop, befor returning'''
        pass
    
    def delay(self, page):
        '''How long to wait before sending the next request'''
        return 2
    
    def pop(self):
        '''Get the next url we should fetch'''
        return self.requests.pop(0)
    
    def extend(self, urls, page):
        '''Add these urls to the list of requests we have to make'''
        self.requests.extend(urls)
    
    def got(self, page):
        '''We fetched a page. Here is where you should decide what
        to do. Most likely, you'll add all the followable links to
        the requests you'll make. If you want something appended to
        the array returned by `run`, return that value here'''
        logger.info('Fetched %s' % page.url)
        if page.status in (301, 302, 303, 307):
            logger.info('Following redirect %s => %s' % (page.url, page.redirection))
            self.extend([page.redirection], page)
        else:
            self.extend(page.links['follow'], page)
        return None
    
    def count(self, page):
        '''Return true here if this request should count toward the 
        max number of pages.'''
        return page.status not in (301, 302, 303, 307)
    