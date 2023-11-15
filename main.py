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

#Temperatuda da propria esp:
import esp32
#esp32.raw_temperature()

#Medir memória:
from gc import mem_free, collect

#Proprios:
from outros import mudar, tempo_h_m_s, iterar_wifi, criar_html
from login_wifi import login_wifi, senha_wifi

def automatizacao_web():
    global automatizacao, modo_global, lcd, atual_automatizado
    
    while True:
        automatizacao_nova = automatizacao
        atual_automatizado = -1
        if automatizacao != []:
            lcd.clear()
            lcd.putstr("MODOnAUTOMATICO")
            ani = 0
            for m, t in automatizacao_nova:
                atual_automatizado = ani
                modo_global = m
                for _ in range(60):
                    sleep(m)
                    if automatizacao_nova != automatizacao:
                        break
                ani += 1
        sleep(3)

def tela_web():
    global modo_global, ip_global, wifi_global, temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite, automatizado, atual_automatizado, memorias, memoria_uso

    def pagina_web():
        global html
        temperatura_placa = str((esp32.raw_temperature() - 32) * 5/9)

        atual_ = []
        if atual_automatizado >= 0:
            atual_ = [0 for i in range(len(automatizado))]
            atual_[atual_automatizado] = 1

        acoes = [f" <tr> <td>{i}</td> <td>{x[0]}</td> <td>{x[1]}</td> <td>a</td> </tr> " for i, x, a in zip([i+1 for i in range(len(automatizado))], automatizado, atual_)]

        html = criar_html(modo_global, freq_global, temperatura_global_1, temperatura_global_2, temperatura_placa, gc, memorias, memoria_uso, acoes)

        return html

    print("Ligando socket")
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("", 80))
    soc.listen(5)
    print(soc)
    while True:
        sleep(5)
        print("Lendo...")
        memorias["temperatura_1"].append(temperatura_global_1)
        memorias["temperatura_2"].append(temperatura_global_2)
        memorias["temperatura_3"].append(str((esp32.raw_temperature() - 32) * 5/9))
        memorias["potencia"].append(pot_global)
        memorias["frequencia"].append(freq_global)

        for k_m in memorias.keys():
            if len(memorias[k_m]) > 100:
                memorias[k_m] = memorias[k_m][-100:]

        memoria_uso[modo_global] += 1
        
        if modo_global != "manual" and modo_global != "resfriar":
            conn, addr = soc.accept()
            print(conn, addr)

            request = str(conn.recv(2048))
            if request.find("\?MODO=") > 1:
                pos = request.find("\?MODO=") + len("\?MODO=")
                num = request[pos:pos+1]
                print(f"Numero_da_altomatizacao: {num}")
                modo_global = f"modo_{num}"
##            elif request.find("\?MODO=1") > 1:
##                modo_global = "modo_2"
##            elif request.find("\?MODO=2") > 1:
##                modo_global = "modo_3"
##            elif request.find("\?MODO=3") > 1:
##                modo_global = "modo_4"

            at = []
            if request.find(f"\?automatizar=1") > 1:
                for i in range(1, 5 + 1):
                    if request.find(f"\?modo{i}=off{i}") > 1:
                        p = request.find(f"\?tempo{i}=")
                        lp = len("\?tempo1=")
                        t = request[p + lp: p + lp + 4]
                        ft = ""
                        for i in t:
                            if ord("0") <= ord(i) <= ord("9"):
                                ft += i
                        at.append(["modo_1", ft])
                    elif request.find(f"\?modo{i}=eco{i}") > 1:
                        p = request.find(f"\?tempo{i}=")
                        lp = len("\?tempo1=")
                        t = request[p + lp: p + lp + 4]
                        ft = ""
                        for i in t:
                            if ord("0") <= ord(i) <= ord("9"):
                                ft += i
                        at.append(["modo_2", ft])
                    elif request.find(f"\?modo{i}=turbo{i}") > 1:
                        p = request.find(f"\?tempo{i}=")
                        lp = len("\?tempo1=")
                        t = request[p + lp: p + lp + 4]
                        ft = ""
                        for i in t:
                            if ord("0") <= ord(i) <= ord("9"):
                                ft += i
                        at.append(["modo_3", ft])
                    elif request.find(f"\?modo{i}=full{i}") > 1:
                        p = request.find(f"\?tempo{i}=")
                        lp = len("\?tempo1=")
                        t = request[p + lp: p + lp + 4]
                        ft = ""
                        for i in t:
                            if ord("0") <= ord(i) <= ord("9"):
                                ft += i
                        at.append(["modo_4", ft])
                automatizacao = at
            print(at,"<< automatização")

            response = pagina_web()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

            conn.close()    

