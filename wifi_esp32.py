"""
Connect to WiFi
"""

import socket
import network
import gc
from time import sleep

class Wifi:
    """
    Class to connect esp32 to wifi
    """
    def __init__(self, login, password, ips:tuple = ("192.168.0.100", "255.255.255.0", "192.168.10.1", "8.8.8.8")):
        """
        Starts with login and password
        """
        self.net = network.WLAN(network.STA_IF)
        if type(login) != list:
            login = [login]
        self.login = login
        if type(password) != list:
            password = [password]
        self.password = password
        self.ifconfig = ips
        self.net.active(False)
        self.ip = None
        self.config = None

    def connect(self):
        """
        Try connecting to wifi
        """
        print("Connecting...")
        sleep(0.5)
        if not self.net.isconnected():
            self.net.active(True)
            self.net.ifconfig(self.ifconfig)
            for login_wifi in self.login:
                for password_wifi in self.password:
                    print(f"Try: {login_wifi} {password_wifi}")
                    tryes_connect = 3
                    while tryes_connect > 0:
                        try:
                            self.net.connect(login_wifi, password_wifi)
                            tryes_connect = 0
                        except:
                            print("Try to connect again...")
                            tryes_connect -= 1
                        sleep(0.5)
                    if self.net.isconnected():
                        self.ip = self.net.ifconfig()[0]
                        self.config = self.net.ifconfig()
                        print(f"{'-'*10}CONFIG{'-'*10}")
                        for line in self.config:
                            print(line)
                        return self.config
        else:
            print("Already connected...")
            self.ip = self.net.ifconfig()[0]
            self.config = self.net.ifconfig()
            print(f"{'-'*10}CONFIG{'-'*10}")
            for line in self.config:
                print(line)
            return self.config
                    
    def is_connected(self):
        return self.net.isconnected()

    def open_web_page(self, page, logic, times = 30, args_page:dict = None, args_logic:dict = None):
        """
        Open a web page using a socket and read the result after a certain time
        """
        if self.ip == None:
            print("Connect to wifi first...")
            return None
        times_try = 0
        while not self.net.isconnected() and times_try < 3:
            print("Not connected to Wi-Fi...")
            times_try += 1
            sleep(1)
        
        if self.net.isconnected():
            print("Connected in wifi!")
            
        times_try = 5
        connected_now = False
        while not connected_now and times_try > 0:
            try:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.bind(('', 80))
                soc.listen(3) #Max of listen
                connected_now = True
            except OSError:
                print(f"Try open socket again...")
                sleep(0.5)
            times_try -= 1
        
        if not connected_now:
            print("Unable to open socket!")
            return False

        if self.net.isconnected():
            while times > 0:                
                print(f"Remaining connections {times}...")
                times -= 1
                
                conn, addr = soc.accept()
                print(f"Connecting with {addr}")
                print("Receiving...")
                request = conn.recv(1024)
                print(f"{'-'*10}\nContent {request}\n{'-'*10}")

                if args_logic != None:
                    return_logic = logic(str(request), **args_logic)
                else:
                    return_logic = logic(str(request))
                
                if type(page) is str:
                    response = page
                else:
                    if args_logic != None:
                        response = page(**args_page)
                    else:
                        response = page()
                conn.send("HTTP/1.1 200 OK\n")
                conn.send("Content-Type: text/html\n")
                conn.send("Connection: close\n\n")
                conn.sendall(response)
                
                conn.close()
        else:
            print("Not connect in wifi!")
            return False
        
        return return_logic
