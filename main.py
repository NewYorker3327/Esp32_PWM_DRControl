#Bibliotecas:
from time import sleep, time
from machine import Pin, PWM, ADC
from machine import SoftI2C as I2C
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
from portas import *
from outros import mudar, tempo_h_m_s, criar_html, criar_html_grafico
from login_wifi import login_wifi, senha_wifi
from wifi_esp32 import Wifi
from ws2812b_hub import Leds, color

def automatizacao_web():
    global automatizacao, modo_global, lcd, atual_automatizado
    sleep(5)   
    
    while True:
        try:
            automatizacao_nova = automatizacao
        except NameError:
            automatizacao = []
            automatizacao_nova = []
        atual_automatizado = -1
        print(f"Atual: {automatizacao}")
        if automatizacao != []:
            globals()["modo_auto"] = True
            lcd.clear()
            lcd.putstr("MODO\nAUTOMATICO")
            ani = 0
            for m, t in automatizacao_nova:
                print(f"{m}>>{t}{type(t)}")
                atual_automatizado = ani
                globals()["modo_global"] = m
                for _ in range(t):
                    sleep(1)
                ani += 1
            automatizacao = []
            automatizacao_nova = []
        globals()["modo_auto"] = False
        sleep(2)

def tela_web():
    sleep(10)
    print("Começando tela_web!")
    global memorias, memoria_uso

    def pagina_web(): #Página da web
        global tipo_html, modo_global, freq_global, temperatura_global_1, temperatura_global_2, temperatura_placa, gc, memorias, memoria_uso, acoes, pot_global
        temperatura_placa = str((esp32.raw_temperature() - 32) * 5/9)

##        atual_ = []
##        if atual_automatizado >= 0:
##            atual_ = [0 for i in range(len(automatizado))]
##            atual_[atual_automatizado] = 1

        #Podem ser 2 htmls, o de automatização e o de gráfico:
        if tipo_html == "automatizacao":
            html = criar_html(modo_global, freq_global, temperatura_global_1, temperatura_global_2, temperatura_placa, gc, pot_global, memoria_uso)
        elif tipo_html == "grafico":
            acoes = [f" <tr> <td>{i}</td> <td>{x[0]}</td> <td>{x[1]}</td> <td>a</td> </tr> " for i, x, a in zip([i+1 for i in range(len(automatizado))], automatizado, atual_)]
            html = criar_html_grafico(memorias, memoria_uso, acoes) 

        return html

    def logica_web(request): #Lógica para página na web
        at = []
        #request = request[3:-2].decode("utf-8")
        print(type(request), request[:10])
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
            globals()["automatizacao"] = at
            print(f"Automatização:\n{at}\n")

        elif request.find("MODO=") > 1:
            pos = request.find("MODO=") + len("MODO=")
            num = request[pos:pos+1]
            print(f"Numero_da_altomatizacao: {num}")
            modo_global = f"modo_{num}"

    contagem_memoria = -1
    while True:
        sleep(0.5)
        
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
                if globals()["net_global"] != None:
                    if globals()["net_global"].is_connected():
                        resp = globals()["net_global"].open_web_page(pagina_web, logica_web)
                    else:
                        sleep(5)
                        interface()

def iterar_estatisticas():
    global temperatura_global_1, temperatura_global_2, freq_global, pot_global, ip_global, modo_nome, modo_global
    nome_5_carac = modo_nome + " " * (5 - len(modo_nome))
    estat_antigo = f"{nome_5_carac}    T1:{int(temperatura_global_1)}  DUTY:{int(pot_global/1024*100 + 0.5):02d}% T2:{int(temperatura_global_2)}"
    while True:
        if modo_global != "resfriar":
            try:
                nome_5_carac = modo_nome + " " * (5 - len(modo_nome))
                estat = f"{nome_5_carac}    T1:{int(temperatura_global_1)}  DUTY:{int(pot_global/1024*100 + 0.5):02d}% T2:{int(temperatura_global_2)}"
            except TypeError:
                print(f"Sem conversão para: {pot_global}")
            if estat_antigo != estat:
                lcd.clear()
                lcd.putstr(estat)
                estat_antigo = estat
        sleep(0.2)
    lcd.clear()

