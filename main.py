#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC
from machine import SoftI2C as 	I2C
import dht
import _thread
from math import log2

#Visor:
from i2c_lcd import I2cLcd

#Para sensores de temperatura:
from ds18x20 import DS18X20
from onewire import OneWire

#Wifi:
import network
import socket

#Temperatuda da propria esp
import esp32
#esp32.raw_temperature()

def voltar(k, log2 = log2, limite_inf = 440):
    return int(12*log2(k/limite_inf))

def passar_nota(n):
    return int(220 * 2 ** (n/12))

def musicas(mus:str):
    global pwm, modo_global, modo_atual, freq_global, pot_global
    obj = pwm

    pot_antigo = pot_global
    freq_antigo = freq_global

    backup = modo_global
    modo_global == "musica"
    modo_atual = modo_global
    
    if mus == "intro":
        temp = 8
        mus = [[392, 200, 2], [392, 400, 3], [523, 200, 2], [523, 400, 3],
               [588, 200, 2], [588, 400, 3], [660, 200, 2], [660, 400, 3], [392, 200, 2],[392, 400, 23], [392,0, .8],
               [392, 400, 5], [523, 400, 5], [523, 400, 3], [588, 400, 5],
               [588, 400, 5], [660, 400, 5], [588, 400, 5], [660, 400, 5], [700, 400, 3], [660, 400, 3], [700, 400, 5],
               [660, 400, 3], [588, 400, 3], [523, 400, 25], [392, 10, 3]]

    if mus == "exit":
        temp = 8
        mus = [[1568+784, 440, 2], [1175+587, 440, 2], [784+523, 440, 2], [587+294, 440, 2],
               [523+392, 440, 2]]

    if mus == "zelda":
        v = 300
        temp = 16
        mus = [[12, v, 6], [0, v, 10], [2, v, 2], [3, v, 2], [5, v, 2], [7, v, 16],
               [8, v, 2], [10, v, 2], [12, v, 16], [10, v, 2], [8, v, 2], [10, v, 4],
               [8, v, 2], [7, v, 16], [5, v, 4], [7, v, 2], [8, v, 16], [7, v, 2], [5, v, 2], [3, v, 4],
               [5, v, 2], [7, v, 16], [5, v, 2], [3, v, 2], [2, v, 2], [3, v, 2], [5, v, 2], [8, v, 6], [7, v, 12]]

    if mus == "fef":
        v = 300
        temp = 16
        mus = [[1, v, 2], [8, v, 2], [15, v, 2], [16, v, 6], [1, v, 2], [8, v, 2], [15, v, 2], [16, v, 6], [1, v, 2], [8, v, 2], [15, v, 2], [16, v, 6],
               [[1,8], v, 2], [8, v, 2], [[15, 8], v, 2], [[16, 8], v, 2], [16, v, 4],
               [[-1,8], v, 2], [8, v, 2], [[15, 8], v, 2], [[16, 8], v, 2], [16, v, 4],
               [[-3,8], v, 2], [8, v, 2], [[15, 8], v, 2], [[16, 8], v, 2], [16, v, 4],
               [[3,6], v, 4], [[1, 4], v, 4], [[-1, 2], v, 4],
               [1, v, 8], [-1, v, 2], [6, v, 2], [1, v, 8], [-1, v, 2], [8, v, 2],
               [4, v, 8], [8, v, 2], [6, v, 2], [8, v, 8]]

    for nota in mus:
        if type(nota[0]) == list:
            resp = 0
            for n_individual in nota[0]:
                resp += passar_nota(n_individual)
            freq_global = resp
            pot_global = nota[1]
            obj.freq(resp)
            obj.duty(nota[1])
            sleep(nota[2]/temp)
        elif nota[0] < 30:
            freq_global = nota[0]
            pot_global = nota[1]
            obj.freq(passar_nota(nota[0]))
            obj.duty(nota[1])
            sleep(nota[2]/temp)
        else:
            freq_global = nota[0]
            pot_global = nota[1]
            obj.freq(nota[0])
            obj.duty(nota[1])
            sleep(nota[2]/temp)

    freq_global = freq_antigo
    pot_global = pot_antigo
    obj.freq(int(300 + int(freq_global/1.517)))
    obj.duty(int(pot_global/4*limite))

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
    pot_antigo = telapot.read()
    c = 0
    while abs(pot_antigo - telapot.read()) < 10 and telabot.value() and not telabot_2.value():
        if c == 20:
            estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/40*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
            lcd.clear()
            lcd.putstr(estat)
        elif c == 40:
            estat = f"  AGROMAG  nDUTY:{int(pot_global/40*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
            lcd.clear()
            lcd.putstr(estat)
        elif c == 60:
            estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}n  AGROMAG" 
            lcd.clear()
            lcd.putstr(estat)
            c = 1
        c += 1
        sleep(0.1)

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

