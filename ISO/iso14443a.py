# Copyright (C) 2015 Guillaume VINET
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pynfcreader.sessions.tpdu import Tpdu
from pynfcreader.tools import utils
import time

class Iso14443ASession(object):
    
    def __init__(self, CID = 0, NAD = 0, device, block_size = 16):
        self._BlockNumber = 0 #Le numero du bloc que l'on veut lire
        self._NAD = NAD #Node Address
        self._CID = CID #Card Identifier
        self._addNAD = False
        self._addCID = True
        self._device = device
        self._iblock_pcb_number = 0x00
        self.set_block_size(block_size)

    def set_block_size(self, size):
        assert( 0 <= size <= 256)
        self._block_size = size

    def get_block_size(self):
        return self._block_size

    def get_and_update_iblock_pcb_number(self):
        self._iblock_pcb_number ^= 1
        return self._iblock_pcb_number ^ 1

    def send_reqa(self):
        """
        Send request for ISO Type A
        
        REQ A ---> 0x26
        """
        resp = self._device.send([ 0x8F, 0x90, 0x3D, 0x00, 0x0F, 0x26 ])
        
        time.sleep(0.01)
        
        resp = self._device.send([ 0x6C ],2)

        resp = self._device.send([ 0x5C ],1)

        if resp[0] == 0:
            raise Exception("REQ A has failed")

        resp = self._device.send([ 0x7F ],2)

        return resp

    def send_wupa(self):
        """
        Send Wake Up request for ISO Type A

        WUP A ---> 0x52
        """
        resp = self._device.send_wupa()


    def get_TagID(self, FSDI = "0", CID = "0"):
        uids=[]
        
        #Select cascade level 1
        
        #Set AntiCollision #1
        data = [0x93, 0x20]
        #Receive UID CLn
        resp = self._device.send(data,5)
        
        uids.append(resp)
        
        #send select #1
        data = [0x93, 0x70] + uids[-1]

        resp = self._device.send(data,3)


        uid=uids[0]

        #Tag ID isn't complete
        if uid[0] == 0x88:
            #Select cascade level 2

            #Set AntiCollision #2
            data = [0x95, 0x20]
            #Receive UID CLn
            resp = self._device.send(data,5)

            uids.append(resp)

            #Send select #2
            data = [0x95, 0x70] + uids[-1]

            resp = self._device.send(data,3)

            uid+=uids[-1]

            if uids[-1][0] == 0x88:
                #Select cascade level 3

                #Set AntiCollision #3
                data = [0x97, 0x20]
                #Receive UID CLn
                resp = self._device.send(data,3)

                uids.append(resp)

                #Send select #3
                data = [0x97, 0x70] + uids[-1]

                resp = self._device.send(data,3)

                uid+=uids[-1]

           
           resp=self.RATS(FSDI,CDI)


           return uid,resp

    def RATS(self, FSDI = "0", CID = "0"):
        """
        Request for answer to select - Type A
        
        see : http://www.gorferay.com/data-transmission-protocol-iso-iec-14-433-4/
        
        From pynfcreader

        return: ATS (Answer to select)
        """

        data = [0xE0, int(FSDI + CID, 16)]
        
        resp = self._device.send(data, 20)


        # resp[0] = TL = length without counting the 2 CRC bytes
        resp = resp[:resp[0]+2]

        T0 = resp[1]
        ta1 = None
        tb1 = None
        tc1 = None
        cmpt = 2
        if T0 & 0x10:
            ta1 = resp[cmpt]
            cmpt += 1
        if T0 & 0x20:
            tb1 = resp[cmpt]
            cmpt += 1
        if T0 & 0x40:
            tc1 = resp[cmpt]
            cmpt += 1

        if tc1:
            self._addNAD = ((tc1 & 0x01) == 0x01)
            self._addCID = ((tc1 & 0x02) == 0x02)

        return resp

    def send_pps(self, CID = 0x0, PPS1 = False, DRI = 0x0, DSI = 0x0):
        data = [ 0xD0, 0x11, 0x00 ]

        resp =  self._device.send(data, 3)

        return resp




    def get_rblock(self, ack = True, cid = True, block_number = None):

        pcb = 0xA2
        cid = ""
        if not ack:
            pcb |= 0x10

        if cid:
            pcb |= 0x08
            cid = " 0x%02X " % self._CID

        if block_number:
            pcb |= block_number
        else:
            pcb |= self.get_and_update_iblock_pcb_number()

        if cid != "":
            return [pcb, cid]
        else:
            return [pcb]


    def getIBlock(self, data, chaining_bit = False):
        """
         - 0
         - 0
         - 0
         - Chaining if 1
         - CID following if 1
         - NAD following if 1
         - 1
         - Block number

         from pynfcreader https://github.com/gvinet/pynfcreader
        """
        pcb =  self.get_and_update_iblock_pcb_number() + 0x02

        cid = ""
        if self._addCID:
            cid = self._CID
            pcb |= 0x08

        if chaining_bit:
            pcb |= 0x10

        nad = ""
        if self._addNAD:
            nad = self.__NAD
            pcb |= 0x04

        header = [pcb]
        if nad != "":
            header.append(nad)
        if cid != "":
            header.append(cid)

        return header + data

    def chaining_iblock(self, data = None, block_size = None):

        if not block_size:
            block_size = self.get_block_size()

        block_lst = []
        fields_lst = [data[i,i+block_size] for i in range(0,len(data),block_size)]
        for field in fields_lst[:-1]:
            frame = self.getIBlock(field, chaining_bit=True)
            block_lst.append(frame)

        frame = self.getIBlock(field_lst[-1], chaining_bit=False)
        block_lst.append(frame)

        return block_lst

    def _send_tpdu(self, tpdu):

        data = raw_to_data(tpdu)

        resp = self._device.send_raw(data, 16)

        resp = Tpdu(resp)
        
        return resp

    def raw_to_data(self,raw):
        bitslen = len(raw) << 4
        bitslen = [ bitslen >> 8, bitslen & 0xFF]
        bitslen.extend(raw)

        crc_field = 0x91
        data = [0x8F, crc_field, 0x3D]
        data.extend(bitslen)

        return data


    def send_apdu(self, apdu):
        '''
        For beeing sent, APDU are translated in TPDU
        '''
        apdu = self.convert_data(apdu)

        block_lst = self.chaining_iblock(data = apdu)
        resp_block_lst = []

        if len(block_lst) == 1:
            resp = self._send_tpdu(block_lst[0])

        else:
            for iblock in block_lst:
                resp = self._send_tpdu(iblock)

        while resp.is_wtx():
            wtx_reply = resp.get_wtx_reply()
            resp = self._send_tpdu(wtx_reply)

        rapdu = resp.get_inf_field()

        while resp.is_chaining():
            rblock = self.get_rblock()

            resp = self._send_tpdu(rblock)

            rapdu += resp.get_inf_field()

        return rapdu


    def convert_data(self, data):
        assert(isinstance(data, str))
        data = data.upper().strip().replace(" ", "")
        assert( (len(data) % 2) == 0 )
        convert = []
        for hit in range(0, len(data), 2):
            convert.append( int(data[hit:hit+2], 16) )
        return convert
