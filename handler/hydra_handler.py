#!/usr/bin/python3

##################################################
# hydra_handler.py :
#
# Fichier de classe de handler de l'outil hydraNFC
#
##################################################

import serial
import time

class HydraNFC():


    def __init__(self, port="COM6", timeout=0.3):
        self._port=port
        self._timeout=timeout

        self._serial=None


    def connect(self):
        self._serial=serial.Serial(self._port,timeout=self._timeout)

    def send(self,cmd,read=None):
        '''
	Send data to the TRF7970A chip
	
	0x05 -> TX timer low byte control
	0x00 -> Chip status control 
	'''
        self.cs_on()
        print("Sendind cmd -> "+''.join([hex(ord(i))[2:] for i in self.array_to_str(cmd)]))
        size = chr(len(cmd))
        resp_length = '\x00\x00'
        if read != None:
            resp_length = '\x00' + chr(read)
        self._serial.write(str.encode('\x05\x00' + size + resp_length))
        self._serial.write(str.encode(self.array_to_str(cmd)))
        status = self._serial.read(1)
        self.cmd_check_status(status)

        resp = None
        if read:
            print('4fun++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            resp = self.str_to_array(self._serial.read(read))
        if not(self.cs_off()):
            print('FAIL CS_OFF 1')
            exit(0)
        return resp
	
    def array_to_str(self, cmd):
        '''
        Concat the APDU cmd in one string
        '''
        return ''.join([chr(c) for c in cmd])
    def str_to_array(self,cmd):
        '''
        Change the string in a array
        '''
        return [ord(chr(i)) for i in cmd]
    def cs_on(self):
        '''
        Put the chip select pin at on,
        this operation is needed by the hydra
        see -> https://github.com/hydrabus/hydrafw/wiki/HydraFW-HydraNFC-TRF7970A-Tutorial
        Function take here -> https://github.com/hydrabus/hydrafw/blob/master/contrib/bbio_hydranfc/bbio_hydranfc_init.py
        '''
        print("CS On")
        self._serial.write(str.encode('\x02'))
        print('********************************************')
        status=self._serial.read(1)
        if status != b'\x01':
            print("CS-ON:")
            print(status)
            print("Error")
            print("")

    def cs_off(self):
        '''
        Put the chip select pin at off,
        this operation is needed by the hydra
        see -> https://github.com/hydrabus/hydrafw/wiki/HydraFW-HydraNFC-TRF7970A-Tutorial
        Function take here -> https://github.com/hydrabus/hydrafw/blob/master/contrib/bbio_hydranfc/bbio_hydranfc_init.py
        '''

        print("CS Off")
        self._serial.write(str.encode('\x03'))
        status=self._serial.read(1)
        if status != b'\x01':
            print("CS-OFF:")
            print(status)
            print("Error")
            print("")
            return False
        return True
    
    def field_on(self):
        self.send([0x00, 0x20])
        time.sleep(0.1)

    def field_off(self):
        self.send([0x00, 0x00])
        time.sleep(0.1)
    
    def cmd_check_status(self, status):
        '''
        Function to check the response status for a cmd
        Function take here -> https://github.com/hydrabus/hydrafw/blob/master/contrib/bbio_hydranfc/bbio_hydranfc_init.py
        '''
        if status != b'\x01':
            print(hex(status))
            return False
        print("Check status OK")
        return True
    
    def trf7970a_software_init(self):
        '''
        Initialize the chip software
        Function take here -> https://github.com/hydrabus/hydrafw/blob/master/contrib/bbio_hydranfc/bbio_hydranfc_init.py
        '''
        self.cs_on()
        self._serial.write(str.encode('\x05\x00\x02\x00\x00'))
        self._serial.write(str.encode('\x83\x83'))
        status=self._serial.read(1) # Read Status
        self.cmd_check_status(status)
        if not(self.cs_off()):
            print("CS_OFF 2")
            exit(0)
    
    def trf7970a_write_idle(self):
        '''
        Function take here -> https://github.com/hydrabus/hydrafw/blob/master/contrib/bbio_hydranfc/bbio_hydranfc_init.py
        '''
        self.cs_on()
        self._serial.write(str.encode('\x05\x00\x02\x00\x00'))
        self._serial.write(str.encode('\x80\x80'))
        status=self._serial.read(1) # Read Status
        self.cmd_check_status(status)
        if not(self.cs_off()):
            print('CS_OFF Faied 3')
            exit(0)
    
    def reset_config(self):
        """
        Perform a reset the TRF7970A chip used by the nfc shield.
        """
        cmd_lst_reset_hydra = [ [ 0x83, 0x83 ],
                    [ 0x00, 0x21 ],
                    [ 0x09, 0x00 ],
                    [ 0x0B, 0x87 ],
                    [ 0x0B, 0x87 ],
                    [ 0x8D, ],
                    [ 0x00, 0x00 ],
                    [ 0x0D, 0x3E ],
                    [ 0x14, 0x0F ],
                    ]

        print("Verification Configuration")
        if self.cs_off():
            print("Configuration Ok")
        else:
            print("Configuration issue, a reset will be perform")
            print ("RESET")
            self._serial.write(str.encode('\x00'))
            self._serial.write(str.encode('\x0F\n'))
            self._serial.readline()
            self._serial.readline()
            print("Re configuration")
            print("Configure the communication between GPIO and HydraBUS in spi")
            self._serial.write(str.encode("exit\n"))
            self._serial.readline()
            self._serial.readline()
            self._serial.readline()
            self._serial.readline()
            self._serial.write(str.encode("\n"))
            self._serial.readline()
            self._serial.readline()
            self._serial.write(str.encode("gpio pa3 mode out off\n"))
            self._serial.readline()
            self._serial.readline()
            self._serial.write(str.encode("gpio pa2 mode out on\n"))
            self._serial.readline()
            self._serial.readline()
            self._serial.write(str.encode("gpio pc0 mode out on\n"))
            self._serial.readline()
            self._serial.readline()
            self._serial.write(str.encode("gpio pc1 mode out on\n"))
            self._serial.readline()
            self._serial.readline()
            self._serial.write(str.encode("gpio pb11 mode out off\n"))
            self._serial.readline()
            self._serial.readline()
            time.sleep(0.02);
            self._serial.write(str.encode("gpio pb11 mode out on\n"))
            self._serial.readline()
            self._serial.readline()
            time.sleep(0.01);
            self._serial.write(str.encode("gpio pa2-3 pc0-1 pb11 r\n"))
            for cmpt in range(8):
                self._serial.readline()
            print("Configure hydra bus spi 2")
            for i in range(20):
                self._serial.write(str.encode("\x00"))

            if b'BBIO1' in self._serial.read(5):
                print("Into BBIO mode: OK")
                self._serial.readline()
            else:
                raise Exception("Could not get into bbIO mode")

            print("Switching to SPI mode:")
            self._serial.write(str.encode('\x01'))
            self._serial.read(4),
            self._serial.readline()

            print("Configure SPI2 polarity 0 phase 1:")
            self._serial.write(str.encode('\x83'))
            status=self._serial.read(1) # Read Status
            self.cmd_check_status(status)

            print("Configure SPI2 speed to 2620000 bits/sec:")
            self._serial.write(str.encode('\x63'))
            status=self._serial.read(1) # Read Status
            self.cmd_check_status(status)
            
            print("Reset hydra nfc...")
            self.trf7970a_software_init()
            self.trf7970a_write_idle()
            for offset in cmd_lst_reset_hydra:
                self.send(offset)
                time.sleep(0.1)
    


    def set_mode_iso14443A(self):
        """
        ISO Control register - 0x01 - see Table 6-6, [REF_DS_TRF7970A]
        """
        # [ 0x83] : command 0x03 : Software reinitialization => Power On Reset
        #
        # [0x09 0x31] *0x09 = 0x31
        #   Modulator and SYS_CLK Control register : 13.56 and 00K 100%
        #
        # [0x01 0x88]
        #   *0x01 = 0x88
        #   ISO Control Register :
        #       80 : Receiving without CRC : true
        #       08 : Active Mode
        #
        cmd_lst = [[ 0x83 ], [ 0x09, 0x31 ],
                    [ 0x01, 0x88 ]]

        print("Set HydraNFC to ISO 14443 A mode")
        for hit in cmd_lst:
            self.send(hit)
        self.send([0x41], 1)
    
    def set_mode_iso14443B(self):
        """
        ISO Control register - 0x01 - see Table 6-6, [REF_DS_TRF7970A]
        """
        # [ 0x83] : command 0x03 : Software reinitialization => Power On Reset
        #
        # [0x09 0x31] *0x09 = 0x31
        #   Modulator and SYS_CLK Control register : 13.56 and 00K 100%
        #
        # [0x01 0x0C]
        #   *0x01 = 0x0C
        #   0x01 -> 0X0C
        cmd_lst = [[0x83], [0x09, 0x31],
                    [0x01, 0x0C]]

        print("Set HydraNFC to ISO 14443 B mode")
        for hit in cmd_lst:
            self.send(hit)
        self.send([0x41], 1)
