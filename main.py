#networking
#import datetime
import network, socket

#micro-controller
import asyncio
from machine import Pin, PWM, I2C
import ssd1306 as disp
import time
from machine import Pin, PWM, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd


#GLOBAL VARIABLES
# wifi settings
ssidName:str|None = None
ssidPwd :str|None = None
ip:str|None = None
port:int = 9000
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

oled = None                   # oled I2C display

request_headers:dict = {}     # client's request headers
response_headers:dict = {}    # server's response headers
response_content:str = ''     # content returned by server
sockets:list = []             # hosts/ports to bind to  (except Tiko only gets one)





# IMPORT CONFIGURATION ... 
def getConfig()->None:
  global ssidName, ssidPwd, oled

  # wifi config
  try:
    with open('config.config', 'r') as config:

      for line in config:
        line:str = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
          setting, value = line.split('=', 1)
          setting = setting.strip()
          value = value.strip()

          if setting == "ssidName": ssidName = value
          if setting == "ssidPwd": ssidPwd = value
  except Exception as err:
    print('Fatal Error: config.config error ... ' + str(err))

  # I2C Disp config
  i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
  oled = disp.SSD1306_I2C(128,64,i2c)






# Connect to the hotspot
def connectToHotspot()->None:
  global ssidName, ssidPwd, wlan, ip

  if ssidName != None and ssidPwd != None:
    s:int=0 #number of secs attempting connection
    timeout:int=10
    wlan.connect(ssidName, ssidPwd)

    while not wlan.isconnected() and s <= timeout:
      print(f"Connecting to {ssidName}... {s}s")
      s+=1
      time.sleep(1)

    if wlan.isconnected():
      print(f"Connected to {ssidName}!, Config:, {wlan.ifconfig()}")
      ip = wlan.ifconfig()[0]
    else:
      print(f"Could not connect to. Check credentials and signal strength.")
  
  else:
    print('Missing ssidName or ssidPwd')





# Listen on sockets
def setupSockets()->None:
  """Configure socket to listen on"""
  global sockets, ip, port

  aSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sockets.append(aSocket)

  # bind socket to port
  try:
    aSocket.bind((ip, port))
    aSocket.listen(5) # max connections
    print(f"Configured socket binding for {ip}:{port}")
  except Exception as err:
    print(f"Couldn't configure socket binding for {ip}:{port} ... Error: {str(err)}")
    aSocket.close() # close on err
    return None

  aSocket.close() # close when done





def getContent()->str:
  """Returns HTML based on request headers"""
  global request_headers
  content:str = ''

  path = request_headers['path']
  if path in ['', '/', '/home']:
    with open('home.html', 'r') as homePage:
      for line in homePage:
        content += str(line)
  else:
    content = f"not-home, is {path}"
  
  return(content)





def parseRequest(request:str)->None:
  global request_headers
  request_headers = {}

  request = str(request)
  lines:list = request.split("\r\n")

  rqstLine:str = lines[0]
  method, path, protocol = rqstLine.split(' ')
  request_headers['method'] = method
  request_headers['path'] = path
  request_headers['protocol'] = protocol
  #request_headers['date'] = datetime.datetime.now().strftime("%a, $d %b %Y %H:%M:00 MST")

  for line in lines[1:]:
    if line == "":
      break
      
    key, value = line.split(":", 1)
    request_headers[key.strip()] = value.strip()





def constructResponse()->bytes:
  """Setup initial headers, get desired response, send it"""
  global response_headers
  global response_content

  response_content = getContent()

  response_headers.setdefault('statusCode', 200)
  response_headers.setdefault('statusMessage', 'OK')
  response_headers.setdefault('contentType', 'text/html; charset="UTF-8"')
  response_headers.setdefault('connection', 'close')

  # construct response header
  headers =  f"HTTP/1.1 {response_headers['statusCode']} {response_headers['statusMessage']}\r\n"
  headers += f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
  headers += f"Connection: {response_headers['connection']}\r\n"  
  headers += f"Content-Type: {response_headers['contentType']}\r\n"
  #headers += f"Date: {datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:00 MST')}\r\n"

  headers += f"\r\n"  #marks end of headers, start of body

  headersEncoded = headers.encode('utf-8')
  contentEncoded = response_content.encode('utf-8')

  response = headersEncoded + contentEncoded
  return(response)





async def handleRequest(reader, writer)->None:
  """Handle a clietn request"""
  request = await reader.read(1024)
  clientAddr = writer.get_extra_info('peername')

  if len(request) > 0:
    parseRequest(request.decode('utf-8'))
    print(f"\nconn with {clientAddr}: requested {request_headers['path']}")

    response = constructResponse()
    writer.write(response)
    print(f"conn withh {clientAddr}: sent response")
    await writer.drain()  # ensures actual sending of response

  print(f"conn with {clientAddr}: closed.")
  writer.close()





# 16 MotorR forward
# 17 MotorR backward
# 18 motorL forward
# 19 MotorL backward
# PMW range for each is 0-65535
pins = [16,17,18,19]
pwms = {p: PWM(Pin(p)) for p in pins}
pwmDuties = {p: 0 for p in pins}

# set start point for each pwm pin
#print(f"Turned off each motor PWM pin and set frequency to 25MHz")
for pwm in pwms.values():
  pwm.duty_u16(0)
  pwm.freq(25000)





#e.g 65535 to 1 (return range = -1 to 1)
def PWMToDecimal(pwm:int)->float:
  print('PWMToDecimal hasn\'t been tested yet')
  return (min(max(round((pwm/65535),2),-1),1))





