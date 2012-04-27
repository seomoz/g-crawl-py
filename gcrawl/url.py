#! /usr/bin/env python

import re
import reppy
import urllib
import urlparse

class Url(object):
    # Link types. Links can be considered any of these types, relative to 
    # one another:
    #
    #   internal  => On the same domain
    #   external  => On a different domain
    #   subdomain => Same top-level domain, but one is a subdomain of the other
    internal  = 1
    external  = 2
    subdomain = 3
    
    @staticmethod
    def sanitize(url, base=None, param_blacklist=None):
        '''Given a url, and optionally a base and a parameter blacklist,
        sanitize the provided url. This includes removing blacklisted 
        parameters, relative paths, and more.
        
        For more information on how and what we parse / sanitize:
            http://tools.ietf.org/html/rfc1808.html
        The more up-to-date RFC is this one:
            http://www.ietf.org/rfc/rfc3986.txt'''
        
        # Parse the url once it has been evaluated relative to a base
        p = urlparse.urlparse(urlparse.urljoin(url, base or ''))
        
        # And remove all the black-listed query parameters
        query = '&'.join(q for q in p.query.split('&') if q.partition('=')[0].lower() not in (param_blacklist or ()))
        query = re.sub(r'^&|&$', '', re.sub(r'&{2,}', '&', query))
        # And remove all the black-listed param parameters
        params = ';'.join(q for q in p.params.split(';') if q.partition('=')[0].lower() not in (param_blacklist or ()))
        params = re.sub(r'^;|;$', '', re.sub(r';{2,}', ';', params))
        
        # Remove double forward-slashes from the path
        path  = re.sub(r'\/{2,}', '/', p.path)
        # With that done, go through and remove all the relative references
        unsplit = []
        for part in path.split('/'):
            # If we encounter the parent directory, and there's
            # a segment to pop off, then we should pop it off.
            if part == '..' and (not unsplit or unsplit.pop() != None):
                pass
            elif part != '.':
                unsplit.append(part)
        
        # With all these pieces, assemble!
        path = '/'.join(unsplit)
        if p.netloc:
            path = path or '/'
        
        if isinstance(path, unicode):
            path = urllib.quote(urllib.unquote(path.encode('utf-8')))
        else:
            path = urllib.quote(urllib.unquote(path))
        
        return urlparse.urlunparse((p.scheme, re.sub(r'^\.+|\.+$', '', p.netloc.lower()), path, params, query, p.fragment)).replace(' ', '%20')
    
    @staticmethod
    def allowed(url, useragent, headers=None, meta_robots=None):
        '''Given a url, a useragent and optionally headers and a dictionary of
        meta robots key-value pairs, determine whether that url is allowed or not.
        
        The headers must be a dictionary mapping of string key to list value:
        
            {
                'Content-Type': ['...'],
                'X-Powered-By': ['...', '...']
            }
        
        The meta robots must be provided as a mapping of string key to directives:
        
            {
                'robots': 'index, follow',
                'foobot': 'index, nofollow'
            }
        '''
        # First, check robots.txt
        r = reppy.findRobot(url)
        allowed = (r == None) or r.allowed(url, useragent)
        
        # Next, check the X-Robots-Tag
        # There can be multiple instances of X-Robots-Tag in the headers, so we've
        # joined them together with semicolons. Now, make a dictionary of each of
        # the directives we found. They can be specific, in which case it's in the
        # format:
        #   botname : directive
        # In the absence of a botname, it applies to all bots. Strictly speaking,
        # there is one directive that itself has a value, but as we're not interested
        # in it (it's the unavailable_after directive), it's ok to ignore it.
        if headers:
            for bot in headers.get('x-robots-tag', []):
                botname, sep, directive = bot.partition(':')
                if directive and botname == useragent:
                    # This is when it applies just to us
                    allowed = allowed and ('noindex' not in directive) and ('none' not in directive)
                else:
                    # This is when it applies to all bots
                    allowed = allowed and ('noindex' not in botname) and ('none' not in botname)
        
        # Now check for specific and general meta tags
        # In this implementation, specific meta tags override general meta robots
        if meta_robots:
            s = meta_robots.get(useragent, '') + meta_robots.get('robots', '')
            allowed = allowed and ('noindex' not in s) and ('none' not in s)
        
        return allowed
    
    @staticmethod
    def relationship(frm, to):
        '''Determine the relationship of the link `to` found on url `frm`.
        For example, the relationship between these urls is `internal`:
            http://foo.com/bar
            http://foo.com/howdy
        
        And `external`:
            http://foo.com/bar
            http://bar.com/foo
        
        And `subdomain`:
            http://foo.com/
            http://bar.foo.com/
        '''
        return 0