#Transcrição identica de código em c simplificado para micropython
#Existem algumas partes que não precissavam mas foi feito assim para
#padronizar com o outro código

#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC, I2C
import onewire
import ds18x20
import dht
import _thread

#Visor:
from i2c_lcd import I2cLcd

#Para sensores de temperatura:
from ds18x20 import DS18X20
from onewire import OneWire

def processos_paralelos(): 
    contagem_paralela = 0
    while True:        
        if contagem_paralela % 2 == 0:
            _t_1, _t_2 = ".", " "
        else:
            _t_1, _t_2 = " ", "."
            
        lcd.clear()
        
        lcd.move_to(0, 6)
        if not pausa_de_seguranca:
            lcd.putstr(f"{_t_2}Duty: {str(int(potValueReal/40.99*limite+0.5))[:6]}%")
        else:
            lcd.putstr(f"{_t_2}Duty: RESFR%")

        lcd.move_to(1, 0)
        lcd.putstr(f"{_t_1}Freq:{str(freq)[:4]}Hz"

##        lcd.move_to(0, 0)
##        lcd.putstr(f"{_t_2}Ponte:{str(temperatura_de_seguranca)[:4]}{_t_3}", 0, 42, 1)

        lcd.move_to(0, 0)
        lcd.putstr(f"{_t_1}Temp:{str(temperatura)[:5]}C")        

        sleep(0.25)
        
        contagem_paralela += 1
        
def musicas(mus:str, obj):    
    temp = 8
    if mus == "intro":
        mus = [[392, 200, 2], [392, 400, 3], [523, 200, 2], [523, 400, 3],
               [588, 200, 2], [588, 400, 3], [660, 200, 2], [660, 400, 3], [392, 200, 2],[392, 400, 23], [392,0, .8],
               [392, 400, 5], [523, 400, 5], [523, 400, 3], [588, 400, 5],
               [588, 400, 5], [660, 400, 5], [588, 400, 5], [660, 400, 5], [700, 400, 3], [660, 400, 3], [700, 400, 5],
               [660, 400, 3], [588, 400, 3], [523, 400, 25], [392, 10, 3]]

    if mus == "exit":
        mus = [[1568+784, 440, 2], [1175+587, 440, 2], [784+523, 440, 2], [587+294, 440, 2],
               [523+392, 440, 2]]

    for nota in mus:
        globals()['freq']=nota[0]
        globals()['potValueReal']=nota[1]
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
    ###Variável limite duty (1=100%):
    limite = 0.35 
    
    ###Saídas:
    h6 = 13 #(era 27) #Pré-carga
    h9 = 12 #(era 25) #PWM    
    pwm = PWM(Pin(12))#Propriedades do canal PWN
    pwm.freq(1)
    pwm.duty(0)
    #Como temos que mandar alguns volts ou saidas 0, 1 pelas portas fazemos:
    ph6 = Pin(13, Pin.OUT)
    ph6.off() #Começa desligado
    sleep(3) #O Programa deve ficar inativo por n segundos...
    ph6.on()

    ###Entradas:
    telabot = Pin(16, Pin.IN)
    telapot = ADC(Pin(4))

    ###Parte para funções de curvas:
    potValue1 = 0
    potValueReal = 0 #Mudar o duty de maneira lenta
    estado, estado_ = 0, 0
    
    #Bloqueando:
    pwm_block = False
    contagem = 1

    #Para o visor:
    pino_visor_1, pino_visor_2 = 18, 19
    DEFALT_I2C_ADDR = 0x20

    i2x = I2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2), freq = 400000)
    lcd = I2cLcd(i2c, DEFALT_I2C_ADDR, 2, 16)

    #Para o sensor de temperatura ds18x20:
    sensor_temperatura_1 = DS18X20(OneWire(Pin(5)))
    roms1 = sensor_temperatura_1.scan()
    temperatura = sensor_temperatura_1.read_temp(roms1[0])

##    sensor_temperatura_2 = DS18X20(OneWire(Pin(17)))
##    roms2 = sensor_temperatura_2.scan()
##    temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
    
    
#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                            
    #Ligando visor:
    lcd.putstr("Carregando...")

    #Existem duas maneiras de inicialização:
    toca_mus = True
    freq = 665
    _t_3 = "."
    pausa_de_seguranca = False

    #Ativando leituras em threads:
    _thread.start_new_thread(processos_paralelos,())
    
    #Se telabot for 0 a saída h9 é 665 e o duty cycle
    if telabot.value():        
        pwm.freq(freq)
        toca_mus = False
        
    print(telabot.value())

    #Se em 5 segundos o telabot é off o toca_mus é on:
    if toca_mus:
        print("Tocando musica")
        musicas("intro", pwm)        
        
    #Loop principal:
    freq = 665
    contagem = 0    
    while True:
        contagem += 1
##        if temperatura_de_seguranca > 60 or pausa_de_seguranca:
##            pwm.duty(0)
##            pwm.freq(1)
##            pausa_de_seguranca = True
##            pwm_block = True
##            if temperatura_de_seguranca < 40:
##                pausa_de_seguranca = False
##                pwm_block = False
##                pwm.freq(665)
                
        if pwm_block == False: 
            potValue1 = telapot.read() #Lê o Duty
            potValueReal = mudar(potValue1, potValueReal)

        if not pausa_de_seguranca:
            try:
                pwm.duty(int(potValueReal/4*limite))
            except ValueError:
                pwm.duty(1023)

        if contagem % 3000 == 0:
            contagem = 0
            sensor_temperatura_1.convert_temp()
##            sensor_temperatura_2.convert_temp()
            temperatura = sensor_temperatura_1.read_temp(roms1[0])
##            temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
            print(temperatura)
