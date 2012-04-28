#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from gcrawl.url import Url

# An example of banned parameters, used for a few tests
banned = [
    'foobar',
    'widget',
    'wassup'
]

class TestParamSanitization(unittest.TestCase):
    ###########################################################################
    # Params
    #
    # In this context, params are urls with ';'-style parameters. Yes, they
    # really exist, and customers get piseed off when we don't honor them.
    ###########################################################################
    def test_pruning_with_other_params(self):
        '''Make sure we can strip out a single blacklisted param'''
        for b in banned:
            bad  = 'http://testing.com/page;%s=foo;ok=foo' % b
            good = 'http://testing.com/page;ok=foo'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_case_insensitivity_params(self):
        '''Make sure we can do it upper-cased'''
        for b in banned:
            bad  = 'http://testing.com/page;%s=foo;ok=foo' % b.upper()
            good = 'http://testing.com/page;ok=foo'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_all_together_params(self):
        '''And make sure we can remove all of the blacklisted query params'''
        params = ';'.join('%s=foo' % b for b in banned)
        bad    = 'http://testing.com/page;%s' % params
        good   = 'http://testing.com/page'
        self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_preserve_order_params(self):
        '''Make sure we keep it all in order'''
        for b in banned:
            bad  = 'http://testing.com/page;hi=low;hello=goodbye;%s=foo;howdy=doodeedoo;whats=up' % b
            good = 'http://testing.com/page;hi=low;hello=goodbye;howdy=doodeedoo;whats=up'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_pruning_alone_params(self):
        '''Make sure we don't include that ";"'''
        for b in banned:
            bad  = 'http://testing.com/page;%s=foo' % b
            good = 'http://testing.com/page'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)
    
    def test_param_values_ok_params(self):
        '''Make sure we can include them as param values'''
        for b in banned:
            ok   = 'http://testing.com/page;foo=%s;ok=foo' % b
            self.assertEqual(Url.sanitize(ok), ok)
    
    def test_prefix_param_ok_params(self):
        '''Make sure we can give each blacklisted param a prefix'''
        for b in banned:
            ok   = 'http://testing.com/page;howdy_%s=foo;ok=foo' % b
            self.assertEqual(Url.sanitize(ok), ok)


class TestQuerySanitization(unittest.TestCase):
    ###########################################################################
    # Query
    #
    # In this context, query strings are after a ? and are joined with ampersands
    # For more,
    #   http://tools.ietf.org/html/rfc1808.html
    ###########################################################################
    def test_pruning_with_other_args(self):
        '''Make sure we can strip out a single blacklisted query'''
        for b in banned:
            bad  = 'http://testing.com/page?%s=foo&ok=foo' % b
            good = 'http://testing.com/page?ok=foo'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_case_insensitivity(self):
        '''Make sure we can do it upper-cased'''
        for b in banned:
            bad  = 'http://testing.com/page?%s=foo&ok=foo' % b.upper()
            good = 'http://testing.com/page?ok=foo'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_all_together(self):
        '''And make sure we can remove all of the blacklisted query params'''
        params = '&'.join('%s=foo' % b for b in banned)
        bad    = 'http://testing.com/page?%s' % params
        good   = 'http://testing.com/page'
        self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_preserve_order(self):
        '''Make sure we keep it all in order'''
        for b in banned:
            bad  = 'http://testing.com/page?hi=low&hello=goodbye&%s=foo&howdy=doodeedoo&whats=up' % b
            good = 'http://testing.com/page?hi=low&hello=goodbye&howdy=doodeedoo&whats=up'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)

    def test_pruning_alone(self):
        '''Make sure we don't include that "?"'''
        for b in banned:
            bad  = 'http://testing.com/page?%s=foo' % b
            good = 'http://testing.com/page'
            self.assertEqual(Url.sanitize(bad, param_blacklist=banned), good)
    
    def test_param_values_ok(self):
        '''Make sure we can include them as query values'''
        for b in banned:
            ok   = 'http://testing.com/page?foo=%s&ok=foo' % b
            self.assertEqual(Url.sanitize(ok), ok)
    
    def test_prefix_param_ok(self):
        '''Make sure we can give each blacklisted param a prefix'''
        for b in banned:
            ok   = 'http://testing.com/page?howdy_%s=foo&ok=foo' % b
            self.assertEqual(Url.sanitize(ok), ok)
    
    def test_multiple_ampersands(self):
        paths = [
            ('howdy?&&'              , 'howdy'),
            ('howdy?&&&foo=bar&&&'   , 'howdy?foo=bar'),
            ('howdy;;;;foo=bar;'     , 'howdy;foo=bar'),
            # These come from the prototype lsapi: https://github.com/seomoz/lsapi-prototype/blob/master/tests/test_convert_url.py
            # In query parameters, we should escape these characters
            #('?foo=\xe4\xb8\xad'    , '?foo=%E4%B8%AD'),
            # But in a path, we should not
            #('\xe4\xb8\xad/bar.html', '\xe4\xb8\xadbar.html')
        ]
        
        base = 'http://testing.com/'
        for bad, clean in paths:
            self.assertEqual(Url.sanitize(base + bad), base + clean)

