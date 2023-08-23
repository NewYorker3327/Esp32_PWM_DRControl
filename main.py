#Transcrição identica de código em c simplificado para micropython
#Existem algumas partes que não precissavam mas foi feito assim para
#padronizar com o outro código

#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC
import onewire
import ds18x20
import dht

#Para visor:
from machine import SoftI2C
import ssd1306

def musicas(mus:str, obj):
    temp = 8
    if mus == "intro":
        mus = [[392, 400, 5], [392, 400, 3], [523, 400, 5], [523, 400, 3],
               [588, 400, 5], [588, 400, 3], [660, 400, 5], [660, 400, 3], [392, 400, 25],[392,0, .8],
               [392, 400, 5], [523, 400, 5], [523, 400, 3], [588, 400, 5],
               [588, 400, 5], [660, 400, 5], [588, 400, 5], [660, 400, 5], [700, 400, 3], [660, 400, 3], [700, 400, 5],
               [660, 400, 3], [588, 400, 3], [523, 400, 25], [392, 10, 1]]

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
    sleep(0.8) #O Programa deve ficar inativo por n segundos...
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

    #Para o visor:
    pino_visor_1, pino_visor_2 = 18, 19
    i2c = SoftI2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2))

    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    #Testando:
    oled.text("Ligando...", 10, 10, 1)
    oled.show()
    
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
        freq = 432
        pwm.freq(freq)
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
        if contagem % 1000 == 0:
            #sensor.convert_temp()
            #entrada_h13 = sensor.read_temp(roms[0])
            contagem = 1
            print("Fazendo loop principal", potValueReal)
            
            oled.fill(0)
            oled.text(f"PWM values:", 0, 0, 1)
            oled.text(f"Duty: {str(int(potValueReal/40.99+0.5))[:6]}%", 0, 25, 1)
            oled.text(f"Freq: {str(freq)[:6]}", 0, 50, 1)
            oled.show()