def interface():
    global net_global, telapot, lcd, ip_global, login_wifi, senha_wifi

    def iterar_estatisticas():
        global temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite, ip_global, modo_nome
        nome_5_carac = modo_nome + " " * (5 - len(modo_nome))
        estat_antigo = f"{nome_5_carac} T1:{int(temperatura_global_1)}\nDUTY:{int(pot_global/1024*100 + 0.5)}% T2:{int(temperatura_global_2)}" 
        while True:
            nome_5_carac = modo_nome + " " * (5 - len(modo_nome))
            estat = f"{nome_5_carac} T1:{int(temperatura_global_1)}\nDUTY:{int(pot_global/1024*100 + 0.5)}% T2:{int(temperatura_global_2)}" 
            if estat_antigo != estat:
                lcd.clear()
                lcd.putstr(estat)
                estat_antigo = estat
            sleep(0.2)
        lcd.clear()     

    net_global, ip_global = iterar_wifi(login_wifi, senha_wifi)
    if ip_global != None:
        lcd.clear()
        lcd.putstr(f"IP: {ip_global}")
        sleep(5)
    iterar_estatisticas()
                
if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)                    
    ###Variável limite duty (1=100%):
    limite = 0.35

    #Para o visor:
    pino_visor_1, pino_visor_2 = 22, 21
    DEFALT_I2C_ADDR = 0x27

    i2c = I2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2), freq = 10000)
    lcd = I2cLcd(i2c, DEFALT_I2C_ADDR, 2, 16)
    lcd.clear()
    lcd.putstr("LIGANDO...")

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
    telapot = ADC(Pin(4))

    ###Parte para funções de curvas:
    potValue1 = 0
    potValueReal = 0 #Mudar o duty de maneira lenta
    estado, estado_ = 0, 0
    
    #Bloqueando:
    pwm_block = False
    contagem = 1

    #Para o sensor de temperatura ds18x20:
##    sensor_temperatura_1 = DS18X20(OneWire(Pin(5)))
##    roms1 = sensor_temperatura_1.scan()
##    temperatura = sensor_temperatura_1.read_temp(roms1[0])

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
    sensor = 0
    toca_mus = True
    freq_global = 0
    pot_global = 0
    pot_ideal = 0
    modo_global = "off"
    modo_nome = "OFF"
    modo_atual = ""
    pausa_de_seguranca = False
    net_global = None
    ip_global = None
    temperatura_global_1, temperatura_global_2 = 0, 0
    automatizado = []
    atual_automatizado = -1
    memoria_uso = {"modo_1":0,
                   "modo_2":0,
                   "modo_3":0,
                   "modo_4":0,
                   "resfriar":0}
    memorias = {"temperatura_1":[],
                "temperatura_2":[],
                "temperatura_3":[],
                "potencia":[],
                "frequencia":[]}

    _thread.start_new_thread(interface,())
    _thread.start_new_thread(tela_web,())
##    _thread.start_new_thread(automatizacao_web,())
    
    #Loop principal:
    contagem = 0

    pwm.freq(432)
    while True:
        contagem += 1

        pot_global = mudar(pot_global, pot_ideal)
        pwm.duty(pot_global)

        sensor = telapot.read()

        if sensor < 4096/4:
            modo_global = "modo_1"
        elif sensor < 4096/2:
            modo_global = "modo_2"
        elif sensor < 4096/4 * 3:
            modo_global = "modo_3"
        else:
            modo_global = "modo_4"
        
        if contagem % 1000 == 0:
            contagem = 1
##            sensor_temperatura_1.convert_temp()
            sensor_temperatura_2.convert_temp()
##            temperatura = sensor_temperatura_1.read_temp(roms1[0])
            temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
##            temperatura_global_1 = temperatura
            temperatura_global_1 = 25
            temperatura_global_2 =  temperatura_de_seguranca

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
                pwm.duty(0)
                pot_global = 0
                lcd.clear()
                lcd.putstr("RESFRIANDO!")
                modo_global = "resfriar"
                modo_atual = modo_global
                sleep(3)

            modo_global = "resfriar"

            if temperatura_de_seguranca < 40:
                modo_global = backup_modo_global

        if not modo_global == "resfriar":
            if modo_global == "modo_1" and modo_atual != modo_global:
                pot_ideal = 0
                modo_atual = modo_global
                modo_nome = "OFF"
                
            elif modo_global == "modo_2" and modo_atual != modo_global:
                pot_ideal = int(4096/400*12)
                modo_atual = modo_global
                modo_nome = "ECO"

            elif modo_global == "modo_3" and modo_atual != modo_global:
                pot_ideal = int(4096/400*32)
                modo_atual = modo_global
                modo_nome = "TURBO"

            elif modo_global == "modo_4" and modo_atual != modo_global:
                pot_ideal = int(4096/400*40)           
                modo_atual = modo_global
                modo_nome = "FULL"         
