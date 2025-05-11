#networking
import network, socket

#micro-controller
import asyncio
import gc #garbage collector
from machine import Pin, PWM, I2C
import ssd1306 as disp
import ujson
import utime

# utime variables
weekdays_abbr = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


# GLOBAL VARIABLES
# wifi settings
ssidName:str|None = None
ssidPwd :str|None = None
ip:str|None = None
port = 80

# I2C Display Configuration
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = disp.SSD1306_I2C(128,64,i2c)

""" #16 MotorR forward ... #17 MotorR backward ... #18 motorL forward ... #19 MotorL backward """
# PMW range for each is 0-65535
pins = [16,17,18,19]
pwms = {p: PWM(Pin(p)) for p in pins}
pwmDuties = {p: 0 for p in pins}

# set start point for each pwm pin
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
    #print(f"Pin {pin} old and new duties are equivalent ... no transition")
    return None





# set tiko to full stop
async def tikoStop()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
  ]
  await asyncio.gather(*tasks)





# set tiko to move forward
async def tikoForward()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 65535, .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 65535, .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
  ]
  await asyncio.gather(*tasks)





# set tiko to move backward
async def tikoReverse()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, 65535, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, 65535, .1)),
  ]
  await asyncio.gather(*tasks)





# set tiko to turn 90deg left
async def tikoTurnLeft()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
  ]
  await asyncio.gather(*tasks)
  tasks = [
    asyncio.create_task(transitionPMW(16, decimalToPWM(.75), .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, decimalToPWM(.75), .1)),
  ]
  await asyncio.gather(*tasks)
  utime.sleep(.1839)
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
  ]
  await asyncio.gather(*tasks)





