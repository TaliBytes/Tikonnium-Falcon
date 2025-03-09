from machine import Pin, PWM
import network
import os
import time
import uasyncio #micro-python version of asyncio


ssidName:str|None = None
ssidPwd :str|None = None

# IMPORT WIFI CONFIGURATION ... 
def getConfig()->None:
  global ssidName, ssidPwd

  print('dir:', os.listdir())

  try:
    with open('/config.config', 'r') as config:

      for line in config:
        line:str = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
          setting, value = line.split('=', 1)
          setting = setting.strip()
          value = value.strip()

          if setting == "ssidName":
            ssidName = value
          elif setting == "ssidPwd":
            ssidPwd = ssidPwd

  except Exception as err:
    print('Fatal Error: config.config error ... ' + str(err))



def connectToHotspot()->None:
  global ssidName, ssidPwd

  if ssidName != None and ssidPwd != None:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(ssidName, ssidPwd)
    wlan.connect(ssidName, ssidPwd)

    while not wlan.isconnected():
      print("Connecting to hotspot...")
      time.sleep(1)

    print(f"Connected to {ssidName}!, Config:, {wlan.ifconfig()}")
  
  else:
    print('Missing ssidName or ssidPwd')



# 16 MotorR forward
# 17 MotorR backward
# 18 motorL forward
# 19 MotorL backward
# PMW range for each is 0-65535
pins = [16,17,18,19]
pwms = {p: PWM(Pin(p)) for p in pins}
pwmDuties = {p: 0 for p in pins}

# set start point for each pwm pin
print(f"Turned off each motor PWM pin and set frequency to 25MHz")
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
      await uasyncio.sleep(stepTime)

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
    uasyncio.create_task(transitionPMW(16, 65535, .25)),
    uasyncio.create_task(transitionPMW(17, 00000, .25)),
    uasyncio.create_task(transitionPMW(18, 65535, .25)),
    uasyncio.create_task(transitionPMW(19, 00000, .25)),
  ]
  await uasyncio.gather(*tasks)



# set tiko to move backward
async def tikoReverse()->None:
  tasks = [
    uasyncio.create_task(transitionPMW(16, 00000, .25)),
    uasyncio.create_task(transitionPMW(17, 65535, .25)),
    uasyncio.create_task(transitionPMW(18, 00000, .25)),
    uasyncio.create_task(transitionPMW(19, 65535, .25)),
  ]
  await uasyncio.gather(*tasks)



# modify/set direction of Tiko's left motor only
# dir -1 thru 1 ... neg = backward, pos = forward
async def tikoSetLeft(dir:int=0)->None:
  pwmVal = decimalToPWM(dir)
  if pwmVal > 0:   
    # forward
    tasks = [
      uasyncio.create_task(transitionPMW(18, pwmVal, .1)),
      uasyncio.create_task(transitionPMW(19, 000000, .1)),
    ]
  elif pwmVal < 0: 
    # backward
    tasks = [
      uasyncio.create_task(transitionPMW(18, 000000, .1)),
      uasyncio.create_task(transitionPMW(19, pwmVal, .1)),
    ]
  else:   
    # stopped         
    tasks = [
      uasyncio.create_task(transitionPMW(18, 0, .1)),
      uasyncio.create_task(transitionPMW(19, 0, .1)),
    ]

  await uasyncio.gather(*tasks)



# modify/set direction of Tiko's right motor only
# dir -1 thru 1 ... neg = backward, pos = forward
async def tikoSetRight(dir:int=0)->None:
  pwmVal = decimalToPWM(dir)
  if pwmVal > 0:   
    # forward
    tasks = [
      uasyncio.create_task(transitionPMW(16, pwmVal, .1)),
      uasyncio.create_task(transitionPMW(17, 000000, .1)),
    ]
  elif pwmVal < 0: 
    # backward
    tasks = [
      uasyncio.create_task(transitionPMW(16, 000000, .1)),
      uasyncio.create_task(transitionPMW(17, pwmVal, .1)),
    ]
  else:   
    # stopped         
    tasks = [
      uasyncio.create_task(transitionPMW(16, 0, .1)),
      uasyncio.create_task(transitionPMW(17, 0, .1)),
    ]

  await uasyncio.gather(*tasks)



# main logic loop
async def main():
  getConfig()
  connectToHotspot()

  while True:
    await tikoSetLeft(0)
    await tikoSetRight(0)

uasyncio.run(main())
