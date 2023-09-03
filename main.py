#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC
from machine import SoftI2C as 	I2C
import dht
import _thread

#Visor:
from i2c_lcd import I2cLcd

#Para sensores de temperatura:
from ds18x20 import DS18X20
from onewire import OneWire
        
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

def estatisticas():          
    lcd.clear()
    lcd.putstr("ESTATISTICAS")

def tipo_uso():
    lcd.clear()
    lcd.putstr("TIPO USO")

def menu_musicas():
    lcd.clear()
    lcd.putstr("MENU MUSICAS")

def avancado():
    lcd.clear()
    lcd.putstr("AVANCADO")

def interface():
    global telapot, telabot, telabot_2, lcd

    def interar_estatisticas():
        c = 0
        while not sair.value():
            if c % 5 == 0:
                lcd.clear()
                c = 0
                lcd.putstr(f"ESTATISTICAS DENTRO")
            sleep(0.1)
        lcd.clear()

    def interar_tipo_uso():
        modo_antigo = ""
        sleep(0.3)
        while not sair.value():
            if seta.read() < 4095/2:
                modo_ = "eco"
            else:
                modo_ = "turbo"

            if modo_antigo != modo_:
                lcd.clear()
                if modo_ == "turbo":
                    lcd.putstr(f"TURBO")
                elif modo_ == "eco":
                    lcd.putstr(f"ECO")
                modo_antigo = modo_
                    
            
            if not entrar.value():
                modo = modo_
                break
            sleep(0.12)
        lcd.clear()
            

    def interar_menu_musicas():
        m_antigo = ""
        sleep(0.3)
        while not sair.value():
            if seta.read() < 4095/3:
                m_ = "m1"
            elif seta.read() < 4095/3 * 2:
                m_ = "m2"
            else:
                m_ = "m3"

            if m_antigo != m_:
                lcd.clear()
                if m_ == "m1":
                    lcd.putstr("Musica 1")
                elif m_ == "m2":
                    lcd.putstr("Musica 2")
                else:
                    lcd.putstr("Musica 3")
                m_antigo = m_                  
            
            if not entrar.value():
                mus = m_
                break               
            
            sleep(0.12)
        lcd.clear()

    def interar_avancado():
        def controlar_pwm():
            c_antigo = ""
            while not sair.value():
                if seta.read() < 4095/2:
                    c = "duty"
                else:
                    c = "freq"
                    
                if c_antigo != c:
                    lcd.clear()
                    if c == "duty":
                        lcd.putstr("Mudar Duty")
                    else:
                        lcd.putstr("Mudar Frequencia")
                    c_antigo = c

                if not entrar.value():
                    if c ==  "duty":
                        freq_antiga = 0
                        potValueReal = 0
                        while not sair.value():
                            lcd.clear()
                            potValue1 = seta.read() #Lê o Duty
                            potValueReal = mudar(potValue1, potValueReal)
                            try:
                                pwm.duty(int(potValueReal/4*limite))
                            except ValueError:
                                pwm.duty(1023)
                            sleep(0.2)
                            lcd.putstr(f"Duty: {potValueReal}")
                    else:
                        lcd.clear()
                        freq_antiga = 0
                        potValueReal = 0
                        while not sair.value():
                            potValue1 = seta.read() #Lê o Duty
                            potValueReal = mudar(potValue1, potValueReal)
                            try:
                                pwm.freq(int(potValueReal/4*limite))
                            except ValueError:
                                pwm.freq(1)
                            sleep(0.2)
                            lcd.putstr(f"Freq: {potValueReal}")
                
    
        s = [0, 0, 0, 0]
        i = 0
        t_antigo = f"{s[0]} {s[1]} {s[2]} {s[3]}"
        while not i < 0:
            sleep(0.12)
            s[i] = int(seta.read()/4095*9.9)
            
            t = f"{s[0]} {s[1]} {s[2]} {s[3]}"
            if str(t_antigo) != str(t):
                lcd.clear()
                t_antigo = t
                lcd.putstr(t)
                
            if s[i] != s[i-1] and not entrar.value():
                i += 1
                sleep(0.3)

            if sair.value():
                i -= 1
                sleep(0.3)  

            if i == 4:
                lcd.clear()
                if s == [2,9,2,3]:
                    lcd.putstr("Senha correta!")
                    sleep(1)
                    lcd.clear()
                    controlar_pwm()
                else:
                    lcd.putstr("Senha incorreta!")
                    sleep(1)
                    lcd.clear()
                    i = 0
                    s = [0, 0, 0, 0]        

    seta = telapot
    entrar = telabot
    sair = telabot_2

    uso_antigo = ""
    while True:
        if seta.read() < 4095/4:
            uso = 0
        elif seta.read() < 4095/2:
            uso = 1
        elif seta.read() < 4095/4 * 3:
            uso = 2
        else:
            uso = 3

        if uso != uso_antigo:
            if uso == 0:
                estatisticas()
                uso_antigo = ""
            elif uso == 1:
                tipo_uso()
                uso_antigo = ""
            elif uso == 2:
                menu_musicas()
                uso_antigo = ""
            else:
                avancado()
            uso_antigo = uso
        
        if not entrar.value():
            if uso == 0:
                interar_estatisticas()
                uso_antigo = ""
            elif uso == 1:
                interar_tipo_uso()
                uso_antigo = ""
            elif uso == 2:
                interar_menu_musicas()
                uso_antigo = ""
            else:
                interar_avancado()
                uso_antigo = ""

        sleep(0.12)
                
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
    telabot_2 = Pin(18, Pin.IN)
    telapot = ADC(Pin(4))

    ###Parte para funções de curvas:
    potValue1 = 0
    potValueReal = 0 #Mudar o duty de maneira lenta
    estado, estado_ = 0, 0
    
    #Bloqueando:
    pwm_block = False
    contagem = 1

    #Para o visor:
    pino_visor_1, pino_visor_2 = 22, 21
    DEFALT_I2C_ADDR = 0x27

    i2c = I2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2), freq = 10000)
    lcd = I2cLcd(i2c, DEFALT_I2C_ADDR, 2, 16)

    #Para o sensor de temperatura ds18x20:
    sensor_temperatura_1 = DS18X20(OneWire(Pin(17)))
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

    #Existem duas maneiras de inicialização:
    toca_mus = True
    freq = 665
    _t_3 = "."
    pausa_de_seguranca = False

    #Ativando leituras em threads:
    def plots():
        global telapot, telabot, telabot_2, lcd
        c = 0
        while True:
            print(c, telapot.read(), telabot.value(), telabot_2.value())
            c += 1
            if c % 100 == 0:
                c = 0
            sleep(0.1)
    _thread.start_new_thread(plots,())
    _thread.start_new_thread(interface,())
    
##    #Se telabot for 0 a saída h9 é 665 e o duty cycle
##    if telabot.value():        
##        pwm.freq(freq)
##        toca_mus = False
##        
##    print(telabot.value())
##
##    #Se em 5 segundos o telabot é off o toca_mus é on:
##    if toca_mus:
##        print("Tocando musica")
##        musicas("intro", pwm)        
        
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
                
##        if pwm_block == False: 
##            potValue1 = telapot.read() #Lê o Duty
##            potValueReal = mudar(potValue1, potValueReal)

##        if not pausa_de_seguranca:
##            try:
##                pwm.duty(int(potValueReal/4*limite))
##            except ValueError:
##                pwm.duty(1023)

        if contagem % 3000 == 0:
            contagem = 0
            sensor_temperatura_1.convert_temp()
##            sensor_temperatura_2.convert_temp()
            temperatura = sensor_temperatura_1.read_temp(roms1[0])
##            temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
##            print(temperatura)
