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

def musicas(mus:str):
    global pwm, modo_global
    obj = pwm

    backup = modo_global
    modo_global == "musica"
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

    if mus == "zelda":
        mus = [[665, 200, 6], [498, 200, 6], [665, 200, 4], [746, 200, 2],
               [791, 200, 2], [888, 200, 2], [996, 200, 16], [1118, 200, 2],
               [1255, 200, 16], [1118, 200, 2], [996, 200, 2], [1118, 200, 4],
               [996, 200, 2], [1118, 200, 4], [996, 200, 2], [940, 200, 8],
               [838, 200, 4], [888, 200, 4], [1056, 200, 2], [940, 200, 2],
               [888, 200, 2], [791, 200, 4], [888, 200, 2], [996, 200, 8],
               [888, 200, 2], [791, 200, 2], [746, 200, 4], [838, 200, 2],
               [888, 200, 8], [1118, 200, 8], [996, 200, 8]]

    for nota in mus:
        globals()['freq'] = nota[0]
        globals()['potValueReal'] = nota[1]
        obj.freq(nota[0])
        obj.duty(nota[1])
        sleep(nota[2]/temp)

    modo_global = backup

def mod(a:int):
    if a < 0:
        return -a
    return a

def mudar(a:int, b:int, n = 1):
    if a > b:
        return b + n
    if a < b:
        return b - n
    return b

def plots():
    global temperatura_global_1, temperatura_global_2, telapot, telabot, telabot_2, lcd
    c = 0
    while True:
        print(c, telapot.read(), telabot.value(), telabot_2.value(), temperatura_global_1, temperatura_global_2)
        c += 1
        if c % 100 == 0:
            c = 0
        sleep(0.1)

def estatisticas():          
    lcd.clear()
    lcd.putstr("MODOnESTATISTICAS <")
    
def tipo_uso():
    lcd.clear()
    lcd.putstr("MODO         <nESTATISTICAS")
    
def menu_musicas():
    lcd.clear()
    lcd.putstr("ESTATISTICASnMUSICAS      <")

def avancado():
    lcd.clear()
    lcd.putstr("MUSICASnMANUAL       <")

def tela_descanso():
    global lcd, telapot, telabot, telabot_2, freq_global, pot_global, temperatura_global_1, temperatura_global_2
    estat_antigo = f"FRQ:{int(300 + int(freq_global/1.517))-1} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/4*limite + 0.9)}% T2:{int(temperatura_global_2)}"
    pot_antigo = telapot.read()
    c = 0
    while abs(pot_antigo - telapot.read()) < 10 and telabot.value() and not telabot_2.value():
        if c % 10 == 0:
            estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/4*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
            if estat_antigo != estat:
                lcd.clear()
                lcd.putstr(estat)
                estat_antigo = estat
        if c % 20 == 0:
            estat = f"  AGROMAG  nDUTY:{int(pot_global/4*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
            if estat_antigo != estat:
                lcd.clear()
                lcd.putstr(estat)
                estat_antigo = estat
        if c % 30 == 0:
            estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}n  AGROMAG" 
            if estat_antigo != estat:
                lcd.clear()
                lcd.putstr(estat)
                estat_antigo = estat
            C = 1
        C += 1
        sleep(0.15)
        lcd.clear()

def vai_tela_descanso():
    global telapot, lcd
    t1, t2, t3, t4 = 100, 300, 500, 700
    while True:
        sleep(7)
        t1 = int(telapot.read()/10)
        sleep(7)
        t2 = int(telapot.read()/10)
        sleep(7)
        if t1 == t2 == t3 == t4:
            tela_descanso()
        t3 = int(telapot.read()/10)
        sleep(7)
        t4 = int(telapot.read()/10)
        if t1 == t2 == t3 == t4:
            tela_descanso()