class TestRelative(unittest.TestCase):
    ###########################################################################
    # Relative url support tests
    ###########################################################################    
    def test_case_insensitivity(self):
        paths = [
            ('www.TESTING.coM'       , 'www.testing.com/'),
            ('WWW.testing.com'       , 'www.testing.com/'),
            ('WWW.testing.COM/FOOBAR', 'www.testing.com/FOOBAR')
        ]
        
        for bad, clean in paths:
            self.assertEqual(Url.sanitize('http://' + bad), 'http://' + clean)
    
    def test_double_forward_slash(self):
        paths = [
            ('howdy'           , 'howdy'),
            ('hello//how//are' , 'hello/how/are'),
            ('hello/../how/are', 'how/are'),
            ('hello//..//how/' , 'how/'),
            ('a/b/../../c'     , 'c'),
            ('../../../c'      , 'c'),
            ('./hello'         , 'hello'),
            ('./././hello'     , 'hello'),
            ('a/b/c/'          , 'a/b/c/')
        ]
        
        base = 'http://testing.com/'
        
        for bad, clean in paths:
            self.assertEqual(Url.sanitize(base + bad), base + clean)
        
        # This is the example from the wild that spawned this whole change
        bad   = 'http://www.vagueetvent.com/../fonctions_pack/ajouter_pack_action.php?id_produit=26301'
        clean = 'http://www.vagueetvent.com/fonctions_pack/ajouter_pack_action.php?id_produit=26301'
        self.assertEqual(Url.sanitize(bad), clean)
    
    def test_insert_trailing_slash(self):
        # When dealing with a path-less url, we should insert a trailing slash.
        paths = [
            ('foo.com?page=home', 'foo.com/?page=home'),
            ('foo.com'          , 'foo.com/')
        ]
        
        for bad, clean in paths:
            self.assertEqual(Url.sanitize('http://' + bad), 'http://' + clean)




class TestTheRest(unittest.TestCase):
    def test_join(self):
        # We should be able to join urls
        self.assertEqual(Url.sanitize('/foo', 'http://cnn.com'), 'http://cnn.com/foo')
    
    def test_escaping(self):
        paths = [
            ('hello%20and%20how%20are%20you', 'hello%20and%20how%20are%20you'),
            ('danny\'s pub'                 , 'danny%27s%20pub'),
            ('danny%27s pub?foo=bar&yo'     , 'danny%27s%20pub?foo=bar&yo')
        ]
        
        base = 'http://testing.com/'
        for bad, clean in paths:
            self.assertEqual(Url.sanitize(base + bad), base + clean)
    
    def test_wild(self):
        # These are some examples from the wild that have been seeming to fail
        # It apparently comes from the fact that the input is a unicode string,
        # and has disallowed character
        pairs = [
            (u'http://www.jointingmortar.co.uk/rompox®-easy.html',
                'http://www.jointingmortar.co.uk/rompox%C2%AE-easy.html'),
            (u'http://www.dinvard.se//index.php/result/type/owner/Stift Fonden för mindre arbetarbos/',
                'http://www.dinvard.se/index.php/result/type/owner/Stift%20Fonden%20f%C3%B6r%20mindre%20arbetarbos/'),
            (u'http://www.ewaterways.com/cruises/all/alaska//ship/safari quest/itinerary/mexico\'s sea of cortés - aquarium of the world (8 days)/itinerary/',
                'http://www.ewaterways.com/cruises/all/alaska/ship/safari%20quest/itinerary/mexico%27s%20sea%20of%20cort%C3%A9s%20-%20aquarium%20of%20the%20world%20%288%20days%29/itinerary/'),
            (u'http://www.mydeals.gr/prosfores/p/Υπόλοιπα%20Νησιά/',
                'http://www.mydeals.gr/prosfores/p/%CE%A5%CF%80%CF%8C%CE%BB%CE%BF%CE%B9%CF%80%CE%B1%20%CE%9D%CE%B7%CF%83%CE%B9%CE%AC/')
        ]
        
        for bad, good in pairs:
            self.assertEqual(Url.sanitize(bad), good)
    
unittest.main()