def tela_web():
    global modo_global, ip_global, wifi_global, temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite

    def pagina_web():
        temperatura_placa = str((esp32.raw_temperature() - 32) * 5/9)
        html = """
    <html>   
        <head>   
            <meta content="width=device-width, initial-scale=1" name="viewport"></meta>   
        </head>   
        <body>   
            <center><h2>AGROMAG</h2></center>   
                <center>   
                 <form>   
                  <button name="MODO" type="submit" value="0"> OFF </button>   
                  <button name="MODO" type="submit" value="1"> ECO </button>
                  <button name="MODO" type="submit" value="2"> TURBO </button>  
                 </form>   
                </center>   
            <center><p>Modo atual: <strong>""" + str(modo_global) + """</strong>.</p></center>
            <center><p>Frequência: <strong>""" + str(freq_global) + """</strong>.</p></center>
            <center><p>Potência: <strong>""" + str(pot_global) + """</strong>.</p></center>
            <center><p>Temperatura saída: <strong>""" + str(temperatura_global_1) + """</strong>.</p></center>
            <center><p>Temperatura da Placa: <strong>""" + str(temperatura_global_2) + """</strong>.</p></center>
            <center><p>Temperatura do Processador: <strong>""" + str(temperatura_placa) + """</strong>.</p></center>
        </body>   
        </html>  
"""
        return html

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("", 80))
    soc.listen(5)
    
    while True:
        sleep(10)
        if modo_global != "manual" and modo_global != "resfriar" and modo_global != "musica":
            conn, addr = soc.accept()

            request = str(conn.recv(1024))
            if request.find("\?MODO=0") > 1:
                modo_global = "off"
            elif request.find("\?MODO=1") > 1:
                modo_global = "off"
            elif request.find("\?MODO=2") > 1:
                modo_global = "turbo"

            response = pagina_web()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

            conn.close()
        

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
        estat_antigo = f"FRQ:{int(300 + int(freq_global/1.517))-1} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/40*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
        while not sair.value():
            if c % 5 == 0:
                c = 0
                estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/40*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
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
                m_ = "fef"
            else:
                m_ = "zelda"

            if m_antigo != m_:
                lcd.clear()
                if m_ == "intro":
                    lcd.putstr("MUSICA:n[1]  2   3 ")
                elif m_ == "fef":
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

                if not entrar.value() and modo_global == "resfriar":
                    lcd.clear()
                    lcd.putstr("ESPEREnRESFRIAR...")
                    sleep(1)

                if not entrar.value() and modo_global != "resfriar":
                    modo_global = "manual"
                    lcd.clear()
                    solta_botao()
                    if c ==  "duty":
                        pot_antiga = 0
                        ciclos = 0
                        pot_visor = pot_global
                        while not sair.value():
                            pot_visor = mudar(seta.read(), pot_visor, 1)
                            if not entrar.value() and modo_global == "manual":
                                pot_global = pot_visor
                                try:
                                    pwm.duty(int(pot_global/4*limite))
                                except ValueError:
                                    pwm.duty(1023)
                                lcd.clear()
                                lcd.putstr(f"DUTY: {str(pot_global/40*limite)[0:4]}% <<nDUTY SETADO!")
                                sleep(1)
                            if abs(pot_visor - pot_antiga) > 10 and ciclos % 2_000 == 0:
                                lcd.clear()
                                lcd.putstr(f"DUTY: {str(pot_visor/40*limite)[0:4]}% <<nFREQ: {int(300 + int(freq_global/1.517))}")
                                pot_antiga = pot_visor
                                ciclos = 1
                            ciclos += 1
                    else:
                        freq_antiga = 0
                        ciclos = 0
                        freq_visor = freq_global
                        while not sair.value():
                            freq_visor = mudar(seta.read(), freq_visor, 1)
                            if not entrar.value() and modo_global == "manual":
                                freq_global = freq_visor
                                try:
                                    pwm.freq(int(300 + int(freq_global/1.517)))
                                except ValueError:
                                    pwm.freq(1)
                                lcd.clear()
                                lcd.putstr(f"FREQ SETADA!nFREQ: {int(300 + int(freq_global/1.517))} <<")
                                sleep(1)
                            if abs(freq_visor - freq_antiga) > 10 and ciclos % 2_000 == 0:
                                lcd.clear()
                                lcd.putstr(f"DUTY: {str(pot_global/40*limite)[0:4]}%nFREQ: {int(300 + int(freq_visor/1.517))} <<")
                                freq_antiga = freq_visor
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

    def connect_wifi(network = network):
        global net_global, ip_global

        if net_global == None:
            lcd.clear()
            lcd.putstr("LIGANDO WIFI...")
            net_global = network.WLAN(network.STA_IF)
            net_global.active()

        if net_global != None:
            if not net_global.isconnected()
                lcd.clear()
                lcd.putstr("ESCANEANDOnREDE...")
                list_of_wifi = net_global.scan()

                wifi = []
                for wifi_ in list_of_wifi:
                    if wifi_[3] == 0:
                        wifi.append(wifi_)
                lw = len(wifi)

                t = ""
                while not sair.value():
                    for i in range(lw):
                        if 4095/lw * i <= seta.read() < 4095/lw * (i + 1):
                            t_novo = f"REDE {i+1} de {lw}n{wifi[i][0].replace('n','N')[:16]}"
                            i_ = i

                    if t != t_novo:                          
                        lcd.clear()
                        lcd.putstr(t)
                        t = t_novo

                    if not entrar.value():
                        wifi_to_connect = wifi[i]
                        break

                    sleep(0.06)


                sta.connect(wifi_to_connect[0])
                if net_global.isconnected() :
                    lcd.clear()
                    lcd.putstr("WIFI CONECTADO!")
                    sleep(1)
                ip_global = net_global.ifconfig()
                
            if net_global.isconnected():
                c = 0
                while not sair.value():
                    if c % 20 == 0:
                        lcd.clear()
                        lcd.putstr(F"ENTRE EM:n{ip_global[0]}")
                        c = 0
                    c += 1
                    sleep(0.06)
        

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
    sensor_temperatura_1 = DS18X20(OneWire(Pin(5)))
    roms1 = sensor_temperatura_1.scan()
    temperatura = sensor_temperatura_1.read_temp(roms1[0])

    sensor_temperatura_2 = DS18X20(OneWire(Pin(17)))
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
    net_global = None
    ip_global = None
    temperatura_global_1, temperatura_global_2 = 0, 0
            
    #_thread.start_new_thread(plots,())
    _thread.start_new_thread(interface,())
    _thread.start_new_thread(vai_tela_descanso,())
    _thread.start_new_thread(tela_web,())
    
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

        if type(temperatura_global_1) == None:
            for _ in range(3):
                lcd.clear()
                lcd.putstr("SENSOR 1nDESCONECTADO!")
                sleep(1)
                lcd.clear()
                lcd.putstr("ENTRANDOnMODO SEGURANCA")
                sleep(1)
            temperatura_de_seguranca = 61

        if type(temperatura_global_2) == None:
            for _ in range(3):
                lcd.clear()
                lcd.putstr("SENSOR 2nDESCONECTADO!")
                sleep(1)
                lcd.clear()
                lcd.putstr("ENTRANDOnMODO SEGURANCA")
                sleep(1)
            temperatura_de_seguranca = 61

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

        if not modo_global == "resfriar" and not modo_global == "manual" and not modo_global == "musica":
            if modo_global == "eco" and modo_atual != modo_global:
                pwm.freq(665)
                pwm.duty(int(500/4*limite))
                freq_global = 554 # 554/1.517 + 300 = 665
                pot_global = 500
                modo_atual = modo_global
                
            elif modo_global == "turbo" and modo_atual != modo_global:
                pwm.freq(665)
                pwm.duty(int(1000/4*limite))
                freq_global = 554
                pot_global = 1000
                modo_atual = modo_global

            elif modo_global == "off" and modo_atual != modo_global:
                pwm.duty(0)
                pot_global = 0
                modo_atual = modo_global
            
