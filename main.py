# M5Stack Acess Point Webserver view temperature, pressure and humidity
# collecting data from sensor to files on SD card
# used JS for view graph in browser
# hardware: M5Stack FIRE + Temperature Humidity Pressure Sensor
# https://m5stack.com/collections/m5-core/products/fire-iot-development-kit
# 
#
from m5stack import *
from m5ui import *

import uos

import units
import random
import machine
import utime
import math

import network
import uselect
try:
    import usocket as socket
except:
    import socket
    
### GLOBAl VARIABLES ###########################################
typeView = 0
previostimeM = -1
previostimeH = -1
previostimeD = -1 
previostimeMn = -1
numHour = 11
numDay = 19
numMonth = 1
### END GLOBAl VARIABLES #######################################

### Setup date and time for RTC ################################
def setupDateTime():
  setup = False
  pointer = 0
  value = 0

  M5TextBox(20, 20, "Current date and time", lcd.FONT_Comic, 0x00FFFF, rotate=0)
  M5TextBox(20, 80, "Time : ", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  M5TextBox(20, 120, "Date : ", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  
  M5TextBox(85, 200, " <", lcd.FONT_Tooney, 0xFFFF00, rotate=90)
  M5TextBox(115, 200, "save", lcd.FONT_Tooney, 0xFFFF00, rotate=0)
  M5TextBox(245, 200, ">", lcd.FONT_Tooney, 0xFFFF00, rotate=0)
  
  labelTable1 = M5TextBox(100, 80, "Text", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  M5TextBox(135, 80, ":", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  labelTable2 = M5TextBox(150, 80, "Text", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  M5TextBox(190, 80, ":", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  labelTable3 = M5TextBox(205, 80, "Text", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  
  labelTable4 = M5TextBox(100, 120, "Text", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  M5TextBox(165, 120, ".", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  labelTable5 = M5TextBox(175, 120, "Text", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  M5TextBox(205, 120, ".", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  labelTable6 = M5TextBox(225, 120, "Text", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
  
  lcd.font(lcd.FONT_Comic)  
  
  while not setup:
    hour = utime.localtime()[3]
    minute = utime.localtime()[4]
    second = utime.localtime()[5]
    date = utime.localtime()[2]
    month = utime.localtime()[1]
    year = utime.localtime()[0]
    
    if pointer == 0:
      table = [0, hour, minute, second, year, month, date]
    else:
      table[pointer] = value
    
    color = 0xFF0000 if pointer == 1 else 0xFFFFFF  
    labelTable1.setColor(color)
    color = 0xFF0000 if pointer == 2 else 0xFFFFFF
    labelTable2.setColor(color)
    color = 0xFF0000 if pointer == 3 else 0xFFFFFF 
    labelTable3.setColor(color)
    color = 0xFF0000 if pointer == 4 else 0xFFFFFF 
    labelTable4.setColor(color)
    color = 0xFF0000 if pointer == 5 else 0xFFFFFF 
    labelTable5.setColor(color)
    color = 0xFF0000 if pointer == 6 else 0xFFFFFF 
    labelTable6.setColor(color)
    
    if len(str(table[1])) < 2:
      labelTable1.setText("0" + str(table[1]))
    else:
      labelTable1.setText(str(table[1]))
    
    if len(str(table[2])) < 2:
      labelTable2.setText("0" + str(table[2]))
    else:
      labelTable2.setText(str(table[2]))

    if len(str(table[3])) < 2:
      labelTable3.setText("0" + str(table[3]))
    else:
      labelTable3.setText(str(table[3]))

    if len(str(table[5])) < 2:
      labelTable5.setText("0" + str(table[5]))
    else:
      labelTable5.setText(str(table[5]))

    if len(str(table[6])) < 2:
      labelTable6.setText("0" + str(table[6]))
    else:
      labelTable6.setText(str(table[6]))
      
    labelTable4.setText(str(table[4]))

    M5TextBox(135, 80, ":", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
    M5TextBox(190, 80, ":", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
    M5TextBox(165, 120, ".", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
    M5TextBox(205, 120, ".", lcd.FONT_Comic, 0xFFFFFF, rotate=0)
    
    wait(0.2)
    
    if buttonC.wasPressed():
      pointer = pointer + 1
      if pointer > 6:
        pointer = 1
        
      value = table[pointer]

    if buttonA.wasPressed():
      value = value + 1
      if pointer == 1:
        if value > 23:
          value = 0
      if pointer == 2 or pointer == 3:
        if value > 59:
          value = 0  
      if pointer == 4:
        if value > 2025:
          value = 2000
        if value < 2000:
          value = 2019 
      if pointer == 5:
        if value > 12:
          value = 1
      if pointer == 6:
        if value > 31:
          value = 1
          
    if buttonB.wasPressed():
      rtc.init((table[4], table[5], table[6], table[1]+1, table[2], table[3], 0, 0))
      setup = True
        
    wait(0.2)

    
### Write data to the files ####################################
def writeFile():
    global previostimeM
    global previostimeH
    global previostimeD
    global previostimeMn
    
     ### WRITE TO FILE FOR HOUR
    if math.fabs(utime.localtime()[4] - previostimeM) >= 1:
      previostimeM = utime.localtime()[4]
      
      if math.fabs(utime.localtime()[3] - previostimeH) >= 1:
        previostimeH = utime.localtime()[3]
        ### create table file
        try:
          os.mkdir('/sd/'+str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]))
          name = '/sd/'+str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]) + '/' + str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]) + '_' + str(utime.localtime()[3]) + '.csv'
          file = open(name, 'a+')
          wrstring = 'date' + ';' + 'time' + ';' + 'temperature' + ';' + 'pressure' + ';' + 'humidity' + '\r\n'
          file.write(wrstring)
          file.close()  
        except:
          wait(0.001)

      name = '/sd/'+str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2])+ '/' + str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]) + '_' + str(utime.localtime()[3]) + '.csv'  
      file = open(name, 'a')

      year = str(utime.localtime()[0])
      month = str(utime.localtime()[1])
      day = str(utime.localtime()[2])
      hour = str(utime.localtime()[3])
      minute = str(utime.localtime()[4])
      second = str(utime.localtime()[5])
      
      # temperature, pressure and humidity
      temperature =str(env0.temperature())
      pressure = str(env0.pressure())
      humidity = str(env0.humidity())
      wrstring = year + '.' + month + '.' + day + ';' + hour + ':' + minute + ':' + second + ';' + temperature + ';' + pressure + ';' + humidity + '\r\n'
      file.write(wrstring)
      file.close()
      
      ### WRITE TO FILE FOR DAY
      if math.fabs(utime.localtime()[4] - previostimeD) >= 5:
        previostimeD = utime.localtime()[4]
        ### create table file
        try:
          uos.stat('/sd/'+str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]) + '/day_' + str(utime.localtime()[2]) + '.csv')
        except:
          name = '/sd/'+str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]) + '/day_' + str(utime.localtime()[2]) + '.csv'
          file = open(name, 'a+')
          wrstring = 'date' + ';' + 'time' + ';' + 'temperature' + ';' + 'pressure' + ';' + 'humidity' + '\r\n'
          file.write(wrstring)
          file.close() 

        name = '/sd/'+str(utime.localtime()[0]) + '_' + str(utime.localtime()[1]) + '_' + str(utime.localtime()[2]) + '/day_' + str(utime.localtime()[2]) + '.csv'
        file = open(name, 'a')
        wrstring = year + '.' + month + '.' + day + ';' + hour + ':' + minute + ':' + second + ';' + temperature + ';' + pressure + ';' + humidity + '\r\n'
        file.write(wrstring)
        file.close()
        
      ### WRITE TO FILE FOR MONTH  
      if math.fabs(utime.localtime()[4] - previostimeMn) >= 20:
        previostimeMn = utime.localtime()[4]
        ### create table file
        try:
          uos.stat('/sd/month_' + str(utime.localtime()[1]) + '.csv')
        except:
          name = '/sd/month_' + str(utime.localtime()[1]) + '.csv'
          file = open(name, 'a+')
          wrstring = 'date' + ';' + 'time' + ';' + 'temperature' + ';' + 'pressure' + ';' + 'humidity' + '\r\n'
          file.write(wrstring)
          file.close()  
          
        name = '/sd/month_' + str(utime.localtime()[1]) + '.csv'
        file = open(name, 'a')
        wrstring = year + '.' + month + '.' + day + ';' + hour + ':' + minute + ':' + second + ';' + temperature + ';' + pressure + ';' + humidity + '\r\n'
        file.write(wrstring)
        file.close()      


### Processing messages and response ###########################
def web():
  global numHour
  global numDay
  global numMonth
  global typeView

  request = ''
  file = ''
  nextPreviousDay = 0
  nextPreviousMonth = 0

  poller = uselect.poll()
  poller.register(s, uselect.POLLIN)
  res = poller.poll(100)
  if res:
    conn, addr = s.accept()
    request = conn.recv(1024)
    request = str(request)
  else:
    request = ''
  
#### FOR HOURS ##############################################  
  # in case when view only hours
  if typeView == 0:  
    # for download next page   
    if request[0:100].find("next") != -1:
      expect = 0
      while str(file) == '':
        numHour = numHour + 1
        
        if numHour > 23:
          numHour = 0
        
        name ='/sd/'+str(utime.localtime()[0]) + '_' + str(numMonth) + '_' + str(numDay)+ '/' + '2019_%s_%s_%s.csv' % (str(numMonth),str(numDay),str(numHour)) 
        try:
          file = open(name, 'r')
          file.close()
        except:
          wait(0.001)
  
    # for download previous page  
    if request[0:100].find("previous") != -1:
      expect = 0
      while str(file) == '':
        numHour = numHour - 1
        
        if numHour < 0:
          numHour = 23
          
        name ='/sd/2019_12_19_%s.csv' % str(numHour)   
        try:
          file = open(name, 'r')
          file.close()
        except:
          wait(0.001)

  # for view hour
  if request[0:100].find("hour") != -1:
    typeView = 0
    numHour = utime.localtime()[3]


#### FOR DAYS ###############################################        
  # in case when view days
  if typeView == 1:  
    # for download next page   
    if request[0:100].find("next") != -1:
      nextPreviousDay = 1
      numDay = numDay + 1
      if numDay > 31:
        numDay = 1
  
    # for download previous page  
    if request[0:100].find("previous") != -1:
      nextPreviousDay = 1
      numDay = numDay - 1
      if numDay < 1:
          numDay = 31

  # for view day
  if request[0:100].find("day") != -1 or nextPreviousDay == 1:
    typeView = 1
    numDay = utime.localtime()[2]

#### FOR MONTH ##############################################    
  # in case when view days
  if typeView == 2:  
    # for download next page   
    if request[0:100].find("next") != -1:
      nextPreviousMonth = 1
      numMonth = numMonth + 1
      if numMonth > 12:
        numMonth = 1
  
    # for download previous page  
    if request[0:100].find("previous") != -1:
      nextPreviousMonth = 1
      numMonth = numMonth - 1
      if numMonth < 1:
          numMonth = 12
          
  # for view month
  if request[0:100].find("month") != -1 or nextPreviousMonth == 1:
    typeView = 2
    numMonth = utime.localtime()[1]
  
#### SEND to BROWSER ########################################
  # for view response in browser
  if request != '':
    #lcd.clear()
    #lcd.print('request = %s' % str(request),0,80,0xffffff)

    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    
    ### first part of HTML page
    file = open('/sd/part1.html', 'r')
    for fileText in file:
      conn.sendall(fileText)
    file.close()
    
    # in case when view only hours
    if typeView == 0:
      ### data for view
      name ='/sd/'+str(utime.localtime()[0]) + '_' + str(numMonth) + '_' + str(numDay)+ '/' + '2019_%s_%s_%s.csv' % (str(numMonth),str(numDay),str(numHour)) 
      file = open(name, 'r')
      i = 0
      for fileText in file:
        if i > 0:
          fileText = fileText.replace('\r\n', '/')
          conn.sendall(fileText)
        i = i + 1
        
      file.close()
      
      ### second part of HTML page
      file = open('/sd/part2.html', 'r')
      for fileText in file:
        conn.sendall(fileText)
      file.close()   
      
    # in case when view only day
    if typeView == 1:
      ### data for view
      name ='/sd/'+str(utime.localtime()[0]) + '_' + str(numMonth) + '_' + str(numDay)+ '/' + 'day_%s.csv' % str(numDay) 
      file = open(name, 'r')
      i = 0
      for fileText in file:
        if i > 0:
          fileText = fileText.replace('\r\n', '/')
          conn.sendall(fileText)
        i = i + 1
        
      file.close()
      
      ### second part of HTML page
      file = open('/sd/part2.html', 'r')
      for fileText in file:
        conn.sendall(fileText)
      file.close()
      
    # in case when view only month
    if typeView == 2:
      ### data for view
      name ='/sd/month_%s.csv' % str(numMonth) 
      file = open(name, 'r')
      i = 0
      for fileText in file:
        if i > 0:
          fileText = fileText.replace('\r\n', '/')
          conn.sendall(fileText)
        i = i + 1
        
      file.close()

      ### second part of HTML page
      file = open('/sd/part3.html', 'r')
      for fileText in file:
        conn.sendall(fileText)
      file.close()
    
    request = ''

    conn.close()

############# MAIN #########################################################################
clear_bg(0x000000)
uos.sdconfig(uos.SDMODE_SPI,clk=18,mosi=23,miso=19,cs =4)
uos.mountsd()
rtc = machine.RTC()
setupDateTime()

numHour = utime.localtime()[3]
numDay = utime.localtime()[2]
numMonth = utime.localtime()[1]

### Acess Point Webserver ###################################################################
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='M5Stack')
ap.config(authmode=3, password='123456789')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('192.168.4.1',80))
s.listen(1)
############################################################################################

