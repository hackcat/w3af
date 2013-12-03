'''
test_bloomfilter_impl_selection.py

Copyright 2006 Andres Riancho

This file is part of w3af, http://w3af.org/ .

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

from nose.plugins.attrib import attr
from w3af.core.data.bloomfilter.bloomfilter import BloomFilter
from pybloomfilter import BloomFilter as CMmapFilter


class TestImplementationSelection(unittest.TestCase):

    @attr('ci_fails')
    def test_correct_type(self):
        _filter = BloomFilter(1000, 0.01)
        self.assertIsInstance(_filter.bf, CMmapFilter)