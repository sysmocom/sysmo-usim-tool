#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A collection of useful routines to make this tool work

(C) 2017 by Sysmocom s.f.m.c. GmbH
All Rights Reserved

Author: Philipp Maier

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Convert list to an printable ascii hex string
def hexdump(array):
	if array:
		return ''.join('{:02x}'.format(x) for x in array)
	else:
		return "(no data)"


# Convert ascii string with decimal numbers to numeric ascii-code list
def ascii_to_list(string):
	rc = []
	for c in string:
		rc.append(ord(c))
	return rc


# Convert an ascii hex string to numeric list
def asciihex_to_list(string):

	string = string.translate(None, ':')
	try:
		return map(ord, string.decode("hex"))
	except:
		print "Warning: Invalid hex string -- ignored!"
		return []
