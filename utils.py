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
def hexdump(array, multilne = False, width = 30, prefix = "   "):

	if array == None:
		return "(no data)"

	if multilne:
		result = ""
		for i in range(0, len(array), width):
			buf = array[i:i + width]
			result += prefix
			result += ''.join('{:02x}'.format(x) for x in buf)
			result += "\n"
		return result
	else:
		return ''.join('{:02x}'.format(x) for x in array)


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


# Pad an ascihex string with a nibble in case it is "incomplete"
def pad_asciihex(string, front=False, padding='f'):

	if front and len(string) % 2 != 0:
		return padding + string
	elif len(string) % 2 != 0:
                return string + padding
	return string


# Swap nibbles of each byte in an array
def swap_nibbles(array):

	rc = []
	for a in array:
		rc.append(((a & 0xf0) >> 4) | ((a & 0x0f) << 4))
	return rc


# Convert from list of bytes to big-endian integer
def list_to_int(arr):
	return int(hexdump(arr), 16)


# Encode an integer number into list of bytes (e.g. 1025 becomes [4, 1])
def int_to_list(inp, num_bytes):
	out = []
	for i in range(0, num_bytes):
		shift_bits = ((num_bytes-1-i) * 8)
		out.append((inp >> shift_bits) & 0xFF)
	return out


# Lookup a string in a given table by its ID
def id_to_str(table, nr):
	dict_by_nr = dict(table)
	return dict_by_nr.get(nr) or '(invalid)'


# Convert a string back to its ID by looking it up in a given table
def str_to_id(table, string):
	dict_by_name = dict([(name.upper(), nr) for nr, name in table])
	id = dict_by_name.get(string.upper())

	if id is None:
		raise ValueError('identifier (\"%s\") not in table %s' % (string, str(table)))
	return id
