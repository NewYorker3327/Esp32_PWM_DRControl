"""
Connect to WiFi
"""

import socket
import network

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
        self.ifconfig = ("192.168.10.99", "255.255.255.0", "192.168.10.1", "8.8.8.8")

    def connect(self):
        """
        Try connecting to wifi
        """
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

    def is_connected(self):
        return self.net.isconnected()

    def open_web_page(self, target_ip = "192.168.1.1", target_port = 80, path = "/", timeout = 5):
        """
        Open a web page using a socket and read the result after a certain time
        """
        if not self.is_connected():
            print("Not connected to Wi-Fi.")
            return

        addr = socket.getaddrinfo(target_ip, target_port)[0][-1]

        with socket.socket() as s:
            s.connect(addr)
            s.sendall(b"GET " + path + b" HTTP/1.0\r\n\r\n")
            time.sleep(timeout)  # Wait for the server to respond

            response = s.recv(4096)
            print("Received response:")
            print(response.decode("utf-8"))
            
if __name__ == "__main__":
    wifi = Wifi(["net_1", "net_2"], ["pass_1", "pass_2", "pass_3"])
    wifi.connect()
    wifi.open_web_page()
