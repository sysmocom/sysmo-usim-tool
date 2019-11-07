#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import *
from sysmo_isim_sja2 import *


	
if __name__ == "__main__":

	print("HELLO EF_SIM_AUTH_KEY!")
	myfile = SYSMO_ISIMSJA2_FILE_EF_SIM_AUTH_KEY()
	print myfile
	myfile.use_opc = True
	myfile.sres_dev_func = 2
	myfile.opc = [0x23] * 16
	myfile.key = [0x42] * 16
	print myfile
	myfile2 = SYSMO_ISIMSJA2_FILE_EF_SIM_AUTH_KEY(myfile.encode())
	print myfile2

	print("=========================================================")



	myfile = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G()
	print myfile

	myfile.algo = SYSMO_ISIMSJA2_ALGO_MILENAGE;
	myfile.sres_dev_func = 2
	myfile.opc = [0x23] * 16
	myfile.key = [0x42] * 16
	print myfile

	myfile2 = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(myfile.encode())
	print myfile2

	
	print("==========================================================")



	myfile = SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG()
	print myfile

	myfile.R1 = 0xAA
	myfile.R2 = 0xBB
	myfile.R3 = 0xCC
	myfile.R4 = 0xDD
	myfile.R5 = 0xEE
	myfile.C1 = [0xDE] * 16
	myfile.C2 = [0xAD] * 16
	myfile.C3 = [0xBE] * 16
	myfile.C4 = [0xEF] * 16
	myfile.C5 = [0x12] * 16

	
	print myfile

	myfile2 = SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG(myfile.encode())
	print myfile2


	print("==========================================================")

	myfile = SYSMO_ISIMSJA2_FILE_EF_USIM_SQN()
	print myfile
	print myfile.encode()

	myfile2 = SYSMO_ISIMSJA2_FILE_EF_USIM_SQN(myfile.encode())
	print myfile2
	print myfile2.encode()



