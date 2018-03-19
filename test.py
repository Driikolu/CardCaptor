from utils.reader_iso14443a import ReaderHydraNFC


def get_values(hn):
    #hn.send_apdu("00 a4 04 00   0E   32 50 41 59 2E 53 59 53 2E 44 44 46 30 31   00") # PPSE entry point
    #hn.send_apdu("00 a4 04 00   07   A0 00 00 00 04 10 10   00") #Selection app -> MC TR
    #hn.send_apdu("00 a4 04 00   07   A0 00 00 00 42 10 10   00") #Selection app -> MC
    #hn.send_apdu("00 B2 01 0C 00") # Extrait num
    #hn.send_apdu("80 A8 00 00 02 83 00 00")
    #hn.send_apdu("00 B2 01 0C 00")
    #hn.send_apdu("00 B2 01 14 00")
    #hn.send_apdu("00 B2 01 1C 00")
    #hn.send_apdu("00 B2 01 24 00")
    #hn.send_apdu("00 B2 02 24 00")
    #hn.send_apdu("00 B2 03 2C 00")
    #hn.send_apdu("80 CA 9F 17 00")
    #hn.send_apdu("80 CA 9F 36 00")
    print(hn.send_apdu("00 A4 04 00 07 A0 00 00 00 04 10 10 00")) #Select MC app
    #hn.send_apdu("80 A8 00 00 02 83 00 00") # Inconnu
    print(hn.send_apdu("00 B2 01 0C 00")) # Read number + exp date
    print(hn.send_apdu("80 CA 9F 17 00")) # Red PIN 
    #hn.send_apdu("00 B2 01 14 00")
    #hn.send_apdu("00 B2 01 1C 00")
    #hn.send_apdu("00 B2 01 24 00")
    #hn.send_apdu("00 B2 02 24 00")
    #hn.send_apdu("00 B2 03 2C 00")
    #hn.send_apdu("80 CA 9F 17 00")
    #hn.send_apdu("80 CA 9F 36 00")


if __name__=="__main__":
    hn = ReaderHydraNFC(port="/dev/ttyACM0", debug_mode=False, block_size= 24)
    hn.connect()
    hn.field_off()
    hn.field_on()
    hn.polling()

    get_values(hn)
    
    hn.field_off() 