### Webserver ##############################################################################
#station = network.WLAN(network.STA_IF)
#station.active(True)
#station.connect('Redmi', '12345678')
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(('192.168.4.1',80))
#s.listen(1)
############################################################################################

while True:
    # print main screen with sky
    clear_bg(0x000000)

    env0 = units.ENV(units.PORTA)
  
    circle4 = M5Circle(40, 40, 20, 0xff9900, 0x000000)
    circle2 = M5Circle(107, 68, 20, 0xFFFFFF, 0xFFFFFF)
    circle0 = M5Circle(136, 67, 32, 0xFFFFFF, 0xFFFFFF)
    circle9 = M5Circle(115, 79, 20, 0xFFFFFF, 0xFFFFFF)
    circle3 = M5Circle(86, 79, 20, 0xFFFFFF, 0xFFFFFF)
    circle12 = M5Circle(163, 79, 20, 0xFFFFFF, 0xFFFFFF)
  
    label0 = M5TextBox(50, 144, "Temperature:", lcd.FONT_Minya, 0xF00FFF, rotate=0)
    label1 = M5TextBox(50, 174, "Pressure:", lcd.FONT_Minya, 0xF00FFF, rotate=0)
    label2 = M5TextBox(50, 204, "Humidity:", lcd.FONT_Minya, 0xF00FFF, rotate=0)
    label3 = M5TextBox(210, 144, "Text", lcd.FONT_Minya, 0xF00FFF, rotate=0)
    label4 = M5TextBox(210, 174, "Text", lcd.FONT_Minya, 0xF00FFF, rotate=0)
    label5 = M5TextBox(210, 204, "Text", lcd.FONT_Minya, 0xF00FFF, rotate=0)
    
    M5TextBox(180, 10, "Time : ", lcd.FONT_Default, 0xF00FFF, rotate=0)
    M5TextBox(180, 30, "Date : ", lcd.FONT_Default, 0xF00FFF, rotate=0)
    label7 = M5TextBox(230, 10, "Text", lcd.FONT_Default, 0xF00FFF, rotate=0)
    label8 = M5TextBox(230, 30, "Text", lcd.FONT_Default, 0xF00FFF, rotate=0)
    
    rect3 = M5Rect(90, 102, 1, 2, 0xFFFFFF, 0xFFFFFF)
    rect4 = M5Rect(111, 102, 1, 2, 0xFFFFFF, 0xFFFFFF)
    rect5 = M5Rect(134, 102, 1, 2, 0xFFFFFF, 0xFFFFFF)
    rect6 = M5Rect(158, 102, 1, 2, 0xFFFFFF, 0xFFFFFF)

    previostimeS = -5  
    random2 = None
    
    # printing data on main screen refreshing data from sensor every 5 seconds
    while True:
        if math.fabs(utime.localtime()[5] - previostimeS) >= 5:
          label5.setText(str(env0.humidity()))
          label3.setText(str(env0.temperature()))
          label4.setText(str(env0.pressure()))
          previostimeS = utime.localtime()[5]
          
        label7.setText(str(utime.localtime()[3]) + ":" + str(utime.localtime()[4]) + ":" + str(utime.localtime()[5]))
        label8.setText(str(utime.localtime()[0]) + "." + str(utime.localtime()[1]) + "." + str(utime.localtime()[2]))
        
        if (env0.humidity()) >= 50:
            circle4.setBgColor(0x000000)
            rect3.setBorderColor(0x3333ff)
            rect4.setBorderColor(0x3333ff)
            rect5.setBorderColor(0x3333ff)
            rect6.setBorderColor(0x3333ff)
            random2 = random.randint(2, 30)
            rect3.setSize(height=random2)
            random2 = random.randint(2, 30)
            rect4.setSize(height=random2)
            random2 = random.randint(2, 30)
            rect5.setSize(height=random2)
            random2 = random.randint(2, 30)
            rect6.setSize(height=random2)
        else:
            rect3.setBorderColor(0x000000)
            rect4.setBorderColor(0x000000)
            rect5.setBorderColor(0x000000)
            rect6.setBorderColor(0x000000)
            circle4.setBgColor(0xff6600)

        wait(0.001)
        writeFile()
        web()
        