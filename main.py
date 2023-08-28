#Transcrição identica de código em c simplificado para micropython
#Existem algumas partes que não precissavam mas foi feito assim para
#padronizar com o outro código

#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC
import onewire
import ds18x20
import dht
import _thread

#Para visor:
from machine import SoftI2C
import ssd1306

#Para sensores de temperatura:
from ds18x20 import DS18X20
from onewire import OneWire

contagem_ = 0

def processos_paralelos():
    _t_3 = "."
    while True:
        contagem_paralela += 1

        if contagem_paralela % 8 == 0:
            contagem_paralela = 0
            temperatura = sensor_temperatura_1.read_temp(roms[0])
            temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms[0])
            if temperatura_de_seguranca > 55:
                _t_3 = "!!!"
            elif temperatura_de_seguranca > 50:
                _t_3 = "!!"
            elif temperatura_de_seguranca > 45:
                _t_3 = "!"
            else:
                _t_3 = " "

        if contagem_paralela % 2 == 0:
            _t_1, _t_2 = ".", " "
        else:
            _t_1, _t_2 = " ", "."
            
        oled.fill(0)
        oled.text(f"{_t_1}Valores PWM:", 0, 0, 1)
        oled.text(f"{_t_2}Duty: {str(int(potValueReal/40.99*limite+0.5))[:6]}%", 0, 16, 1)
        oled.text(f"{_t_1}Freq: {str(freq)[:6]}", 0, 32, 1)
        oled.text(f"{_t_2}Temperatura: {str(temperatura)[:4]} {_t_3}", 0, 48, 1)
        oled.show()
        sleep(0.25)
        
def musicas(mus:str, obj):    
    temp = 8
    if mus == "intro":
        mus = [[392, 400, 5], [392, 200, 3], [523, 100, 5], [523, 600, 3],
               [588, 200, 5], [588, 300, 3], [660, 400, 5], [660, 400, 3], [392, 400, 25],[392,0, .8],
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
    limite = 0.4
    
    ###Saídas:
    h6 = 13 #(era 27) #Pré-carga
    h9 = 12 #(era 25) #PWM    
    pwm = PWM(Pin(12))#Propriedades do canal PWN
    pwm.freq(1)
    pwm.duty(0)
    #Como temos que mandar alguns volts ou saidas 0, 1 pelas portas fazemos:
    ph6 = Pin(13, Pin.OUT)
    ph6.off() #Começa desligado
    sleep(.8) #O Programa deve ficar inativo por n segundos...
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
    i2c = SoftI2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2))
    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    #Para o sensor de temperatura ds18x20:
    sensor_temperatura_1 = DS18X20(OneWire(Pin('a definir', PIN.OPEN_DRAIN)))
    sensor_temperatura_1.powermode(Pin('a definir'))
    roms = sensor_temperatura_1.scan()
    sensor_temperatura_1.resolution(roms[0])
    temperatura = sensor_temperatura_1.read_temp(roms[0])

    sensor_temperatura_2 = DS18X20(OneWire(Pin('a definir', PIN.OPEN_DRAIN)))
    sensor_temperatura_2.powermode(Pin('a definir'))
    roms = sensor_temperatura_2.scan()
    sensor_temperatura_2.resolution(roms[0])
    temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms[0])
    
    
#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                            
    #Ligando visor:
    oled.text("Ligando...", 10, 10, 1)
    oled.show()

    #Existem duas maneiras de inicialização:
    toca_mus = True
    freq = 432

    #Ativando leituras em threads:
    _thread.start_new_thread(processos_paralelos,())
    
    #Se telabot for 0 a saída h9 é 432 e o duty cycle
    if telabot.value():        
        pwm.freq(freq)
        toca_mus = False
        
    print(telabot.value())

    #Se em 5 segundos o telabot é off o toca_mus é on:
    if toca_mus:
        print("Tocando musica")
        musicas("intro", pwm)        
    
    #Loop principal:
    freq = 432
    while True:
        if temperatura_de_seguranca > 60:
            pwm.duty(0)
            pwm.freq(1)
            break
            
        if pwm_block == False: 
            potValue1 = telapot.read() #Lê o Duty
            potValueReal = mudar(potValue1, potValueReal)

        try:
            pwm.duty(int(potValueReal/4*limite))
        except ValueError:
            pwm.duty(1023)
        
            
