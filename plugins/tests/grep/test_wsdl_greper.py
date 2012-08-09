'''
test_wsdl_greper.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import unittest

import core.data.kb.knowledgeBase as kb

from core.data.url.httpResponse import httpResponse
from core.data.request.fuzzableRequest import fuzzableRequest
from core.controllers.misc.temp_dir import create_temp_dir
from core.data.parsers.urlParser import url_object
from core.controllers.coreHelpers.fingerprint_404 import fingerprint_404_singleton
from plugins.grep.wsdl_greper import wsdl_greper


class test_wsdl_greper(unittest.TestCase):

    def setUp(self):
        create_temp_dir()
        kb.kb.cleanup()
        fingerprint_404_singleton( [False, False, False] )
        self.plugin = wsdl_greper()
        self.url = url_object('http://www.w3af.com/')
        self.request = fuzzableRequest(self.url)

    def tearDown(self):
        self.plugin.end()
    
    def test_wsdl_greper_empty(self):
        body = ''
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.getData('wsdl_greper', 'wsdl')), 0 )
    
    def test_wsdl_greper_long(self):
        body = 'ABC ' * 10000
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.getData('wsdl_greper', 'wsdl')), 0 )
    
    def test_wsdl_greper_positive(self):
        body = 'ABC ' * 100
        body += '/s:sequence'
        body += '</br> ' * 50
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.getData('wsdl_greper', 'wsdl')), 1 )

    def test_wsdl_greper_positive_disco(self):
        body = 'ABC ' * 100
        body += 'disco:discovery '
        body += '</br> ' * 50
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.getData('wsdl_greper', 'disco')), 1 )
        self.assertEqual( len(kb.kb.getData('wsdl_greper', 'wsdl')), 0 )