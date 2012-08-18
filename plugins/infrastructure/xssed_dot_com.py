'''
xssed_dot_com.py

Copyright 2006 Andres Riancho

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
import re
import urllib2

import core.controllers.outputManager as om
import core.data.kb.knowledgeBase as kb
import core.data.kb.vuln as vuln
import core.data.constants.severity as severity

from core.controllers.basePlugin.baseInfrastructurePlugin import baseInfrastructurePlugin
from core.controllers.w3afException import w3afRunOnce, w3afException
from core.controllers.misc.decorators import runonce
from core.data.parsers.urlParser import url_object


class xssed_dot_com(baseInfrastructurePlugin):
    '''
    Search in xssed.com to find xssed pages.
    
    @author: Nicolas Crocfer (shatter@shatter-blog.net)
    @author: Fix: Set "." in front of the root domain to limit the search - Raul Siles
    '''    
    def __init__(self):
        baseInfrastructurePlugin.__init__(self)
        
        #
        #   Could change in time,
        #
        self._xssed_url = url_object("http://www.xssed.com")
        self._fixed = "<img src='http://data.xssed.org/images/fixed.gif'>&nbsp;FIXED</th>"
    
    @runonce(exc_class=w3afRunOnce)
    def discover(self, fuzzableRequest ):
        '''
        Search in xssed.com and parse the output.
        
        @parameter fuzzableRequest: A fuzzableRequest instance that contains 
                                    (among other things) the URL to test.
        '''
        target_domain = fuzzableRequest.getURL().getRootDomain()

        try:
            check_url = self._xssed_url.urlJoin("/search?key=." + target_domain)
            response = self._uri_opener.GET( check_url )
        except w3afException, e:
            msg = 'An exception was raised while running xssed_dot_com plugin.'
            msg += 'Exception: "%s".' % e
            om.out.debug( msg )
        else:
            #
            #   Only parse the xssed result if we have it,
            #
            try:
                return self._parse_xssed_result( response )
            except w3afException, e:
                self._exec = True
                msg = 'An exception was raised while running xssed_dot_com plugin. '
                msg += 'Exception: "%s".' % e
                om.out.debug( msg )

    def _decode_xssed_url(self, url):
        '''
        Replace the URL in the good format.
        
        @return: None
        '''
        url = url.replace('<br>', '')
        url = url.replace('</th>', '')
        url = url.replace('URL: ', '')
        url = url.replace('\r', '')
        url = url.replace('&lt;', '<')
        url = url.replace('&gt;', '>')
        url = url.replace('&quot;', '\'')
        url = url.replace('&amp;', '&')
        return urllib2.unquote(url)
    
    def _parse_xssed_result(self, response):
        '''
        Parse the result from the xssed site and create the corresponding info
        objects.
        
        @return: Fuzzable requests pointing to the XSS (if any)
        '''
        html_body = response.getBody()
        
        if "<b>XSS:</b>" in html_body:
            #
            #   Work!
            #
            regex_many_vulns = re.findall("<a href='(/mirror/\d*/)' target='_blank'>", html_body)
            for mirror_relative_link in regex_many_vulns:
                
                mirror_url = self._xssed_url.urlJoin( mirror_relative_link )
                xss_report_response = self._uri_opener.GET( mirror_url )
                matches = re.findall("URL:.+", xss_report_response.getBody())
                
                v = vuln.vuln()
                v.setPluginName(self.getName())
                v.setName('Possible XSS vulnerability')
                v.setURL( mirror_url )
                
                if self._fixed in xss_report_response.getBody():
                    v.setSeverity( severity.LOW )
                    msg = 'This script contained a XSS vulnerability: "'
                    msg += self._decode_xssed_url( self._decode_xssed_url(matches[0]) ) +'".'
                else:
                    v.setSeverity( severity.HIGH )
                    msg = 'According to xssed.com, this script contains a XSS vulnerability: "'
                    msg += self._decode_xssed_url( self._decode_xssed_url(matches[0]) ) +'".'

                v.setDesc( msg )
                kb.kb.append( self, 'xss', v )
                om.out.information( v.getDesc() )
                
                #
                #   Add the fuzzable request, this is useful if I have the XSS plugin enabled
                #   because it will re-test this and possibly confirm the vulnerability
                #
                fuzzable_requests = self._create_fuzzable_requests( xss_report_response )
                return fuzzable_requests
        else:
            #   Nothing to see here...
            om.out.debug('xssed_dot_com did not find any previously reported XSS vulnerabilities.')

        return []

                
    def getLongDesc( self ):
        return '''
        This plugin searches the xssed.com database and parses the result. The
        information stored in that database is useful to know about previous XSS
        vulnerabilities in the target website.
        '''