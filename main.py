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
from outros import mudar, tempo_h_m_s, criar_html
from login_wifi import login_wifi, senha_wifi
from wifi_esp32 import Wifi

def automatizacao_web():
    global automatizacao, modo_global, lcd, atual_automatizado
    sleep(5)

    while True:
        if "automatizacao" in globals():
            break
        sleep(0.5)      
    
    while True:
        automatizacao_nova = automatizacao
        atual_automatizado = -1
        if automatizacao != []:
            modo_auto = True
            lcd.clear()
            lcd.putstr("MODO\nAUTOMATICO")
            ani = 0
            for m, t in automatizacao_nova:
                atual_automatizado = ani
                modo_global = m
                for _ in range(t):
                    sleep(1)
                    if automatizacao_nova != automatizacao:
                        break
                ani += 1
        modo_auto = False
        sleep(1)

def tela_web():
    sleep(10)
    print("Começando tela_web!")
    global modo_global, ip_global, net_global, temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite, automatizado, atual_automatizado, memorias, memoria_uso

    def pagina_web(): #Página da web
        global html, modo_global, freq_global, temperatura_global_1, temperatura_global_2, temperatura_placa, gc, memorias, memoria_uso, acoes, pot_global
        temperatura_placa = str((esp32.raw_temperature() - 32) * 5/9)

        atual_ = []
        if atual_automatizado >= 0:
            atual_ = [0 for i in range(len(automatizado))]
            atual_[atual_automatizado] = 1

        acoes = [f" <tr> <td>{i}</td> <td>{x[0]}</td> <td>{x[1]}</td> <td>a</td> </tr> " for i, x, a in zip([i+1 for i in range(len(automatizado))], automatizado, atual_)]

        html = criar_html(modo_global, freq_global, temperatura_global_1, temperatura_global_2, temperatura_placa, gc, memorias, memoria_uso, acoes, pot_global)

        return html

    def logica_web(request): #Lógica para página na web
        if request.find("MODO=") > 1:
            pos = request.find("MODO=") + len("MODO=")
            num = request[pos:pos+1]
            print(f"Numero_da_altomatizacao: {num}")
            modo_global = f"modo_{num}"

        at = []
        if request.find(f"automatizar=1") > 1:
            for i in range(1, 5 + 1):
                if request.find(f"modo{i}=off{i}") > 1:
                    p = request.find(f"tempo{i}=")
                    lp = len("tempo1=")
                    t = request[p + lp: p + lp + 4]
                    ft = ""
                    for i in t:
                        if ord("0") <= ord(i) <= ord("9"):
                            ft += i
                    at.append(["modo_1", int(ft)])
                elif request.find(f"modo{i}=eco{i}") > 1:
                    p = request.find(f"tempo{i}=")
                    lp = len("tempo1=")
                    t = request[p + lp: p + lp + 4]
                    ft = ""
                    for i in t:
                        if ord("0") <= ord(i) <= ord("9"):
                            ft += i
                    at.append(["modo_2", int(ft)])
                elif request.find(f"modo{i}=turbo{i}") > 1:
                    p = request.find(f"tempo{i}=")
                    lp = len("tempo1=")
                    t = request[p + lp: p + lp + 4]
                    ft = ""
                    for i in t:
                        if ord("0") <= ord(i) <= ord("9"):
                            ft += i
                    at.append(["modo_3", int(ft)])
                elif request.find(f"modo{i}=full{i}") > 1:
                    p = request.find(f"tempo{i}=")
                    lp = len("tempo1=")
                    t = request[p + lp: p + lp + 4]
                    ft = ""
                    for i in t:
                        if ord("0") <= ord(i) <= ord("9"):
                            ft += i
                    at.append(["modo_4", int(ft)])
            automatizacao = at
            print(f"Automatização:\n{at}\n")
            globals()["automatizado"] = automatizacao

    contagem_memoria = -1
    while True:
        sleep(0.1)
        
        print("Lendo memoria para site...")
        memorias["temperatura_1"].append(temperatura_global_1)
        memorias["temperatura_2"].append(temperatura_global_2)
        memorias["temperatura_3"].append(str((esp32.raw_temperature() - 32) * 5/9))
        memorias["potencia"].append(pot_global)
        memorias["frequencia"].append(freq_global)

        for k_m in memorias.keys():
            if len(memorias[k_m]) > 30:
                memorias[k_m] = memorias[k_m][-100:]

        memoria_uso[modo_global] += 1
        
        if modo_global != "manual" and modo_global != "resfriar":
            if globals()["pode_conectar"]:
                gc.collect()
                resp = net_global.open_web_page(pagina_web, logica_web)