#e.g 1 to 65535 (return range = -65535 to 65535)
def decimalToPWM(decimal:float)->int:
  return(min( max( int(decimal*65535), -65535), 65535))





# transition the duty cycle of a PWM pin
async def transitionPMW(pin, newDuty:int=0, seconds:float=1, steps:int=1000)->None:
  global pwms, pwmDuties

  stepTime = seconds/steps # how long each step will take
  curDuty = pwmDuties[pin] # current duty of on the pin
  step = abs((curDuty - newDuty) / steps) # how much the duty needs to change per iteration
  dirMultiplier = 1 if newDuty > curDuty else -1  #1 = stepping up to newDuty, -1 stepping down to newDuty

  if curDuty != newDuty:
    #print(f"Pin {pin} transitioning to {newDuty} from {curDuty} over {seconds}s ({stepTime}s/step for {steps} steps)")
    for duty in range (curDuty, newDuty, int(step)*dirMultiplier):
      pwms[pin].duty_u16(round(duty,0))
      pwmDuties[pin] = duty
      await asyncio.sleep(stepTime)

    # ensure new value is set
    pwms[pin].duty_u16(newDuty)
    pwmDuties[pin] = newDuty
    return None

  else: # old and new are equivalent
    #print(f"C. Pin {pin} old and new duties are equivalent ... no transition")
    return None





# set tiko to move forward
async def tikoForward()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 65535, .25)),
    asyncio.create_task(transitionPMW(17, 00000, .25)),
    asyncio.create_task(transitionPMW(18, 65535, .25)),
    asyncio.create_task(transitionPMW(19, 00000, .25)),
  ]
  await asyncio.gather(*tasks)





# set tiko to move backward
async def tikoReverse()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .25)),
    asyncio.create_task(transitionPMW(17, 65535, .25)),
    asyncio.create_task(transitionPMW(18, 00000, .25)),
    asyncio.create_task(transitionPMW(19, 65535, .25)),
  ]
  await asyncio.gather(*tasks)





# modify/set direction of Tiko's left motor only
# dir -1 thru 1 ... neg = backward, pos = forward
async def tikoSetLeft(dir:int=0)->None:
  pwmVal = decimalToPWM(dir)
  if pwmVal > 0:   
    # forward
    tasks = [
      asyncio.create_task(transitionPMW(18, pwmVal, .1)),
      asyncio.create_task(transitionPMW(19, 000000, .1)),
    ]
  elif pwmVal < 0: 
    # backward
    tasks = [
      asyncio.create_task(transitionPMW(18, 000000, .1)),
      asyncio.create_task(transitionPMW(19, pwmVal, .1)),
    ]
  else:   
    # stopped         
    tasks = [
      asyncio.create_task(transitionPMW(18, 0, .1)),
      asyncio.create_task(transitionPMW(19, 0, .1)),
    ]

  await asyncio.gather(*tasks)





# modify/set direction of Tiko's right motor only
# dir -1 thru 1 ... neg = backward, pos = forward
async def tikoSetRight(dir:int=0)->None:
  pwmVal = decimalToPWM(dir)
  if pwmVal > 0:   
    # forward
    tasks = [
      asyncio.create_task(transitionPMW(16, pwmVal, .1)),
      asyncio.create_task(transitionPMW(17, 000000, .1)),
    ]
  elif pwmVal < 0: 
    # backward
    tasks = [
      asyncio.create_task(transitionPMW(16, 000000, .1)),
      asyncio.create_task(transitionPMW(17, pwmVal, .1)),
    ]
  else:   
    # stopped         
    tasks = [
      asyncio.create_task(transitionPMW(16, 0, .1)),
      asyncio.create_task(transitionPMW(17, 0, .1)),
    ]

  await asyncio.gather(*tasks)






async def startServer()->None:
  """Initialize the server"""
  global ip, port
  #tasks:list = []
  server = None

  #indefinitely server on the socket
  if ip != '0.0.0.0' and port != '0':
    try:
      #continue to run upon receiving request
      server = await asyncio.start_server(handleRequest, ip, port)
      print(f"Success! Serving on {ip}:{port}")

      await server.wait_closed()  # run on server object itself
    except Exception as err:
      print(f"Error: Couldn't add {ip}:{port} to async listener. Server is not listening to this socket!: {str(err)}")
      if server:
        server.close()
        await server.wait_closed()
      pass
    finally:
      if server:
        print(f"Closing err'd server {ip}:{port}")
        server.close()
        await server.wait_closed()
        print(f"Closed err'd server")
  else:
    print(f"Skipped binding on {ip}:{port}")





if __name__ == "__main__":
  getConfig(); print('\n')
  while not wlan.isconnected():
    connectToHotspot(); print('\n')

  # ensure ip is correctly assigned
  if wlan.isconnected() and ip == None:
    ip = wlan.ifconfig()[0]

  if wlan.isconnected():
    setupSockets(); print('\n')

    if oled is not None:
      oled.fill(0)
      oled.text('Tikonnium',28,16)
      oled.text('Falcon',40,24)
      oled.show()
      time.sleep(10)
      oled.fill(0)
      oled.text('host: tiko', 0, 0)
      oled.text('pass: falcon', 0, 8)
      oled.text(f'site', 0, 24)
      oled.text(str(ip), 8, 32)
      oled.text('port: 9000', 0, 40)
      oled.show()
    else:
      print('OLED display was not found')
    asyncio.run(startServer())
