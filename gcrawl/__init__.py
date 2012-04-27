#! /usr/bin/env python

import logging

logger = logging.getLogger('gcrawl')

import urllib3
import requests

class Crawl(object):
    # The headers that we'd like to use in general
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
    
    def __init__(self, seed, allow_subdomains=False, max_pages=10):
        self.requests         = [seed]
        self.results          = []
        self.crawled          = 0
        self.allow_subdomains = allow_subdomains
        self.max_pages        = max_pages
    
    def before(self):
        '''This is executed before we run the main crawl loop'''
        pass
    
    def run(self):
        self.before()
        while self.requests and len(self.results) < self.max_pages:
            next = self.requests.pop()
            try:
                response = requests.get(next, headers=self.headers)
                r = self.dump(response)
                if r:
                    self.results.append(r)
                
                if self.count(response):
                    self.crawled += 1
                
                if self.recurse(response):
                    from lxml import etree
                    parser = etree.HTMLParser(recover=True)
                    # Some stuff here
                    tree = etree.fromstring(response.text, parser)
                
            except Exception as e:
                logger.exception('Failed to request %s' % next)
        
        self.after()
        return self.results
    
    def after(self):
        '''This is executed after we run the main crawl loop, befor returning'''
        pass
    
    def recurse(self, response):
        '''Return true if we should recurse on the content of this request'''
        return True
    
    def dump(self, response):
        '''Produce the output you would like to save, based on the
        response. Return `None` to save nothing'''
        return None
    
    def count(self, response):
        '''Return true here if this request should count toward the 
        max number of pages.'''
        return True
    
    def allowed(self, url):
        '''If you would like to perform some additional pruning
        during your crawl, subclass (or assign) this function to
        make decisions about whether or not to crawl a page'''
        return True
    