def interface():
    global telapot, telabot, telabot_2, lcd

    def solta_botao():
        global telabot
        c = 0
        while telabot.value():
            sleep(0.035)
            c += 1
            if c % 100 == 0:
                lcd.clear()
                lcd.putstr(f"SOLTE O BOTAO!")

    def interar_estatisticas():
        global temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite
        c = 0
        solta_botao()
        estat_antigo = f"FRQ:{int(300 + int(freq_global/1.517))-1} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/4*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
        while not sair.value():
            if c % 5 == 0:
                c = 0
                estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/4*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
                if estat_antigo != estat:
                    lcd.clear()
                    lcd.putstr(estat)
                    estat_antigo = estat
            sleep(0.02)
        lcd.clear()

    def interar_tipo_uso():
        global modo_global
        modo_antigo = ""
        solta_botao()
        while not sair.value():
            if seta.read() < 4095/3:
                modo_ = "eco"
            elif seta.read() < 4095/3 * 2:
                modo_ = "turbo"
            else:
                modo_ = "off"

            if modo_antigo != modo_:
                lcd.clear()
                if modo_ == "eco":
                    lcd.putstr(f"[ECO] TURBO OFFnBAIXO GASTO")
                elif modo_ == "turbo":
                    lcd.putstr(f" ECO [TURBO]OFFnPERFORMANCE")
                elif modo_ == "off":
                    lcd.putstr(f"ECO TURBO [OFF]nDESLIGADO")
                modo_antigo = modo_
                    
            
            if not entrar.value():
                modo_global = modo_
                lcd.clear()
                lcd.putstr(f"MODO {modo_.upper()}nATIVADO!")
                sleep(1)
                break
            sleep(0.06)
        lcd.clear()
            

    def interar_menu_musicas():
        m_antigo = ""
        solta_botao()
        while not sair.value():
            if seta.read() < 4095/3:
                m_ = "intro"
            elif seta.read() < 4095/3 * 2:
                m_ = "exit"
            else:
                m_ = "zelda"

            if m_antigo != m_:
                lcd.clear()
                if m_ == "intro":
                    lcd.putstr("MUSICA:n[1]  2   3 ")
                elif m_ == "exit":
                    lcd.putstr("MUSICA:n 1  [2]  3 ")
                else:
                    lcd.putstr("MUSICA:n 1   2  [3]")
                m_antigo = m_                  
            
            if not entrar.value():
                lcd.clear()
                lcd.putstr("TOCANDO...")
                mus = m_
                musicas(m_)                
                break               
            
            sleep(0.06)
        lcd.clear()

    def interar_avancado():
        def controlar_pwm():
            global potValue1, potValueReal, limite, freq_global, pot_global, modo_global
            c_antigo = ""
            while not sair.value():
                if seta.read() < 4095/2:
                    c = "duty"
                else:
                    c = "freq"
                    
                if c_antigo != c:
                    lcd.clear()
                    if c == "duty":
                        lcd.putstr(f"[DUTY:{str(pot_global/40*limite)[0:4]}%]n FREQ:{int(300 + int(freq_global/1.517))}")
                    else:
                        lcd.putstr(f" DUTY:{str(pot_global/40*limite)[0:4]}% n[FREQ:{int(300 + int(freq_global/1.517))}]")
                    c_antigo = c
                sleep(0.06)

                if not entrar.value():
                    modo_global = "manual"
                    lcd.clear()
                    solta_botao()
                    if c ==  "duty":
                        pot_antiga_1 = 0
                        pot_antiga_2 = 0
                        ciclos = 0
                        pot_visor = pot_global
                        while not sair.value():
                            pot_visor = mudar(seta.read(), pot_visor, 1)
                            if not entrar.value() and modo_global == "manual":
                                try:
                                    pwm.duty(int(pot_global/4*limite))
                                except ValueError:
                                    pwm.duty(1023)
                                pot_global = pot_visor
                                pot_antiga_1 = pot_global
                                lcd.clear()
                                lcd.putstr(f"DUTY: {str(pot_global/40*limite)[0:4]}% <<nDUTY SETADO!")
                                sleep(1)
                            if abs(pot_visor - pot_antiga_2) > 10 and ciclos % 1000 == 0:
                                lcd.clear()
                                lcd.putstr(f"DUTY: {str(pot_visor/40*limite)[0:4]}% <<nFREQ: {int(300 + int(freq_global/1.517))}")
                                ciclos = 1
                                pot_antiga_2 = pot_visor
                            ciclos += 1
                    else:
                        freq_antiga_1 = 0
                        freq_antiga_2 = 0
                        freq_visor = freq_global
                        ciclos = 0
                        while not sair.value():
                            freq_global = mudar(seta.read(), freq_global, 1)
                            if not entrar.value() and modo_global == "manual":
                                try:
                                    pwm.freq(int(300 + int(freq_global/1.517)))
                                except ValueError:
                                    pwm.freq(1)
                                freq_global = freq_visor
                                freq_antiga_1 = freq_global
                                lcd.clear()
                                lcd.putstr(f"FREQ SETADA!nFREQ: {int(300 + int(freq_global/1.517))} <<")
                                sleep(1)
                            if abs(freq_visor - freq_antiga_2) > 10 and ciclos % 1000 == 0:
                                lcd.clear()
                                lcd.putstr(f"DUTY: {str(pot_global/40*limite)[0:4]}%nFREQ: {int(300 + int(freq_visor/1.517))} <<")
                                freq_antiga_2 = freq_visor
                                ciclos = 1
                            ciclos += 1
                    lcd.clear()
                    c_antigo = ""
                    sleep(0.3)
                
    
        s = [0, 0, 0, 0]
        i = 0
        t_antigo = f"SENHA:n[{s[0]}]{s[1]} {s[2]} {s[3]}"
        while not i < 0:
            sleep(0.06)
            try:
                s[i] = int(seta.read()/4095*9.9)
            except:
                i = 0

            if i == 0:
                t = f"SENHA:n[{s[0]}]{s[1]} {s[2]} {s[3]}"
            elif i == 1:
                t = f"SENHA:n {s[0]}[{s[1]}]{s[2]} {s[3]}"
            elif i == 2:
                t = f"SENHA:n {s[0]} {s[1]}[{s[2]}]{s[3]}"
            else:
                t = f"SENHA:n {s[0]} {s[1]} {s[2]}[{s[3]}]"
                
            if str(t_antigo) != str(t):
                lcd.clear()
                t_antigo = t
                lcd.putstr(t)
                
            if not entrar.value():
                i += 1
                solta_botao()

            if sair.value():
                i -= 1
                sleep(0.3)

            if i == 4:
                lcd.clear()
                if s == [2,9,2,3]:
                    lcd.putstr("SENHAnCORRETA!")
                    sleep(1)
                    lcd.clear()
                    controlar_pwm()
                else:
                    lcd.putstr("SENHAnINCORRETA!")
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
                tipo_uso()
                uso_antigo = ""
            elif uso == 1:
                estatisticas()
                uso_antigo = ""
            elif uso == 2:
                menu_musicas()
                uso_antigo = ""
            else:
                avancado()
            uso_antigo = uso
        
        if not entrar.value():
            if uso == 0:
                interar_tipo_uso()
                uso_antigo = ""
            elif uso == 1:
                interar_estatisticas()
                uso_antigo = ""
            elif uso == 2:
                interar_menu_musicas()
                uso_antigo = ""
            else:
                interar_avancado()
                uso_antigo = ""

        sleep(0.06)
                
