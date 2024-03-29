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

from handler.hydra_handler import HydraNFC
from ISO.iso14443a import Iso14443ASession

class ReaderHydraNFC(object):

    def __init__(self, port="COM8", debug_mode=True, block_size = 16):
        self.__driver = HydraNFC(port=port)
        self.__session = Iso14443ASession(device=self.__driver, block_size= block_size)

    def connect(self):
        self.__driver.connect()
        self.__driver.reset_config()
        self.__driver.set_mode_iso14443A()

    def field_on(self):
        print("Field on")
        self.__driver.field_on()

    def field_off(self):
        print("Field off")
        self.__driver.field_off()

    def polling(self):
        self.__session.send_reqa()
        self.__session.get_TagID()
        self.__session.send_pps()

    def send_apdu(self, apdu):
        resp = self.__session.send_apdu(apdu)

        return resp

