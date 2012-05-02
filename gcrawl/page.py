#! /usr/bin/env python

from .url import Url
from lxml import etree

# The XPath functions available in lxml.etree do not include a lower()
# function, and so we have to provide it ourselves. Ugly, yes.
import string
def lower(dummy, l):
    return [string.lower(s) for s in l]

ns = etree.FunctionNamespace(None)
ns['lower'] = lower

class Page(object):
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
    banned = ''.join('[not(starts-with(normalize-space(@href),"%s:"))]' % sc for sc in banned_schemes)
    
    followableLinksXpath   = etree.XPath('//a[not(contains(lower(@rel),"nofollow"))]' + banned + '/@href')
    unfollowableLinksXpath = etree.XPath('//a[contains(lower(@rel),"nofollow")]' + banned + '/@href')
    allLinksXpath          = etree.XPath('//a' + banned + '/@href')
    
    def __init__(self, response):
        self.url      = response.url
        self.status   = response.status_code
        self.headers  = response.headers
        self.response = response
        self._content = ''
        self._tree    = None
    
    def __getstate__(self):
        # Make sure we get the content -- this will fire that
        self.content
        result = self.__dict__.copy()
        del result['response']
        return result
    
    def __getattr__(self, key):
        if key == 'content':
            self.content = self.response.content
            return self.content
        elif key == 'html':
            self.html = etree.fromstring(self.content, etree.HTMLParser(recover=True))
            return self.html
        elif key == 'xml':
            self.xml = etree.fromstring(self.content, etree.XMLParser(recover=True))
            return self.xml
        elif key == 'redirection':
            # This looks at both the Refresh header and the Location header
            self.redirection = self.headers.get('location')
            if self.redirection:
                self.redirection = Url.sanitize(self.redirection, self.url)
                return self.redirection
            
            rate, sep, self.redirection = self.headers.get('refresh', '').partition('=')
            if self.redirection:
                self.redirection = Url.sanitize(self.redirection, self.url)
            return self.redirection
        elif key == 'links':
            # Returns the links in the document that are followable and not:
            #         
            #     {
            #         'follow'  : [...],
            #         'nofollow': [...]
            #     }
            robots = ';'.join(self.metaRobotsXpath(self.html))
            base   = ''.join(self.baseXpath(self.html)) or self.url
            if 'nofollow' in robots:
                self.links = {
                    'follow'  : [],
                    'nofollow': [Url.sanitize(link, base) for link in self.allLinksXpath(self.html)]
                }
            else:
                self.links = {
                    'follow'  : [Url.sanitize(link, base) for link in self.followableLinksXpath(self.html)],
                    'nofollow': [Url.sanitize(link, base) for link in self.unfollowableLinksXpath(self.html)]
                }
            return self.links
    
    def text(self):
        '''Return all the text in the document, excluding tags'''
        raise NotImplementedError()
    