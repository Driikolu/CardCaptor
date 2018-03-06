#!/usr/bin/python3

##################################################
# hydra_handler.py :
#
# Fichier de classe de handler de l'outil hydraNFC
#
##################################################

import serial

class HydraNFC():

    def __init__(self, port="COM8", timeout=0,3):
        self._port=port
        self._timeout=timeout

        self._serial=None


    def connect(self):
        self._serial=serial.Serial(self._port,timeout=self._timeout)

    
