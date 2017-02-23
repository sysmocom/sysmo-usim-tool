#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Smartcard Terminal IO Class

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

from smartcard.scard import *
import smartcard.util
from utils import *

# The following class abstract the terminal, however we reference it as "Card",
# because the terminal itsslef is not in the users interest, we are focussed
# on the card all the time. The abstraction done here is very simple and
# implements only the very basic functionality to communicate with a smartcard
# on APDU level.
#
# The classes Card_res_apdu and Card_apdu are helper classes in order to make
# passing the parameters/results simpler. They are not meant to be created
# anwhere else in the code. All handling is done through the Card class.
#
# The method apdu formats an APDU with its basic features (CLA, INS etc..)
# for the user. The user also may set an expected status word (Default is
# 0x9000). The status word is then checked when the transaction is performed
# using the transact method.
#
# The expected status word is a list of two bytes, each of the two bytes may be
# set to None. If this is the case the byte is not checked. If the whole list
# is set to none, the status word is not checked at all. If the status word
# check fails, the swok flag inside the repsonse apdu is set to false and an
# exception is thwron unless the strict parameter is not set to False.
#
# The user may set a dry-flag when calling the transact, then the transaction
# is not performed. Only the log line is printed. This is to verify if the
# transaction would be sent correctly, as some smartcad operations might
# be risky.


# Note: Programmed with the help of a blogpost from Ludovic Rousseau:
# https://ludovicrousseau.blogspot.de/2010/04/pcsc-sample-in-python.html

# A class to make handling of the responses a little simpler
# Note: Do not use directly, Card object will return responses.
class Card_res_apdu():

	apdu = None
	sw = None
	swok = True
	def __init__(self, apdu, sw):
		self.apdu = apdu
		self.sw = sw

	def __str__(self):
		dump = "APDU:" + hexdump(self.apdu)
		dump += " SW:" + hexdump(self.sw)
		return dump


# A class to make handling of the card input a little simpler
# Note: Do not use directly, use Card.apdu(...) instead
class Card_apdu():

	apdu = None
	sw = None
	def __init__(self, cla, ins, p1, p2, p3, data, sw):
		self.apdu = [cla, ins, p1, p2, p3]
		if data:
			self.apdu += data
		self.sw = sw

	def __str__(self):
		dump = "APDU:" + hexdump(self.apdu)
		return dump


# A class to abstract smartcard and terminal
class Card():

	card = None
	protocol = None
	verbose = None

	# Constructor: Set up connection to smartcard
	def __init__(self, verbose = False):

		self.verbose = verbose

		# Eestablish a smartcard terminal context
		hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
		if hresult != SCARD_S_SUCCESS:
			print " * Error: Unable to establish smartcard terminal context -- exiting"
			exit(1)

		# Select the next available smartcard terminal
		hresult, terminals = SCardListReaders(hcontext, [])
	        if hresult != SCARD_S_SUCCESS or len(terminals) < 1:
			print " * Error: No smartcard terminal found -- exiting"
			exit(1)
		terminal = terminals[0]
		print " * Terminal:", terminal

		# Establish connection to smartcard
		hresult, hcard, dwActiveProtocol = SCardConnect(hcontext,
			terminal, SCARD_SHARE_SHARED,
			SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
		if hresult != SCARD_S_SUCCESS:
			print " * Error: No smartcard detected -- exiting"
			exit(1)
		print " * Protocol: " + str(dwActiveProtocol)
		self.card = hcard
		self.protocol = dwActiveProtocol


	# Print debug info
	def __debug_print(self, message):
		if self.verbose:
			print message


	# Perform smartcard transaction
	def transact(self, apdu, dry = False, strict = True):

		# Dry run
		if (dry):
			self.__debug_print("   Card transaction: " + str(apdu)
				+ " ==> Dry run: Transaction not executed")
			return Card_res_apdu(None,None)

		# Perform transaction
		hresult, response = SCardTransmit(self.card,
			self.protocol, apdu.apdu)
		if hresult != SCARD_S_SUCCESS:
			self.__debug_print(" * Card transaction: " + str(apdu)
				+ " ==> Error: Smartcard transaction failed")
			return Card_res_apdu(None,None)
		res = Card_res_apdu(response[:-2],response[-2:])

		self.__debug_print("   Card transaction: " + str(apdu)
			+ " ==> " + str(res))

		# Check status word
		if apdu.sw:
			if apdu.sw[0] and apdu.sw[0] == res.sw[0]:
				res.swok = True
			elif apdu.sw[0]:
				res.swok = False
				self.__debug_print(" * Warning: Unexpected status word (SW1)!")

			if apdu.sw[1] and apdu.sw[1] == res.sw[1]:
				res.swok = True
			elif apdu.sw[1]:
				res.swok = False
				self.__debug_print(" * Warning: Unexpected status word (SW2)!")

		# If strict mode is turned on, the status word must match,
		# otherwise an exception is thrown
		if strict and res.swok == False:
			raise ValueError('Transaction failed!')
			
		return res


	# set up a new APDU
	def apdu(self, cla, ins, p1 = 0x00, p2 = 0x00, p3 = 0x00,
		data = None, sw = [0x90, 0x00]):
		return Card_apdu(cla, ins, p1, p2, p3, data, sw)

		