# set tiko to turn 90deg right
async def tikoTurnRight()->None:
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
  ]
  await asyncio.gather(*tasks)
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, decimalToPWM(.75), .1)),
    asyncio.create_task(transitionPMW(18, decimalToPWM(.75), .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
  ]
  await asyncio.gather(*tasks)
  utime.sleep(.1839)
  tasks = [
    asyncio.create_task(transitionPMW(16, 00000, .1)),
    asyncio.create_task(transitionPMW(17, 00000, .1)),
    asyncio.create_task(transitionPMW(18, 00000, .1)),
    asyncio.create_task(transitionPMW(19, 00000, .1)),
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





def getConfig()->None:
  """import data for access point configuration"""
  global ssidName, ssidPwd, port

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
          elif setting == "ssidPwd": ssidPwd = value
          elif setting == "port": port = int(value)
          else: print(f'Unknown setting... {setting} : {value}')
  except Exception as err:
    print('Fatal Error: config.config error ... ' + str(err))





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
      await server.wait_closed()

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





async def handleRequest(reader, writer)->None:
  """Entry point for handling a client request"""
  # placeholders
  request_headers = {}
  request_content = None
  response = None

  request = b''
  while b'\r\n\r\n' not in request:
    packet = await reader.read(1024)
    if not packet: break
    request += packet

  clientAddr = writer.get_extra_info('peername')
  part_header, _, part_body = request.partition(b'\r\n\r\n')
  headers = part_header.decode('utf-8')

  if len(headers) > 0:
    request_headers = parseHeaders(headers)     # parse headers into usable data
    print(f"\nconn with {clientAddr}: rqst {request_headers['path']}")

    if 'Content-Length' in request_headers: body_length = int(request_headers['Content-Length'])
    else: body_length = 0

  try:
    body = part_body
    emptyPackets = 0

    while len(body) < body_length:
      nextPacket = await reader.read(body_length - len(body))
      if not nextPacket:
        if emptyPackets == 10: break  # prevent waiting indefintely
        emptyPackets += 1
        await asyncio.sleep(0.05)
        print(f'Awaiting additional packet(s) attempt {emptyPackets+1}/10...')
        continue
      else: body += nextPacket

    if len(body) < body_length:
      print(f'Incomplete body received! Received {len(body)}/{body_length}')
      raise ValueError(f'Incomplete body received! Received {len(body)}/{body_length}')

    request_content = body.decode('utf-8')  # utf-8 because only text content is being transmitted from client
  except Exception as err:
    print(f'Could not process request body for {clientAddr} fetching {request_headers["path"]}! Error: {err}')


  if request_headers:
    response = await constructResponse(request_headers, request_content)    # respond to request by building response
    writer.write(response)
    print(f"conn with {clientAddr}: sent response")

  await writer.drain()  # ensures actual sending of response
  print(f"conn with {clientAddr}: closed")
  await writer.wait_closed()
  gc.collect()  # manage garbage





def parseHeaders(headers:str) -> dict:
  """parses a client request headers into usable data before using said data to create a response"""
  request_headers = {}

  headers = str(headers)
  lines:list = headers.split("\r\n")

  rqstLine:str = lines[0]
  method, path, protocol = rqstLine.split(' ')
  request_headers['method'] = method
  request_headers['path'] = path
  request_headers['protocol'] = protocol
  # no request time because pico does not have RTC

  for line in lines[1:]:
    if line == "":
      break
      
    key, value = line.split(":", 1)
    request_headers[key.strip()] = value.strip()

  return(request_headers)





async def constructResponse(request_headers, request_content)->bytes:
  """Setup initial headers, get desired response, send it"""
  headersEncoded:bytes
  contentEncoded:bytes

  response_headers = {}
  response_content, response_headers = await getContent(request_headers, request_content) # get/generate content based on request data

  response_headers.setdefault('statusCode', 200)
  response_headers.setdefault('statusMessage', 'OK')
  response_headers.setdefault('contentType', 'text/html; charset="UTF-8"')
  response_headers.setdefault('connection', 'close')

  if type(response_content) == 'str':
    contentEncoded = response_content.encode('utf-8')
  else:
    contentEncoded = response_content # assumed to be bytes

  # construct response header
  # no response time because pico does not have RTC
  headers =  f"HTTP/1.1 {response_headers['statusCode']} {response_headers['statusMessage']}\r\n"
  headers += f"Content-Length: {len(response_content)}\r\n"
  headers += f"Connection: {response_headers['connection']}\r\n"  
  headers += f"Content-Type: {response_headers['contentType']}\r\n"
  headers += f"\r\n"  #marks end of headers, start of body
  headersEncoded:bytes = headers.encode('utf-8')

  response = headersEncoded + contentEncoded
  return(response)





async def getContent(request_headers:dict, request_content:str)->tuple[str|bytes,dict]:
  """Returns HTML based on request headers"""
  response_headers = {}
  content:str = ''

  # home page / controller page
  path = request_headers['path']
  if path in ['', '/', '/home']:
    try:
      with open('home.html', 'r') as homePage:
        for line in homePage:
          content += str(line)
    except Exception as err:
      content = f'<p>Could not find home page. Err: {err}</p>'
    finally: 
      response_headers['contentType'] = 'text/html; charset="UTF-8"'

  elif path == '/favicon.ico':
    try:
      with open('favicon.ico', 'rb') as icon:
        content = icon.read()
      response_headers['contentType'] = 'image/x-icon'
    except Exception as err:
      content = f'Favicon error: {err}'
      response_headers['contentType'] = 'text/html; charset="UTF-8"'

  # process AJAX command and send response
  elif path == '/command':
    targetID = None
    targetValue = None
    json_data = None
    try:
      json_data = ujson.loads(request_content)
      targetID = json_data.get('targetID')
      targetValue = json_data.get('targetValue')
    except Exception as err:
      print(f'Error parsing JSON payload ({json_data}): {err}')
      statusMessage = 'Command failed'
    finally:
      if targetID:
        # execute command and get status message (if applicable)
        statusMessage = await executeCMD(targetID, targetValue)
      content = statusMessage
      response_headers['contentType'] = 'text/html; charset="UTF-8"'

  # trick iPhones into believing this network is valid (not very reliable)
  elif path == '/hotspot-detect.html':
    content = '<!DOCTYPE HTML><HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>'

  # trick android devices into believing this network is valid (unknown reliability)
  elif path == '/generate_204':
    response_headers['statusCode'] = 204
    response_headers['statusMessage'] = 'No Content'
    content = ''

  else:
    content = f"not-home, is {path}"
  
  return(content, response_headers)





async def executeCMD(cmd, val) -> str:
  """Takes command from client and executes it on hardware"""
  #print(f'Executing {cmd} with value {val}.')
  statusMessage = ''  # if a status message needs to be sent...

  # throttle controls
  if cmd in ['lThrottle', 'rThrottle']:
    # val is range -100 to 100... /100 to convert to decimal
    if cmd == 'lThrottle': await tikoSetLeft(decimalToPWM(int(val)/100))
    if cmd == 'rThrottle': await tikoSetRight(decimalToPWM(int(val)/100))

  # left hand side controls
  if cmd == 'lB': statusMessage = f'{cmd} not integrated'
  if cmd == 'lT': statusMessage = f'{cmd} not integrated'
  if cmd == 'm1': statusMessage = f'{cmd} not integrated'
  if cmd == 'lUp': await tikoForward()
  if cmd == 'lLeft': await tikoTurnLeft()
  if cmd == 'lRight': await tikoTurnRight()
  if cmd == 'lDown': await tikoReverse()

  # right hand side controls
  if cmd == 'rB': statusMessage = f'{cmd} not integrated'
  if cmd == 'rT': statusMessage = f'{cmd} not integrated'
  if cmd == 'm2': statusMessage = f'{cmd} not integrated'
  if cmd == 'rUp': statusMessage = f'{cmd} not integrated'
  if cmd == 'rLeft': statusMessage = f'{cmd} not integrated'
  if cmd == 'rRight': statusMessage = f'{cmd} not integrated'
  if cmd == 'rDown': await tikoStop()

  if not statusMessage: statusMessage = ''
  return(statusMessage)





if __name__ == "__main__":
  # welcome splash
  if oled is not None:
    oled.fill(0)
    oled.text('TIKONNIUM',28,16)
    oled.text('FALCON',40,24)
    oled.show()
  else:
    print('OLED display was not found')

  # get wifi config settings
  getConfig()
  ap = network.WLAN(network.AP_IF)
  ap.active(False)  # clean up old network
  utime.sleep(1)
  ap.config(ssid=str(ssidName), password=str(ssidPwd))
  ap.active(True)

  counter = 1 # start at 1 since it sleeps for 1 second during cleanup
  while not ap.active():
    print('Configuring access point...')
    counter += 1
    utime.sleep(1)
  print("Access point configured!")

  # guarantee splash screen shows for at least 5 seconds
  utime.sleep(min(5-counter,0))  

  ip = ap.ifconfig()[0]

  # stats screen
  if oled is not None:
    oled.fill(0)
    oled.text(f'host: {ssidName}', 0, 8)
    oled.text(f'pwd: {ssidPwd}', 0, 16)
    oled.text(f'website:', 0, 32)
    oled.text(str(ip), 8, 40)
    oled.show()
   
  asyncio.run(startServer())
