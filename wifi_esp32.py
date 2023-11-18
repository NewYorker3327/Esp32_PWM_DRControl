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
    def __init__(self, login, password):
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
        self.ifconfig = ("192.168.0.100", "255.255.255.0", "192.168.10.1", "8.8.8.8")
        self.net.active(False)
        self.ip = None

    def connect(self):
        """
        Try connecting to wifi
        """
        print("Connecting...")
        if not self.net.isconnected():
            self.net.active(True)
            self.net.ifconfig(self.ifconfig)
            for login_wifi in self.login:
                for password_wifi in self.password:
                    print(f"Try: {login_wifi} {password_wifi}")
                    self.net.connect(login_wifi, password_wifi)
                    sleep(0.1)
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

    def open_web_page(self, page, logic, times = 1, args_page:dict = None, args_logic:dict = None):
        """
        Open a web page using a socket and read the result after a certain time
        """
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
                soc.listen(5) #Max of listen
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
                if gc.mem_free() < 102000:
                    print("Clearing memory...")
                    gc.collect()
                
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
            
if __name__ == "__main__":
    def web_page(t):
        html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong> """ + str(t) + """ /strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
        return html
    
    def logic(text):
        if text.find("led=on") > -1:
            print(">>> LED IS 1")
        if text.find("led=off") > -1:
            print(">>> LED IS 0")
    
    wifi = Wifi("login", "senha")
    wifi.connect()
    deu = wifi.open_web_page(web_page, logic, args_page = {"t":"teste"})
