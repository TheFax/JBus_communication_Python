import serial
import time
import jbus

#UPS COMMUNICATION CLASS

#This class is not perfect and has not been tested on a big number of UPS.
#
#Exports:
#  send_command(self, command)
#  request_measures(self)
#  request_identifier(self)
#  extract_word(self, answer, word_number)
#  (other functions are intended for internal use only)

#TODO: implementare la gestione degli errori in tutto il resto della classe
#      magari creando una variabile esportata che contenga l'esito dell'azione

#TODO: rinominare le variabili locali utilizzando le trail underscore

#TODO: rinominare le funzioni locali utilizzando le trail underscore

class ups:
    def __init__(self, port, speed=9600, node=0x01):
        self.debug = False
        #self.debug = True
        self.error = ""
        self.port = port
        self.node = node
        self.speed = speed
        self.timeout = 0.06 #centesimi di secondo
        if (self.debug):
            print ("[ups] - Apertura porta seriale")
        #TODO: try per catturare gli errori
        self.ser = serial.Serial(port,
                                 baudrate=speed,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS
                                )
        
     
    def send_request(self, data):
        #TODO: qui verifica se la seriale è aperta
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(data)
        if (self.debug):
            conteggio = 0
            print ("[ups] - Invio pacchetto dati completato")
        answer = bytes([])
        counter = 0
        while counter<10:
            time.sleep(self.timeout)
            counter=counter + 1
            while self.ser.inWaiting() > 0:
                if (self.debug):
                    conteggio=conteggio + 1
                    print ("[ups] - Ricezione pacchetto dati n.", conteggio)
                answer = answer + self.ser.read(self.ser.inWaiting())
                counter=6 #scarico il contatore se ricevo qualcosa
                time.sleep(self.timeout) #attendo che arrivino altri byte di altra roba
        return answer
    
    def send_command(self, command):
        """Send the command passed as argument to the UPS
        """
        question = jbus.jbus_generator_data_write(self.node, 0x15b0, bytes([0x00,command]))
        answer = self.send_request(question)
        #print("Question: [", question, "]")
        #print("Answer: [",answer,"] LEN: ",len(answer))
        return self.verify_response(question, answer)
    
    def request_measures(self):
        """Request the measures to the UPS.
        Returns: the complete measures frame
        """
        question = jbus.jbus_generator_read(self.node, 0x1060, 48)
        answer = self.send_request(question)
        #print("Question: [", question, "]")
        #print("Answer: [",answer,"] LEN: ",len(answer))
        result = self.verify_response(question, answer)
        if (result == "OK"):
            return answer
        else:
            self.error=result
            return False
        
    def request_identifier(self):
        """Ask the identifies to the UPS.
        Returns: a dictionary with informations returned from UPS
        """
        question = jbus.jbus_generator_read(self.node, 0x1000, 12)
        answer = self.send_request(question)
        #print("Question: [", question, "]")
        print("Answer: [",answer,"] LEN: ",len(answer))
        result = self.verify_response(question, answer)
        if (result == "OK"):
            result = {
                "UPS_type" :   self.extract_word(answer,0),
                "Power_KVA" :  self.extract_word(answer,1)/10,
                "SN" :         chr(answer[10])+
                               chr(answer[9])+
                               chr(answer[12])+
                               chr(answer[11])+
                               chr(answer[14])+
                               chr(answer[13])+
                               chr(answer[16])+
                               chr(answer[15])+
                               chr(answer[18])+
                               chr(answer[17])
            }
            return result
        else:
            self.error=result
            return False

    
    def verify_response(self, question, response):
        #print(response)
        if (len(response) < 5):
            return "[ups] - Error - No response, or response too short"
        if (jbus.jbus_add_checksum(response[0:-2]) != response):
            return "[ups] - Error - Checksum error"
        #TODO: qui aggiungere la verifica del checksum
        if ((int(response[2]) & 0x80) != 0):
            if (response[3] == 0x01):
                return "[ups] - Error - Bad function code"
            elif (response[3] == 0x02):
                return "[ups] - Error - Bad address"
            elif (response[3] == 0x03):
                return "[ups] - Error - Bad CRC"
            else:
                return "[ups] - Error - Unknown error"
        return "OK"
    
    def extract_word(self, answer, word_number):
        return jbus.jbus_extract_word(answer, word_number)
