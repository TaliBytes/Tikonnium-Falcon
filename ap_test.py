from machine import Pin, PWM, I2C
import network, socket
import ssd1306 as disp
import time



# I2C Disp config
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = disp.SSD1306_I2C(128,64,i2c)

# splash screen
if oled is not None:
  oled.fill(0)
  oled.text('Tikonnium',28,16)
  oled.text('Falcon',40,24)
  oled.show()
else:
  print('OLED display was not found')



# configure access point for tiko
ap = network.WLAN(network.AP_IF)
ap.active(False)  # clean up
time.sleep(1)
ap.config(essid='tiko', password='tkfalcon1', channel=6) 
ap.active(True)

# wait until active
counter = 1 # start at 1 since it sleeps for 1 second during cleanup
while not ap.active():
  print('Configuring access point...')
  counter += 1
  time.sleep(1)
print("Access point configured!")

ip = ap.ifconfig()[0]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)



# guarantee splash screen shows for at least 5 seconds
time.sleep(min(5-counter,0))  

# stats
if oled is not None:
  oled.fill(0)
  oled.text('host: tiko', 0, 8)
  oled.text('p: tkfalcon1', 0, 16)
  oled.text(f'site', 0, 32)
  oled.text(str(ip), 8, 40)
  oled.show()



while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  response = 'hello'
  conn.send(response)
  conn.close()
