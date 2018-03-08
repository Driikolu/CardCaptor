#!/usr/bin/python3

##################################################
# hydra_handler.py :
#
# Fichier de classe de handler de l'outil hydraNFC
#
##################################################

import serial

class HydraNFC():

    def __init__(self, port="/dev/ttyACM0", timeout=0.3):
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
	self.cs_on()
	size = chr(len(cmd))
	self._serial.write('\x05\x00' + size + '\x00\x00') 
	self._serial.write(self.array_to_str(cmd))
	self.cd_off()
	
    def array_to_str(self, cmd):
	'''
	Concat the APDU cmd in one string
	'''
        return ''.join([chr(c) for c in cmd])

    def cs_on(self):
    '''
	Put the chip select pin at on,
        this operation is needed by the hydra
        see -> https://github.com/hydrabus/hydrafw/wiki/HydraFW-HydraNFC-TRF7970A-Tutorial
    '''
        print("CS On")
        self._serial.write('\x02')
        status=self._serial.read(1)
        if status != '\x01':
            print("CS-ON:")
            print(status.encode('hex'))
            print("Error")
            print("")

    def cs_off(self):
    '''
        Put the chip select pin at off,
        this operation is needed by the hydra
        see -> https://github.com/hydrabus/hydrafw/wiki/HydraFW-HydraNFC-TRF7970A-Tutorial
    '''

        print("CS Off")
        self._serial.write('\x03')
        status=self._serial.read(1)
        if status != '\x01':
            print("CS-OFF:")
            print(status.encode('hex'))
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
    def trf7970a_software_init(self):
	self.cs_on()
        self._serial.write('\x05\x00\x02\x00\x00')
        self._serial.write('\x83\x83')
	self.cs_off()
    def trf7970a_write_idle(self):
	self.cs_on()
        self._serial.write('\x05\x00\x02\x00\x00')
        self._serial.write('\x80\x80')
	self.cs_off()
    def reset_config(self):
        """
        Perform a reset the TRF7970A chip used by the nfc shield.
        """
        cmd_lst_hydra = [ [ 0x83, 0x83 ],
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
	    self._serial.write('\x00')
            self._serial.write('\x0F\n')
            self._serial.readline()
            self._serial.readline()
            print("Re configuration")
            print("Configure the communication between GPIO and HydraBUS in spi")
            self._serial.write("exit\n")
            self._serial.readline()
            self._serial.readline()
            self._serial.readline()
            self._serial.readline()
            self._serial.write("\n")
            self._serial.readline()
            self._serial.readline()
            self._serial.write("gpio pa3 mode out off\n")
            self._serial.readline()
            self._serial.readline()
            self._serial.write("gpio pa2 mode out on\n")
            self._serial.readline()
            self._serial.readline()
            self._serial.write("gpio pc0 mode out on\n")
            self._serial.readline()
            self._serial.readline()
            self._serial.write("gpio pc1 mode out on\n")
            self._serial.readline()
            self._serial.readline()
            self._serial.write("gpio pb11 mode out off\n")
            self._serial.readline()
            self._serial.readline()
            time.sleep(0.02);
            self._serial.write("gpio pb11 mode out on\n");
            self._serial.readline()
            self._serial.readline()
            time.sleep(0.01);
            self._serial.write("gpio pa2-3 pc0-1 pb11 r\n");
            for cmpt in range(8):
                self._serial.readline()
            print("Configure hydra bus spi 2")
	    for i in xrange(20):
                self._serial.write("\x00")

            if "BBIO1" in self._serial.read(5):
                print("Into BBIO mode: OK")
                self._serial.readline()
            else:
                raise Exception("Could not get into bbIO mode")

            print("Switching to SPI mode:")
            self._serial.write('\x01')
            self._serial.read(4),
            self._serial.readline()

            print("Configure SPI2 polarity 0 phase 1:")
            self._serial.write('\x83')
            status=self._serial.read(1) # Read Status
            self.cmd_check_status(status)

            print("Configure SPI2 speed to 2620000 bits/sec:")
            self._serial.write('\x63')
            status=self._serial.read(1) # Read Status
            self.cmd_check_status(status)
            
	    print("Reset hydra nfc...")
            self.__reset_hydra_nfc()
            self.__logger.info("")
            self.trf7970a_software_init()
            self.trf7970a_write_idle()
            for offset in cmd_lst_hydra:
                self.send(offset)
                time.sleep(0.1)
    def cmd_check_status(self, status):
        if status != '\x01':
            print status.encode('hex'),
            self.__logger.info("Check status error")
            return False
        print("Check status OK")
        return True

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