if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)                    
    ###Variável limite duty (1=100%):
    limite = 0.35

    temperatura_global_1, temperatura_global_2 = 0, 0
    
    ###Saídas:
    h6 = 13 #(era 27) #Pré-carga
    h9 = 12 #(era 25) #PWM    
    pwm = PWM(Pin(12))#Propriedades do canal PWN
    pwm.freq(300)
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

    sensor_temperatura_2 = DS18X20(OneWire(Pin(5)))
    roms2 = sensor_temperatura_2.scan()
    temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
    
    
#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                            

    #Globais:
    toca_mus = True
    freq_global = 0
    pot_global = 0
    modo_global = "off"
    modo_atual = ""
    pausa_de_seguranca = False
            
    #_thread.start_new_thread(plots,())
    _thread.start_new_thread(interface,())
    _thread.start_new_thread(vai_tela_descanso,())
    
    #Loop principal:
    contagem = 0  
    while True:
        contagem += 1

        #print(contagem, temperatura_global_1, temperatura_global_2)

        if contagem % 1000 == 0:
            contagem = 1
            sensor_temperatura_1.convert_temp()
            sensor_temperatura_2.convert_temp()
            temperatura = sensor_temperatura_1.read_temp(roms1[0])
            temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
            temperatura_global_1, temperatura_global_2 = temperatura, temperatura_de_seguranca

        if temperatura_de_seguranca > 60 or modo_global == "resfriar":
            if modo_global != "resfriar":
                backup_modo_global = modo_global
                pwm.freq(1)
                pwm.duty(0)
                pot_global = 0
                freq_global = 0
                lcd.clear()
                lcd.putstr("RESFRIANDO!")
                modo_global = "resfriar"
                modo_atual = modo_global
                sleep(3)

            modo_global = "resfriar"

            if temperatura_de_seguranca < 40:
                modo_global = backup_modo_global

        if not modo_global == "resfriar" and not modo_global == "manual":
            if modo_global == "eco" and modo_atual != modo_global:
                pwm.freq(665)
                pwm.duty(100)
                freq_global = 554 # 554/1.517 + 300 = 665
                pot_global = 100
                modo_atual = modo_global
                
            elif modo_global == "turbo" and modo_atual != modo_global:
                pwm.freq(665)
                pwm.duty(200)
                freq_global = 554
                pot_global = 200
                modo_atual = modo_global

            elif modo_global == "off" and modo_atual != modo_global:
                pwm.duty(0)
                pot_global = 0
                modo_atual = modo_global
            
