#Transcrição identica de código em c simplificado para micropython
#Existem algumas partes que não precissavam mas foi feito assim para
#padronizar com o outro código

#Bibliotecas:
from time import sleep
from machine import Pin, PWM, ADC
import onewire
import ds18x20
import dht

def musicas(mus:str, obj):
    temp = 8
    if mus == "intro":
        mus = [[294+587, 2], [370+784, 2], [466+1175, 2], [587+1568, 2],
               [784+2093, 2], [1175+2349, 2]]

        

    if mus == "exit":
        mus = [[1568+784, 2], [1175+587, 2], [784+523, 2], [587+294, 2],
               [523+392, 2]]

    for nota in mus:
        obj.freq(nota[0])
        sleep(nota[1]/temp)
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
    h4 = 4 #Tensão do banco de capacitores, vai de 0 a 3v
    entrada_h4 = 1
    
    h8 = 15 #Detecção de sobrecorrente, 3.1v
    entrada_h8 = 0
    
    h11 = 2 #Detecção de supra-tensão, 1.8v
    entrada_h11 = 0
    
    h13 = 13 #//Temperatura
    entrada_h13 = 0
    sensor = ds18x20.DS18X20(onewire.OneWire(Pin(h13)))
    roms = sensor.scan()
    
    sw3 = 32; #Se for 1 o protocolo funciona
    entrada_sw3 = 0
    
    ###Entradas:
    rp3 = 26 #Esse é o pino que "receberá o valor" do potenciometro para o PWM duty 33
    prp3 = ADC(Pin(rp3))
    rp2 = 14 #Esse é o pino que "receberá o valor" do potenciometro para a frequência 12
    prp2 = ADC(Pin(rp2))
    
    ###Saídas:
    h6 = 27 #Pré-carga
    h9 = 25 #PWM
    
    ###Parte para funções de curvas:
    potValue1, potValue2 = 0, 0
    
    potValueReal = 0 #Mudar o duty de maneira lenta
    potValueReal2 = 0 #Mudar a frequência de maneira lenta
    estado, estado_ = 0, 0
    
    #Propriedades do canal PWN
    ledChannel = h9
    pwm = PWM(Pin(ledChannel))
    freq = pwm.freq(294+587)
    resolution = 8 # Vai de 0 a 2^8-1 = 255
    dutyCycle = pwm.duty(resolution**2) # Vai de 0 = 0% a 2^8-1 = 255 = 100%
    dutyCycle_ = 2
    
    #Bloqueando:
    pwm_block = False
    contagem = 1
    
#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                            
    #Mesma estrutura do void Setup do outro código:

    #Pinos que irão receber valores:
    ph4 = ADC(Pin(h4))
    ph8 = ADC(Pin(h8))
    ph11 = ADC(Pin(h11))
    ph13 = ADC(Pin(h13))
    
    #Botão de segurança:
    psw3 = ADC(Pin(sw3))

    #Como temos que mandar alguns volts ou saidas 0, 1 pelas portas fazemos:
    ph6 = Pin(h6, Pin.OUT)

    #O Programa deve ficar inativo por 2 segundos...
    sleep(1)

    #Permanece [0] até que [H4 (V_BUS)] seja maior que [3V]
    #while ph4.read() < 1241 * 3:
    #    sleep(0.001)

    #Ativa o sensor:
    #sensor.convert_temp()
    
    pwm.freq(1)

    musicas("intro", pwm)
    
    #Loop principal:
    while True:
        contagem += 1
  
        if pwm_block == False: 
            potValue1 = prp3.read() #Lê o Duty
            potValueReal = mudar(potValue1, potValueReal)

        if pwm_block == False:
            potValueReal2 = prp2.read() #Lê a frequência
            
        if (mod(potValueReal-potValue1) > 30 or estado_ != estado  or mod(potValueReal2-potValue2)> 30 ) and contagem % 25 == 0:
            if mod(potValueReal2-potValue2) > 30:
                try:
                    pwm.freq(int (int((25 * int(freq/25)))/4))
                except ValueError:
                    pwm.freq(25)
            estado_ = estado
            potValue2 = potValueReal2
        #try:
        pwm.duty(dutyCycle_)
        #except TypeError:
        #    pwm.duty()
        
        if potValueReal2 < -50: #Ele desliga se a frequencia está em um valor muito baixo.
            dutyCycle = 0
            potValueReal2 = 0
            potValueReal = 0
            estado = 0
        else:
            estado = 1
            dutyCycle_ = int(potValueReal/16 * 1.6) #//0(0%) a 255*0,4(40%)
            freq = potValueReal2

        #Lógica quando h4 for maior do que 2.5v a saída é 1 h6:
        if ph4.read() > 1241 * 2.5:
            ph6.on()
        else:
            ph6.off()
        
        #Lê a temperatura:
        if contagem % 50 == 0:
            #sensor.convert_temp()
            #entrada_h13 = sensor.read_temp(roms[0])
            contagem = 1
       
        #[H9] vai a [0] sempre que [H11 (UVLO]) for menor que [1.8 VOLTS], indicando um [evento de supra-tensão]
        #[H9] vai a [0] sempre que [H13 (Temperatura)] for maior que 110C°, indicando um [evento de sobre-temperatura]
        #Se o botão estiver desativado
#         if entrada_h13 > 110 or ph11.read() < 1241 * 1.8 or ph8.read() > 1241 * 2.5 or psw3.read() < 1000: 
#             potValueReal = 0 # potValueReal é o valor que o pwm tem que 
#             pwm_block = True # Ele trava a leitura do duty(porcentagem) do pwm
#         else:
#             pwm_block = False # Ele deixa que o programa leia o valor do pwm
    
