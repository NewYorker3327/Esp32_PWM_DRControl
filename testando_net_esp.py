"""
Teste de Conexão da ESP
"""
print("Iniciando teste de conexão...")

import socket
import network
from gc import mem_free, collect
from time import sleep

def por_wifi(network = network):
    net_global = network.WLAN(network.STA_IF)
    net_global.active()

    if net_global != None:
        if not net_global.isconnected():
            list_of_wifi = net_global.scan()
            print(list_of_wifi)

            wifi = []
            for wifi_ in list_of_wifi:
                if wifi_[3] == 0:
                    wifi.append(wifi_)
            lw = len(wifi)
                
            wifi_to_connect = wifi[i]
            sta.connect(wifi_to_connect[0])
            ip_global = net_global.ifconfig()[0]
    print(f"NET: {net_global}\nIP: {ip_global}")
    return net_global, ip_global

print("Criando socket")
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Abrindo porta 80")
soc.bind(("", 80))

print("Aberto para ouvir")
soc.listen(5)
print(f"socket: {soc}")

while True:
    conn, addr = soc.accept()
    print(f"Conn: {conn}\n Addr: {addr}")

    request = str(conn.recv(2048))
    print(f"Request: {request}")
    
    sleep(3)
    m_livre = mem_free()
    print(f"Memoria livre {m_livre}...\n\n")

    response = f"Quantidade de Memoria Livre: {m_livre}"
    conn.send("HTTP/1.1 200 OK\n")
    conn.send("Content-Type: text/html\n")
    conn.send("Connection: close\n\n")
    conn.sendall(response)

    conn.close()
    
