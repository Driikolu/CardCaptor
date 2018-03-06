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
    def trf7970a_software_init(self):
        self._serial.write('\x05\x00\x02\x00\x00')
        self._serial.write('\x83\x83')

    def trf7970a_write_idle(self):
        self._serial.write('\x05\x00\x02\x00\x00')
        self._serial.write('\x80\x80')
    def reset_hydra_nfc(self):
        """
        Perform a reset the TRF7970A chip used by the nfc shield.
        """
        cmd_lst = [ [ 0x83, 0x83 ],
                    [ 0x00, 0x21 ],
                    [ 0x09, 0x00 ],
                    [ 0x0B, 0x87 ],
                    [ 0x0B, 0x87 ],
                    [ 0x8D, ],
                    [ 0x00, 0x00 ],
                    [ 0x0D, 0x3E ],
                    [ 0x14, 0x0F ],
                    ]

        self.trf7970a_software_init()
        self.trf7970a_write_idle()
        for offset in cmd_lst:
            self.send(offset)
            time.sleep(0.1)