def animacao_espera():
    global ip_teste
    i = 0
    while ip_teste == False:
        lcd.clear()
        lcd.putstr(f"Conectando{'.'*i}")
        led.animation("wait", color["red"])
        if i > 0 and i % 3 == 0:
            i = 0
        i += 1
    
def interface():
    global telapot, lcd, login_wifi, senha_wifi, ip_teste

    wifi = Wifi(login_wifi, senha_wifi)

    globals()["ip_teste"] = wifi.connect_continuos()
        
    globals()["net_global"] = wifi
    globals()["ip_global"] = wifi.ip
    globals()["pode_conectar"] = True

    lcd.clear()
    lcd.putstr(f"IP: {ip_global}")
                
if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)

    pode_conectar = False
    ip_teste = False
    sensor = 0
    freq_global = 0
    pot_global = 0
    pot_ideal = 0
    modo_global = "off"
    modo_nome = "OFF"
    modo_atual = ""
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
    tipo_html = "grafico"#"automatizacao"

    ###Parte para funções de curvas:
    potValue1 = 0
    potValueReal = 0 #Mudar o duty de maneira lenta
    estado, estado_ = 0, 0

    #Bloqueando:
    contagem = 1

    print("Ligando os leds (PIN {pino_led})")
    led = Leds(door = pino_led, width = 32)
    led.animation("load", value = 5)

    #Para o visor:
    print("Ligando o visor (PIN {pino_visor_1} e {pino_visor_2})...")
    i2c = I2C(scl = Pin(pino_visor_1), sda = Pin(pino_visor_2), freq = 10000)
    lcd = I2cLcd(i2c, DEFALT_I2C_ADDR, 2, 16)
    lcd.clear()
    print("Visor ligado!\n")
    lcd.putstr(f"[{'#'*0}{' '*10}]")
    led.animation("load", value = 10)

    _thread.start_new_thread(interface,())
    _thread.start_new_thread(animacao_espera,())

    print("Ligando PWM (PIN {pino_pwm})...")
    ###Saídas: 
    pwm = PWM(Pin(pino_pwm))#Propriedades do canal PWN
    pwm.freq(300)
    pwm.duty(0)
    print("PWM ligado!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*2}{' '*8}]")
    led.animation("load", value = 15)
  
    #Como temos que mandar alguns volts ou saidas 0, 1 pelas portas fazemos:
    print("Ligando saida serial (PIN {serial_pino})...")
    ph6 = Pin(serial_pino, Pin.OUT)
    ph6.off() #Começa desligado
    sleep(inatividade_serial) #O Programa deve ficar inativo por n segundos...
    ph6.on()
    print("Saída serial ligada!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*4}{' '*6}]")
    led.animation("load", value = 20)

    ###Entradas:
    print("Ligando potenciometro (PIN {pino_potenciometro})...")
    telapot = ADC(Pin(pino_potenciometro))
    telapot.atten(ADC.ATTN_11DB)
    print(f"Potenciometro ligado, pos: {telapot.read()}!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*6}{' '*4}]")
    led.animation("load", value = 25)

    #Para o sensor de temperatura ds18x20:
##    print("Ligando o sensor de temperatura 1 (PIN {pino_temperatura_1})")
##    sensor_temperatura_1 = DS18X20(OneWire(Pin(pino_temperatura_1)))
##    roms1 = sensor_temperatura_1.scan()
##    temperatura = sensor_temperatura_1.read_temp(roms1[0])
##    print(f"Sensor de temperatura 1 ligado!\n")
##    lcd.clear()
##    lcd.putstr(f"[{'#'*8}{' '*2}]")
    led.animation("load", value = 27)

    print("Ligando o sensor de temperatura 2 (PIN {pino_temperatura_2})")
    sensor_temperatura_2 = DS18X20(OneWire(Pin(pino_temperatura_2)))
    roms2 = sensor_temperatura_2.scan()
    temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
    print(f"Sensor de temperatura 2 ligado!\n")
    lcd.clear()
    lcd.putstr(f"[{'#'*9}{' '*1}]")
    led.animation("load", value = 30)

