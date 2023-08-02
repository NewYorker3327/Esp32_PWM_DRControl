#Transcrição identica de código em c simplificado para micropython
#Existem algumas partes que não precissavam mas foi feito assim para
#padronizar com o outro código

#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC
import onewire
import ds18x20
import dht

def musicas(mus:str, obj):
    temp = 8
    if mus == "intro":
        mus = [[400, 10, 5], [400, 100, 5], [400, 200, 5], [400, 400, 5],
               [400, 700, 5], [400, 900, 5]]
            #[[294+587, 100, 4], [370+784, 200, 4], [466+1175, 440, 4], [587+1568, 600, 4],
            #[784+2093, 700, 4], [1175+2349, 900, 4]]

    if mus == "exit":
        mus = [[1568+784, 440, 2], [1175+587, 440, 2], [784+523, 440, 2], [587+294, 440, 2],
               [523+392, 440, 2]]

    for nota in mus:
        obj.freq(nota[0])
        obj.duty(nota[1])
        sleep(nota[2]/temp)
    return

def mod(a:int):
    if a < 0:
        return -a
    return a

def mudar(a:int, b:int):
    if a > b:
        return b + 1
    if a < b:
        return b - 1
    return b

if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)                    
    
    ###Variáveis potencia:
    
    ###Saídas:
    h6 = 13 #(era 27) #Pré-carga
    h9 = 12 #(era 25) #PWM
    #Como temos que mandar alguns volts ou saidas 0, 1 pelas portas fazemos:
    ph6 = Pin(13, Pin.OUT)
    ph6.off() #Começa desligado
    sleep(5) #O Programa deve ficar inativo por n segundos...
    ph6.on()

    ###Entradas:
    telabot = Pin(16, Pin.IN)
    telapot = ADC(Pin(4))

    ###Parte para funções de curvas:
    potValue1 = 0

    potValueReal = 0 #Mudar o duty de maneira lenta
    estado, estado_ = 0, 0
    
    #Propriedades do canal PWN
    pwm = PWM(Pin(12))
    
    #Bloqueando:
    pwm_block = False
    contagem = 1
    
#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                            
    #Mesma estrutura do void Setup do outro código:

    pwm.duty(0)
    pwm.freq(1)

    toca_mus = True
    #Se telabot for 0 a saída h9 é 432 e o duty cycle
    if telabot.value():
        pwm.freq(432)
        toca_mus = False
        
    print(telabot.value())

    #Se em 5 segundos o telabot é off:
    if toca_mus:
        print("Tocando musica")
        musicas("intro", pwm)        
    
    #Loop principal:
    while True:
        contagem += 1

        if pwm_block == False: 
            potValue1 = telapot.read() #Lê o Duty
            potValueReal = mudar(potValue1, potValueReal)

        try:
            pwm.duty(int(potValueReal/4))
        except ValueError:
            pwm.duty(1023)
            
        
        #Lê a temperatura:
        if contagem % 50 == 0:
            #sensor.convert_temp()
            #entrada_h13 = sensor.read_temp(roms[0])
            contagem = 1
            print("Fazendo loop principal", potValueReal)    
