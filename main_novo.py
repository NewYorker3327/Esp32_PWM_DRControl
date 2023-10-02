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

#Classes:
class Botao_adaptavel:
    def __init__(self, porta):
        self.real = Pin(porta, Pin.IN)
        if self.real.value() == 0:
            self.normal = True

    def value(self):
        resp = self.real.value()
        if self.normal:
            return resp
        else:
            if resp == 0:
                return 1
            else:
                0

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
                
def mudar(a:int, b:int, n = 1):
    if a > b:
        return b + n
    if a < b:
        return b - n
    return b

def tempo_h_m_s(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos = segundos % 60
    return f"{horas} hora(s), {minutos} minuto(s) e {segundos} segundo(s)"

def tela_web():
    global modo_global, ip_global, wifi_global, temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite, automatizado, atual_automatizado, memorias, memoria_uso

    def pagina_web():
        temperatura_placa = str((esp32.raw_temperature() - 32) * 5/9)

        atual_ = []
        if atual_automatizado >= 0:
            atual_ = [0 for i in range(len(automatizado))]
            atual_[atual_automatizado] = 1

        acoes = [f" <tr> <td>{i}</td> <td>{x[0]}</td> <td>{x[1]}</td> <td>a</td> </tr> " for i, x, a in zip([i+1 for i in range(len(automatizado))], automatizado, atual_)]
        
        html = """
    <html>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>
        
        <head>   
            <meta content="width=device-width, initial-scale=1" name="viewport"></meta>   
        </head>

        <style>
        table, th, td {
          border: 1px solid black;
        }

        .grafico-par {
            display: flex;
            flex-wrap: wrap;
        }

        .grafico-container {
            flex-basis: calc(50% - 20px); /* Divide em duas colunas com espaço entre elas */
            padding: 10px;
            box-sizing: border-box;
        }

        .grafico {
            width: 100%;
            max-width: 100%;
        }

        @media screen and (max-width: 900px) {
            .grafico-container {
                flex-basis: 100%; /* Uma coluna em telas menores */
            }
        }
        </style>

        <body>
            <center><p>Ligado a <strong>""" + tempo_h_m_s(sum(memoria_uso.values()) * 10) + """</strong>.</p></center>
            <center><h2>AGROMAG</h2></center>   
                <center>   
                 <form>   
                  <button name="MODO" type="submit" value="0"> OFF </button>   
                  <button name="MODO" type="submit" value="1"> ECO </button>
                  <button name="MODO" type="submit" value="2"> TURBO </button>  
                 </form>   
                </center>   
            <center><p>Modo atual: <strong>""" + str(modo_global) + """</strong>.</p></center>
            <center><p>Frequência: <strong>""" + str(int(300 + int(freq_global/1.517))-1) + """</strong>.</p></center>
            <center><p>Potência: <strong>""" + str(int(pot_global/40*limite + 0.9)) + """</strong>.</p></center>
            <center><p>Temperatura saída: <strong>""" + str(temperatura_global_1) + """</strong>.</p></center>
            <center><p>Temperatura da Placa: <strong>""" + str(temperatura_global_2) + """</strong>.</p></center>
            <center><p>Temperatura do Processador: <strong>""" + str(temperatura_placa) + """</strong>.</p></center>
            <center><p>Memória usada (kb): <strong>""" + str((512*1024 - gc.mem_alloc)/1024)[:6] + """/"""+ str(512) + """</strong>.</p></center>

            <br>

            <form>
                <input type="checkbox" id="automatizar" name="automatizar" value="1">
                <label for="vehicle1">Rodar automatização definida abaixo</label><br>
                  
                <label for="modo1">Ação 1 MODO e TEMPO (em minutos):</label>
                <select id="modo1" name="modo1">
                <option value="nada1" selected>NADA</option>
                    <option value="off1">OFF</option>
                    <option value="eco1">ECO</option>
                    <option value="turbo1">TURBO</option>
                  </select>
                  <input type="number" id="tempo1" name="tempo1" min="1" max="4320" value="1"> <p>

                <label for="modo2">Ação 2 MODO e TEMPO (em minutos):</label>
                <select id="modo2" name="modo1">
                <option value="nada2" selected>NADA</option>
                    <option value="off2">OFF</option>
                    <option value="eco2">ECO</option>
                    <option value="turbo2">TURBO</option>
                  </select>
                  <input type="number" id="tempo2" name="tempo2" min="1" max="4320" value="1"> <p>

                <label for="modo3">Ação 3 MODO e TEMPO (em minutos):</label>
                <select id="modo3" name="modo1">
                <option value="nada3" selected>NADA</option>
                    <option value="off3">OFF</option>
                    <option value="eco3">ECO</option>
                    <option value="turbo3">TURBO</option>
                  </select>
                  <input type="number" id="tempo3" name="tempo3" min="1" max="4320" value="1"> <p>

                <label for="modo4">Ação 4 MODO e TEMPO (em minutos):</label>
                <select id="modo4" name="modo1">
                <option value="nada4" selected>NADA</option>
                    <option value="off4">OFF</option>
                    <option value="eco4">ECO</option>
                    <option value="turbo4">TURBO</option>
                  </select>
                  <input type="number" id="tempo4" name="tempo4" min="1" max="4320" value="1"> <p>

                <label for="modo5">Ação 5 MODO e TEMPO (em minutos):</label>
                <select id="modo5" name="modo1">
                <option value="nada5" selected>NADA</option>
                    <option value="off5">OFF</option>
                    <option value="eco5">ECO</option>
                    <option value="turbo5">TURBO</option>
                  </select>
                  <input type="number" id="tempo5" name="tempo5" min="1" max="4320" value="1"> <p>

            <button type="submit">Salvar</button>
            <\form>

            <br>
            
            <h2>Automazização Atual:</h2>
            <table style="width:100%">
              <tr>
                <th>Ação</th> 
                <th>Modo</th> 
                <th>Tempo Dessa Ação (Minutos)</th>
                <th>Ativa no Momento</th>
              </tr>""" + acoes + """
            </table>


            <div class="grafico-par">
                <div class="grafico-container">
                    <canvas id="graficotemperatura" class="grafico"></canvas>
                </div>
                <div class="grafico-container">
                    <canvas id="graficopotencia" class="grafico"></canvas>
                </div>
            </div>

            <div class="grafico-par">
                <div class="grafico-container">
                    <canvas id="graficofrequencia" class="grafico"></canvas>
                </div>
                <div class="grafico-container">
                    <canvas id="myChart" class="grafico"></canvas>
                </div>
            </div>

            <script>
            const xValues = """ + str([i * -10 for i in range(len(memorias["temperatura_1"]))]) + """;

            new Chart("graficotemperatura", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{ 
                  data: """ + str(memorias["temperatura_1"]) + """,
                  borderColor: "blue",
                  fill: false,
                  label: "Saída" // Adicione o nome da série A aqui
                }, { 
                  data: """ + str(memorias["temperatura_2"]) + """,
                  borderColor: "green",
                  fill: false,
                  label: "Hardware" // Adicione o nome da série B aqui
                }, { 
                  data: """ + str(memorias["temperatura_3"]) + """,
                  borderColor: "red",
                  fill: false,
                  label: "Controlador"
                }]
              },
              options: {
                title: { 
                  display: true,
                  text: 'Temperaturas'
                },
                legend: {
                  display: true,
                  position: 'top',
                }
              }
            });


            new Chart("graficopotencia", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{ 
                  data: """ + str(memorias["potencia"]) + """,
                  borderColor: "red",
                  fill: false,
                  label: "Potência"
                }]
              },
              options: {
                title: { 
                  display: true,
                  text: 'Potência'
                },
                legend: {
                  display: false,
                  position: 'top',
                }
              }
            });


            new Chart("graficofrequencia", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{ 
                  data: """ + str(memorias["frequencia"]) + """,
                  borderColor: "red",
                  fill: false,
                  label: "Frequência"
                }]
              },
              options: {
                title: { 
                  display: true,
                  text: 'Frequência'
                },
                legend: {
                  display: false,
                  position: 'top',
                }
              }
            });


            const xValues2 = ["OFF", "ECO", "TURBO", "MANUAL", "RESFRIAR"];
            const yValues = """ + str(memoria_uso.values()) + """;
            const barColors = [
              "#808080",
              "#8ae580",
              "#e95151",
              "#feec35",
              "#16aeae"
            ];

            new Chart("myChart", {
              type: "pie",
              data: {
                labels: xValues2,
                datasets: [{
                  backgroundColor: barColors,
                  data: yValues
                }]
              },
              options: {
                title: {
                  display: true,
                  text: "Frequência de uso dos Modos (nos últimos """ + str(sum(memoria_uso.values()) * 10) + """ segundos)"
                }
              }
            });

            </script>
    
        </body>   
        </html>  
"""
        return html

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("", 80))
    soc.listen(5)

    while True:
        sleep(10)
        memorias["temperatura_1"].append(temperatura_global_1)
        memorias["temperatura_2"].append(temperatura_global_2)
        memorias["temperatura_3"].append(str((esp32.raw_temperature() - 32) * 5/9))
        memorias["potencia"].append(int(pot_global/40*limite + 0.9))
        memorias["frequencia"].append(int(300 + int(freq_global/1.517))-1)

        for k_m in memorias.keys():
            if len(memorias[k_m]) > 100:
                memorias[k_m] = memorias[k_m][-100:]

        memoria_uso[modo_global] += 1
        
        if modo_global != "manual" and modo_global != "resfriar" and modo_global != "musica":
            conn, addr = soc.accept()

            request = str(conn.recv(2048))
            if request.find("\?MODO=0") > 1:
                modo_global = "off"
            elif request.find("\?MODO=1") > 1:
                modo_global = "off"
            elif request.find("\?MODO=2") > 1:
                modo_global = "turbo"

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
                        at.append(["off", ft])
                    elif request.find(f"\?modo{i}=eco{i}") > 1:
                        p = request.find(f"\?tempo{i}=")
                        lp = len("\?tempo1=")
                        t = request[p + lp: p + lp + 4]
                        ft = ""
                        for i in t:
                            if ord("0") <= ord(i) <= ord("9"):
                                ft += i
                        at.append(["off", ft])
                    elif request.find(f"\?modo{i}=turbo{i}") > 1:
                        p = request.find(f"\?tempo{i}=")
                        lp = len("\?tempo1=")
                        t = request[p + lp: p + lp + 4]
                        ft = ""
                        for i in t:
                            if ord("0") <= ord(i) <= ord("9"):
                                ft += i
                        at.append(["off", ft])
                automatizacao = at
            print(at,"<< automatização")

            response = pagina_web()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

            conn.close()    

