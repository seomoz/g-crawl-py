g-crawl-py
==========
Qless-based crawl jobs, and gevent-based crawling. Hot damn!

Installation
============
Installation in the typical way:

	sudo python setup.py install

This installs, aside from the library itself, `reppy`, `urllib3`, `requests` and
`gevent`. In addition to these, you'll have to install qless-py manually until it
is released on `pip`:

	git clone git://github.com/seomoz/qless-py.git
	cd qless-py
	sudo python setup.py install

Until you need to run `qless` jobs, you won't need it, but when that day inevitably
comes, you'll need Redis 2.6. Unfortunately, Redis 2.6 has been delayed, and is 
still only available as an unstable release. __NOTE__: You only need Redis 2.6 
installed on the system where you'll be hosting the queue. This may or may not be
the same system where you'll be running your crawlers:

	git clone git://github.com/antirez/redis.git
	cd redis
	git checkout 2.6
	make && make test && sudo make install

Development
===========
There's mostly one class that you have to worry about subclassing: `gcrawl.Crawl`.
It provides a few methods that you're encouraged to override in subclasses:

	def before(self):
		# This method gets executed before the crawl loop, in case you need it
	
	def after(self):
		# Before's counterpart, exucted right before returning from `run()`
	
	def delay(self, response):
		# Return how many seconds to wait before sending the next request in this crawl
    
    def parse(self, response):
		# Return an etree against which you can make queries
    
    def pop(self):
		# Return the next url to fetch
    
    def extend(self, urls, response):
		# These urls were discovered in response. Pick, choose, add to your list
		# Response is the `requests.Response` object returned, urls is a list of
		# string urls
    
    def recurse(self, response, tree):
		# Should we recurse on this page at all? As in, should we crawl any links
		# on this page? Response is the `requests.Response` object received, and
		# tree is an etree you might need in making a decision
    
    def dump(self, response, tree):
		# Return the value you want appended to the list of results returned from
		# `run()`. Response and tree arguments are same as above. Return None if
		# you don't want to append to the output
    
    def count(self, response, tree):
		# Should this page count against the max_pages count?

A `Crawl` object also has a method `run()`, which performs the crawl in a non-blocking
way in a greenlet, and returns a list of results from the crawl (determined by the
`dump()` method in the class). The `run()` method first fetches the seed url, finds
links, and then provides them to you to decide if you want to follow them.

Usage
=====
Hot damn! You can run it striaght from the interpreter (go ahead -- try it out):

	>>> from gcrawl import Crawl
	>>> c = Crawl('http://www.seomoz.org')
	>>> c.run()

This is probably a good way to debug for development. When it comes time to run the
thing in production, you'll want to have `qless` (which amounts to having Redis 2.6
installed) on a server somewhere, and then invoke `g-crawl-worker` (included when 
you install this package). It's based on work (and largely inherits from) the `qless-py`
worker to:

1. Fork itself and make use of multiple cores on your machine, and manages the child
	processes. If child processes exit, it spawns replacements.
2. Each process spawns a pool of greenlets to run crawls in a non-blocking way

The details of the invocation can be discussed further.