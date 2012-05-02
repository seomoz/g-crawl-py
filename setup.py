#! /usr/bin/env python
#
# Copyright (c) 2011 SEOmoz
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

try:
	from setuptools import setup
	extra = {
		'install_requires' : ['reppy', 'urllib3', 'requests', 'gevent']
	}
except ImportError:
	from distutils.core import setup
	extra = {
		'dependencies' : ['reppy', 'urllib3', 'requests', 'gevent']
	}

setup(name       = 'gcrawl',
	version      = '0.1.0',
	description  = 'Fetch urls. Faster.',
	url          = 'http://github.com/seomoz/g-crawl-py',
	author       = 'Dan Lecocq',
	author_email = 'dan@seomoz.org',
	license      = 'MIT',
	packages     = ['gcrawl'],
	classifiers  = [
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Topic :: Internet :: WWW/HTTP'
	],
	**extra
)