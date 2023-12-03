"""
Class to ws2812b
"""

import machine
from neopixel import NeoPixel
from random import random
from time import sleep

class Leds:
    def __init__(self, door:int, width:int, bpp:int = 3):
        """
        • door: Microcontroller port
        • width: Number of LEDs on the strip
        
        If the LED is RGB, bpp is 3
        """
        self.door = door
        self.leds = NeoPixel(machine.Pin(door), width, bpp = bpp)
        self.width = width
        self.numbers = None

    def draw_in(self, i:int, color:list):
        """
        Draw individually
        """
        self.leds[i] = color
        self.leds.write()

    def gradient(self, color_max:list, inverse:bool = False):
        """
        Draw gradient on the entire LED strip
        """
        temp = []
        for i in range(self.width):
            temp.append([int(color_max[0]/(self.width-1)*i),
                         int(color_max[1]/(self.width-1)*i),
                         int(color_max[2]/(self.width-1)*i)])

        if inverse:
            temp = temp[::-1]

        for i in range(self.width):
            self.leds[i] = temp
        self.leds.write()

    def dell_all(self, animation:int = 0):
        """
        turn off all the LEDs
        """
        if animation == 0:
            for i in range(self.width):
                self.leds[i] = [0, 0, 0]
            self.leds.write()
            
        elif animation == 1: #smooth
            dif = 3
            while True:
                for i in range(self.width):
                    self.leds[i] = [max(self.leds[i][0] - dif, 0), max(self.leds[i][1] - dif, 0), max(self.leds[i][2] - dif, 0)]

                self.leds.write()
                    
                if sum(list(map(sum,seld.leds))) == 0:
                    break

        elif animation == 2: #random
            value = 0.01
            while True:
                for i in range(self.width):
                    if sum(self.leds[i]) != 0:
                        if random() < 0.1:
                            self.leds[i] = [0, 0, 0]
                self.leds.write()

                if sum(list(map(sum,self.leds))) == 0:
                    break

    def return_colors(self):
        """
        returns the list of LED colors
        """
        temp = [self.leds[i] for i in range(self.width)]
        return temp

    def animation(self, animation:str, value = None):
        if animation == "load" and value != None:
            for i in range(value):
                self.leds[i] =  [100, 100, max(int(i * 255/self.width), 255)]
            self.leds.write()

        elif animation == "wait":
            if value == None:
                value = 0.05
            if type(value) == list:
                for i in range(self.width):
                    if self.leds[i] != [0, 0, 0]:
                        temp = self.leds[i]
                        self.leds[i] = value
                        self.leds.write()
                        self.leds[i] = temp
                    sleep(0.05)
            else:
                for i in range(self.width):
                    if self.leds[i] != [0, 0, 0]:
                        try:
                            if i > 0:
                                temp = self.leds[i - 1]
                                self.leds[i - 1] = [min(int(self.leds[i][0] * 0.7), 255), min(int(self.leds[i][1] * 1.3), 255), min(int(self.leds[i][2]  * 1.3), 255)]
                                self.leds[i - 1] = temp
                        except:
                            pass
                        try:
                            if i < width - 1:
                                temp = self.leds[i + 1]
                                self.leds[i + 1] = [min(int(self.leds[i][0] * 0.7), 255), min(int(self.leds[i][1] * 1.3), 255), min(int(self.leds[i][2]  * 1.3), 255)]
                                self.leds[i + 1] = temp
                        except:
                            pass
                        temp = self.leds[i]
                        self.leds[i] = [min(int(self.leds[i][0] * 0.3), 255), min(int(self.leds[i][1] * 1.7), 255), min(int(self.leds[i][2]  * 1.7), 255)]
                        self.leds.write()
                        self.leds[i] = temp
                    sleep(value)
        
    def test(self):
        """
        test the LED strip here
        """
        for i in range(10):
            color_ = color[int(len(color.keys())*random())]
            for i in range(self.width):
                for j in range(0, i):
                    if self.leds[j] != [0, 0, 0]:
                        self.leds[j] = [max(int(self.leds[i][0] * 0.9), 0), max(int(self.leds[i][1] * 0.9), 0), max(int(self.leds[i][2] * 0.9), 0)]
                self.leds[i] = color_
                self.leds.write()
                sleep(0.05)


            for k in range(10):
                for i in range(self.width):
                    if self.leds[j] != [0, 0, 0]:
                        self.leds[j] = [max(int(self.leds[i][0] * 0.9), 0), max(int(self.leds[i][1] * 0.9), 0), max(int(self.leds[i][2] * 0.9), 0)]
                self.leds.write()
                sleep(0.025)

        if self.numbers != None:
            for i in self.numbers:
                k = ""
                for k in range(int(self.width/len(self.numbers[i]))):
                    k += i
                self.add_numbers(values = k)
                self.leds.write()
            
        for i in range(self.width):
            temp.append([int(random()*256), int(random()*256), int(random()*256)])
            self.leds[i] = temp[-1]
        self.leds.write()

    def add_numbers(self, design_list:dict = False, color:list = [255, 255, 255], values:str = False, animation:int = 0):
        """
        It helps to create displays, pass the list of characters in a list and pass a string of what should be written.
        """
        if self.numbers == None:
            self.numbers = design_list
        else:
            design_list = self.numbers
            
        for i in design_list.keys():
            if self.width % design_list[i] != 0:
                print(f"The value {i} in the dictionary is not in the correct dimension.")

        if values != False:
            if len(values)*design_list[design_list.keys()[0]] != self.width:
                print(f"Pass a size string {self.width/design_list[design_list.keys()[0]]}.")

            temp = []
            for i in values:
                temp.extend(design_list[i])

            for i in range(len(temp)):
                if temp[i] == 1:
                    temp[i] = color

            if animation == 0:
                for i in range(self.width):
                    self.leds[i] = temp[i]
                self.leds.write()
            
            elif animation == 1: #smooth
                dif = 3
                while True:
                    for i in range(self.width):
                        self.leds[i][0] = int(temp[i][0]*0.05 + self.leds[i][0]*0.95 + 1)
                        self.leds[i][1] = int(temp[i][1]*0.05 + self.leds[i][1]*0.95 + 1)
                        self.leds[i][2] = int(temp[i][2]*0.05 + self.leds[i][2]*0.95 + 1)

                    self.leds.write()
                        
                    if sum(list(map(sum,a))) == 0:
                        break

            elif animation == 2: #random
                value = 0.01
                while True:
                    for i in range(self.width):
                        if sum(self.leds[i]) != 0:
                            if random() < 0.1:
                                self.leds[i] = temp[i]
                    self.leds.write()
                        
                    if sum(list(map(sum,a))) == 0:
                        break

