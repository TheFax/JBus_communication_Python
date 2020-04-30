import time
import ups_comunication_class

print("Starting program")

time.sleep(0.2)

try:
    #Instauro un'istanza della classe, passando il nome della porta seriale, la velocità ed il nodo dell'UPS.
    my_ups = ups_comunication_class.ups("/dev/ttyUSB0", 9600, 1)
    
    while True:
        #Richiedo il pacchetto misure
        risposta = my_ups.request_measures()

        #TODO: qui controllare che la risposta non sia negativa

        #Stampo sullo schermo il pacchetto misure 
        print("------------------------------------------------------")
        #print(risposta)
        for m in range(0,39):
            misura = my_ups.extract_word(risposta, m)
            if (misura != 65535):
                print (" --> M", m , "=",  misura, sep = '')
        
        #Richiedo il pacchetto identifier
        risposta = my_ups.request_identifier()

        #TODO: qui controllare che la risposta non sia negativa

        #Stampo sullo schermo il dictionary restituito
        print("------------------------------------------------------")
        print(risposta)
        #ITYS2 1K - type 30
        #ITYS1 1K - type 30
        #MODULYS  - type 31
        #NETYS RR 2 3.3K - type 31
        #NETYS RT 2 5/7K - type 31
        
        #Attesa 0.5 secondi
        time.sleep(0.5)

        #print("Command 5")
        #risposta = my_ups.send_command(5)
        
except KeyboardInterrupt:
    print("Exiting Program")

#except:
#    print("Error Occurs, Exiting Program")

finally:
    pass
