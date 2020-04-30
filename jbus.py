def crc16(data):
    crc = 0xFFFF
    for i in range(0,len(data)):
        crc = crc ^ ( data[i] & 0xFF )
        for x in range(1,9):
            if (crc % 2 ) == 0:
                crc = crc >> 1
            else:
                crc = crc >> 1
                crc = crc ^ 0xA001
    return crc

def jbus_add_checksum(data):
    crc = crc16(data)
    final = data + bytes([crc & 0xff]) + bytes([(crc>>8) & 0xff])
    return final

def jbus_generator_read(node, address, words):
    frame = bytes([node]) + bytes([0x03]) + bytes([address>>8 & 0xff]) + bytes([address & 0xff]) + bytes([0x00]) + bytes([words & 0xff])
    frame = jbus_add_checksum(frame)
    return frame

def jbus_generator_data_write(node, address, data):
    frame = bytes([node]) + bytes([0x10]) + bytes([address>>8 & 0xff]) + bytes([address & 0xff]) + bytes([0x00]) + bytes([int(len(data)/2) & 0xff]) + bytes([(len(data)) & 0xff]) + data
    frame = jbus_add_checksum(frame)
    return frame
    #esempio:
    #print(jbus.jbus_generator_command_write(1,0x15b0,0x06).hex())

def jbus_generator_command_write(node, address, data):
    frame = bytes([node]) + bytes([0x06]) + bytes([address>>8 & 0xff]) + bytes([address & 0xff]) + bytes([data>>8 & 0xff]) + bytes([data & 0xff])
    frame = jbus_add_checksum(frame)
    return frame
    #esempio:
    #print(jbus.jbus_generator_data_write(0x01,0x15b0,bytes([0x00,0x05])).hex())

def jbus_extract_word(frame, word_number):
  #Dato un vettore di dati ricevuto via JBUS, restituisco la word richiesta, considerando che i primi
  #tre byte di qualsiasi pacchetto JBUS sono dati "non interessanti" per noi.
  
  #TODO: controllare se il jbus_frame in analisi contiene una risposta negativa dell'host.
  
  word_number = word_number*2  #perchè si ragiona a 16 bit, non a 8 bit
  word_number = word_number+3  #perchè i primi tre byte fanno parte del protocollo JBUS
  return (frame[word_number] <<8 ) + (frame[word_number+1])