def interface():
    global telapot, lcd, login_wifi, senha_wifi

    def iterar_estatisticas():
        global temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite, ip_global, modo_nome
        nome_5_carac = modo_nome + " " * (5 - len(modo_nome))
        estat_antigo = f"{nome_5_carac} T1:{int(temperatura_global_1)}\nDUTY:{int(pot_global/1024*100 + 0.5)}% T2:{int(temperatura_global_2)}" 
        while True:
            try:
                nome_5_carac = modo_nome + " " * (5 - len(modo_nome))
                estat = f"{nome_5_carac} T1:{int(temperatura_global_1)}\nDUTY:{int(pot_global/1024*100 + 0.5)}% T2:{int(temperatura_global_2)}"
            except TypeError:
                print(f"Sem conversão para: {pot_global}")                
            if estat_antigo != estat:
                lcd.clear()
                lcd.putstr(estat)
                estat_antigo = estat
            sleep(0.2)
        lcd.clear()     

    wifi = Wifi(login_wifi, senha_wifi)
    ip_teste = wifi.connect()
    i = 0
    while ip_teste == None and i < 4:
        i += 1
        sleep(1)
        ip_teste = wifi.connect()
        lcd.clear()
        lcd.putstr(f"Conectando{'.'*i}")
        
    globals()["pode_conectar"] = True
    globals()["net_global"] = wifi
    globals()["ip_global"] = wifi.ip

    if ip_global != None:
        lcd.clear()
        lcd.putstr(f"IP: {ip_global}")
        sleep(3)
    iterar_estatisticas()
                
if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)                    
    ###Variável limite duty (1~40%):
    limite = 0.35

    #Para o visor:
    print("Ligando o visor (PIN 21 e 22)...")
    pino_visor_1, pino_visor_2 = 22, 21
    DEFALT_I2C_ADDR = 0x27

    i2c = I2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2), freq = 10000)
    lcd = I2cLcd(i2c, DEFALT_I2C_ADDR, 2, 16)
    lcd.clear()
    print("Visor ligado!\n")
    lcd.putstr(f"[{'#'*0}{' '*10}]")

    print("Ligando PWM (PIN 12)...")
    ###Saídas: 
    pwm = PWM(Pin(12))#Propriedades do canal PWN
    pwm.freq(300)
    pwm.duty(0)
    print("PWM ligado!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*2}{' '*8}]")
  
    #Como temos que mandar alguns volts ou saidas 0, 1 pelas portas fazemos:
    print("Ligando saida serial (PIN 13)...")
    ph6 = Pin(13, Pin.OUT)
    ph6.off() #Começa desligado
    sleep(3) #O Programa deve ficar inativo por n segundos...
    ph6.on()
    print("Saída serial ligada!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*4}{' '*6}]")

    ###Entradas:
    print("Ligando potenciometro (PIN 32)...")
    telapot = ADC(Pin(32))
    print(f"Potenciometro ligado, pos: {telapot.read()}!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*6}{' '*4}]")

    ###Parte para funções de curvas:
    potValue1 = 0
    potValueReal = 0 #Mudar o duty de maneira lenta
    estado, estado_ = 0, 0
    
    #Bloqueando:
    pwm_block = False
    contagem = 1

    #Para o sensor de temperatura ds18x20:
##    print("Ligando o sensor de temperatura 1 (PIN 5)")
##    sensor_temperatura_1 = DS18X20(OneWire(Pin(5)))
##    roms1 = sensor_temperatura_1.scan()
##    temperatura = sensor_temperatura_1.read_temp(roms1[0])
##    print(f"Sensor de temperatura 1 ligado!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*8}{' '*2}]")

    print("Ligando o sensor de temperatura 2 (PIN 16)")
    sensor_temperatura_2 = DS18X20(OneWire(Pin(16)))
    roms2 = sensor_temperatura_2.scan()
    temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
    print(f"Sensor de temperatura 2 ligado!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*9}{' '*1}]")

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
    modo_auto = False
    atual_automatizado = -1
    memoria_uso = {"modo_1":0,
                   "modo_2":0,
                   "modo_3":0,
                   "modo_4":0,
                   "manual":0,
                   "resfriar":0}
    memorias = {"temperatura_1":[],
                "temperatura_2":[],
                "temperatura_3":[],
                "potencia":[],
                "frequencia":[]}
    pode_conectar = False

    print("Ligando os threads...")
    _thread.start_new_thread(interface,())
    _thread.start_new_thread(tela_web,())
##    _thread.start_new_thread(automatizacao_web,())
    print("Threads ligados!")
    lcd.clear()
    lcd.putstr(f"[{'#'*10}{' '*0}]")
    
    #Loop principal:
    contagem = -1

    pwm.freq(432)
    while True:
        contagem += 1

        sensor = telapot.read()

        pot_global = mudar(pot_global, pot_ideal)
        pwm.duty(pot_global)

        if not modo_auto:
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
            temperatura_global_1 = 15
            temperatura_global_2 =  temperatura_de_seguranca

        if type(temperatura_global_1) == None:
            for _ in range(3):
                lcd.clear()
                lcd.putstr("SENSOR 1\nDESCONECTADO!")
                sleep(1)
                lcd.clear()
                lcd.putstr("ENTRANDO\nMODO SEGURANCA")
                sleep(1)
            temperatura_de_seguranca = 61

        if type(temperatura_global_2) == None:
            for _ in range(3):
                lcd.clear()
                lcd.putstr("SENSOR 2\nDESCONECTADO!")
                sleep(1)
                lcd.clear()
                lcd.putstr("ENTRANDO\nMODO SEGURANCA")
                sleep(1)
            temperatura_de_seguranca = 61

        if modo_auto:
            lcd.clear()
            lcd.putstr("MODO AUTOMATICO")
            sleep(0.5)

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