class Matrix_Leds:
    """
    If you assemble a matrix of LEDs from top to bottom like this:
    >>>>>>>>>>>>>>v
    v<<<<<<<<<<<<<<
    >>>>>>>>>>>>>>v
    v<<<<<<<<<<<<<<
    """
    def __init__(self, door:int, width:int, lines:int, bpp:int = 3):
        if width % columns != 0:
            print("The tape width dimensions and number of lines do not match.")
            return None
        
        self.door = door
        self.leds = NeoPixel(machine.Pin(door), width, bpp = bpp)
        self.width = width
        self.columns = lines
        self.strings = None
        self.lines = None

    def strings(self, strings:dict):
        """
        Defines the strings
        """
        n = (len(strings[strings.keys()[0]]), len(strings[strings.keys()[0]])[0])
        for i in strings.keys():
            if n != (len(i), len(i[0])):
                print(f"String {i} has dimension {len(i), len(i[0])} and should have dimension {n}.")
                return None
        self.strings = strings
        self.lines = n[0]

    def write(self, text:str, color:list = [255, 255, 255]):
        """
        Write on the display
        """
        matrix = [[[0,0,0] for i in range(self.width/self.lines)] for j in range(self.lines)]

        if type(color[0]) != list and type(color[0]) != tuple:
            color = [color for i in range(len(text))]            
        
        for character in text:
            c = self.strings[character]
            k = 0
            for i in range(len(c)):
                for j in range(len(c[0])):
                    if c[i][j] == 1:
                        matrix[i][k * len(c[0] + 1)] = color[k]
                    k += 1

        for i in range(len(matrix)):
            if i % 2 == 0:
                matrix[i] = matrix[i][::-1]

        final_matrix = []
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                final_matrix.append(matrix[i][j])

        for i in range(self.width):
            self.leds[i] = final_matrix[i]

        self.leds.write()

color = {"blue": [0,0,255],
         "lightblue": [173,216,230],
         "darkclue": [0,0,139],
         "cyam": [0,255,255],
         "aquamarine": [127,255,212],
         "teal": [0,128,128],
         "green": [0,128,0],
         "lightgreen": [144,238,144],
         "darkgreen": [0,100,0],
         "gold": [218,165,32],
         "sienna": [160,82,45],
         "tan": [210,180,140],
         "blueviolet": [138,43,226],
         "indigo": [75,0,130],
         "mediumpurple": [147,112,219],
         "purple": [128,0,128],
         "darkmagenta": [139,0,139],
         "hotpink": [255,105,180],
         "red": [255,0,0],
         "darkred": [139,0,0],
         "salmon": [250,150,114],
         "darkorange": [255,140,0],
         "orange": [255,165,0],
         "yellow": [255,255,0],
         "ice": [240,248,255],
         "ghost": [248,248,255],
         "whitesmoke": [245,245,245],
         "beige": [245,245,220],
         "old": [253,245,230],
         "ivory": [255,255,224],
         "beige": [245,245,220],
         "bisque": [255,228,196],
         "lightgolden": [250,250,210],
         "lavender": [230,230,250],
         "thistle": [216,191,216],
         "lightcyan": [224,255,255],
         "powderblue": [176,224,230],
         "gray": [128,128,128],
         "silver": [192,192,192],
         "dimgray": [105,105,105],
         "fire": [255, 40, 0]}
