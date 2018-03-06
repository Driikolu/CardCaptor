#!/usr/bin/python3

##################################################
# hydra_handler.py :
#
# Fichier de classe de handler de l'outil hydraNFC
#
##################################################

import serial

class HydraNFC():

    def __init__(self, port="/dev/ttyACM0", timeout=0,3):
        self._port=port
        self._timeout=timeout

        self._serial=None


    def connect(self):
        self._serial=serial.Serial(self._port,timeout=self._timeout)

    def send(self,cmd):
	'''
	Send data to the TRF7970A chip
	
	0x05 -> TX timer low byte control
	0x00 -> Chip status control 
	'''
	size = chr(len(cmd))
	self._serial.write('\x05\x00' + size + '\x00\x00') 
	self._serial.write(self.array_to_str(cmd))
	
	
    def array_to_str(self, cmd):
	'''
	Concat the APDU cmd in one string
	'''
        return ''.join([chr(c) for c in cmd])

    def field_on(self):
        self.send([0x00, 0x20])
        time.sleep(0.1)

    def field_off(self):
        self.send([0x00, 0x00])
        time.sleep(0.1)