#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                                

    led.animation("load", value = 32)
    
    print("Ligando os threads...")
    _thread.start_new_thread(iterar_estatisticas,())
    _thread.start_new_thread(tela_web,())
    _thread.start_new_thread(automatizacao_web,())
    print("Threads ligados!")
    lcd.clear()
    lcd.putstr(f"[{'#'*10}{' '*0}]")
    
    #Loop principal:
    contagem = -1

    pwm.freq(432)
    while True:
        contagem += 1

        sensor = telapot.read()

        if modo_auto:
            pot_global = pot_ideal
        else:
            pot_global = mudar(pot_global, pot_ideal, n = 1)
        
        pwm.duty(pot_global)

        if not modo_auto:
            if 0 < sensor < 4096/4 - margem:
                modo_global = "modo_1"
            elif 4096/4 + margem < sensor < 4096/2 - margem:
                modo_global = "modo_2"
            elif 4096/2 + margem < sensor < 4096/4 * 3 - margem:
                modo_global = "modo_3"
            elif 4096/4 * 3 + margem < sensor < 4096:
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

        try:
            if temperatura_de_seguranca > temperatura_maxima_aceitavel or modo_global == "resfriar": #As vezes a variável (temp...) não é lida corretamente 
                if modo_global != "resfriar":
                    backup_modo_global = modo_global
                    pwm.duty(0)
                    pot_global = 0
                    modo_atual = modo_global
                    modo_global = "resfriar"
                    lcd.clear()
                    lcd.putstr("RESFRIANDO!")
                    
                sleep(0.1)
                    
                modo_global = "resfriar"

                sensor_temperatura_2.convert_temp()
                if sensor_temperatura_2.read_temp(roms2[0]) < tempetatura_de_volta:
                    modo_global = backup_modo_global
                    temperatura_de_seguranca = sensor_temperatura_2.read_temp(roms2[0])
                    temperatura_global_2 = temperatura_de_seguranca
        except TypeError:
            pass

        if not modo_global == "resfriar":
            if modo_global == "modo_1" and modo_atual != modo_global:
                for i in range(31):
                    led.draw_in(i, [20, 10, 10])
                    sleep(0.01)
                pot_ideal = 0
                modo_atual = modo_global
                modo_nome = "OFF"
                
            elif modo_global == "modo_2" and modo_atual != modo_global:
                for i in range(31):
                    led.draw_in(i, color["green"])
                    sleep(0.01)
                pot_ideal = int(4096/400*porcentagem_modo_2)
                modo_atual = modo_global
                modo_nome = "ECO"

            elif modo_global == "modo_3" and modo_atual != modo_global:
                for i in range(31):
                    led.draw_in(i, color["blue"])
                    sleep(0.01)
                pot_ideal = int(4096/400*porcentagem_modo_3)
                modo_atual = modo_global
                modo_nome = "TURBO"

            elif modo_global == "modo_4" and modo_atual != modo_global:
                for i in range(31):
                    led.draw_in(i, color["blueviolet"])
                    sleep(0.01)
                pot_ideal = int(4096/400*porcentagem_modo_4)           
                modo_atual = modo_global
                modo_nome = "FULL"

        else:
            sensor_temperatura_2.convert_temp()
            temporario = sensor_temperatura_2.read_temp(roms2[0])
            print(f"Modo Resfriar {temporario} {type(temporario)}")
            if type(temporario) == float:
                for i in range(31):
                    led.leds[i] = [0, 60, 255]
                for i in range(min(31, (temporario-39))):
                    led.leds[i] = color["fire"]
                led.leds.write()
