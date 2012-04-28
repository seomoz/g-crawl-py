#! /usr/bin/env python

import logging
logging.basicConfig()
logger = logging.getLogger('gcrawl')

from gevent import sleep

import urllib3
import requests
from .url import Url
from lxml import etree

# The XPath functions available in lxml.etree do not include a lower()
# function, and so we have to provide it ourselves. Ugly, yes.
import string
def lower(dummy, l):
    return [string.lower(s) for s in l]

ns = etree.FunctionNamespace(None)
ns['lower'] = lower

class Crawl(object):
    # The headers that we'd like to use in general
    headers = {}
    # Disallowed schemes
    banned_schemes = ('mailto', 'javascript', 'tel')
    
    # A few xpaths we use
    # Meta robots. This applies to /all/ robots, though...
    metaRobotsXpath = etree.XPath('//meta[lower(@name)="robots"]/@content')
    # The xpath for finding the base tag, if one is supplied
    baseXpath = etree.XPath('//base[1]/@href')
    # Links we count should:
    #   - have rel not containing nofollow
    #   - have a valid href
    #   - not start with any of our blacklisted schemes (like 'javascript', 'mailto', etc.)
    s = '//a[not(contains(lower(@rel),"nofollow"))]'
    s += ''.join('[not(starts-with(normalize-space(@href),"%s:"))]' % sc for sc in banned_schemes)
    linksXpath = etree.XPath(s + '/@href')
    
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
        while self.requests and self.crawled < self.max_pages:
            url = self.pop()
            try:
                logger.info('Requesting %s' % url)
                response = requests.get(url, headers=self.headers)
                tree = self.parse(response)
                
                # Should we append these results?
                r = self.dump(response, tree)
                if r:
                    self.results.append(r)
                
                if self.count(response, tree):
                    self.crawled += 1
                
                if self.recurse(response, tree):
                    # Meta robots, and all links
                    metar = self.metaRobotsXpath(tree)
                    base  = self.baseXpath(tree) or url
                    links = [Url.sanitize(link, base) for link in self.linksXpath(tree)]
                    self.extend(links, response)
                
                sleep(self.delay(response))
            except Exception as e:
                logger.exception('Failed to request %s' % next)
        
        self.after()
        return self.results
    
    def after(self):
        '''This is executed after we run the main crawl loop, befor returning'''
        pass
    
    def delay(self, response):
        '''How long to wait before sending the next request'''
        return 2
    
    def parse(self, response):
        '''This generates a query-able tree'''
        return etree.fromstring(response.text, etree.HTMLParser(recover=True))
    
    def pop(self):
        '''Get the next url we should fetch'''
        return self.requests.pop(0)
    
    def extend(self, urls, response):
        '''Add these urls to the list of requests we have to make'''
        logger.debug('Adding links: %s' % '\n'.join(urls))
        self.requests.extend(urls)
    
    def recurse(self, response, tree):
        '''Return true if we should recurse on the content of this request'''
        return True
    
    def dump(self, response, tree):
        '''Produce the output you would like to save, based on the
        response. Return `None` to save nothing'''
        return None
    
    def count(self, response, tree):
        '''Return true here if this request should count toward the 
        max number of pages.'''
        return True
    
    def allowed(self, response, url, metarobots):
        '''If you would like to perform some additional pruning
        during your crawl, subclass (or assign) this function to
        make decisions about whether or not to crawl a page'''
        return True
    