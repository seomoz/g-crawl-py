#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from gcrawl.url import Url

class TestParamSanitization(unittest.TestCase):
    # In these tests, we're going to assume that reppy's unit tests
    # are working properly
    def test_x_robots_header(self):
        examples = [
            (['noindex']     , False),
            (['none']        , False),
            (['noindex,none'], False),
            (['index']       , True ),
            (['foobot:index'], True ),
            (['foobot:none' ], False),
            (['barbar:index'], True ),
            (['barbot:none' ], True )
        ]
        for line in examples:
            e, result = line
            d = {
                'x-robots-tag': e
            }
            self.assertEqual(Url.allowed('http://www.seomoz.org/', 'foobot', headers=d), result)
    
    def test_meta_robots(self):
        pass
    
unittest.main()