def interface():
    global telapot, lcd, ip_global

    def interar_estatisticas():
        global temperatura_global_1, temperatura_global_2, freq_global, pot_global, limite, ip_global
        c = 0
        estat_antigo = f"FRQ:{int(300 + int(freq_global/1.517))-1} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/40*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
        k = 0
        while True:
            if c % 5 == 0:
                k += 1
                c = 0
                if k % 5 == 0:
                    estat = f"FRQ:{int(300 + int(freq_global/1.517))} T1:{int(temperatura_global_1)}nDUTY:{int(pot_global/40*limite + 0.9)}% T2:{int(temperatura_global_2)}" 
                else:
                    estat = f"IP: {ip_global}"
                if estat_antigo != estat:
                    lcd.clear()
                    lcd.putstr(estat)
                    estat_antigo = estat
            sleep(0.02)
        lcd.clear()     

    def interar_wifi(network = network):
        global net_global, ip_global

        if net_global == None:
            lcd.clear()
            lcd.putstr("LIGANDO WIFI...")
            net_global = network.WLAN(network.STA_IF)
            net_global.active()

        if net_global != None:
            if not net_global.isconnected():
                list_of_wifi = net_global.scan()

                wifi = []
                for wifi_ in list_of_wifi:
                    if wifi_[3] == 0:
                        wifi.append(wifi_)
                lw = len(wifi)
                
                wifi_to_connect = wifi[i]
                sta.connect(wifi_to_connect[0])
                ip_global = net_global.ifconfig()[0]

    seta = telapot
    entrar = telabot
    sair = telabot_2
    iterar_wifi()
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
    lcd.putstr("    AGROMAGnLIGANDO...")

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
    automatizado = []
    atual_automatizado = -1
    memoria_uso = {"off":0,
                   "eco":0,
                   "turbo":0,
                   "manual":0,
                   "resfriar":0}
    memorias = {"temperatura_1":[],
                "temperatura_2":[],
                "temperatura_3":[],
                "potencia":[],
                "frequencia":[]}

    _thread.start_new_thread(interface,())
    _thread.start_new_thread(tela_web,())
    
    #Loop principal:
    contagem = 0  
    while True:
        contagem += 1
        
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
            
