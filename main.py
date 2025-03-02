from machine import Pin, PWM
from time import sleep
import uasyncio #micro-python version of asyncio

# 16 MotorR forward
# 17 MotorR backward
# 18 motorL forward
# 19 MotorL backward
pins = [16,17,18,19]
pwms = {p: PWM(Pin(p)) for p in pins}
pwmDuties = {p: 0 for p in pins}

# set start point for each pwm pin
print(f"Turned off each motor PWM pin and set frequency to 25MHz")
for pwm in pwms.values():
  pwm.duty_u16(0)
  pwm.freq(25000)



# transition the duty cycle of a PWM pin
async def transitionPMW(pin, newDuty:int=0, seconds:float=1, steps:int=1000)->None:
  global pwms, pwmDuties

  stepTime = seconds/steps # how long each step will take
  curDuty = pwmDuties[pin] # current duty of on the pin
  step = abs((curDuty - newDuty) / steps) # how much the duty needs to change per iteration
  dirMultiplier = 1 if newDuty > curDuty else -1  #1 = stepping up to newDuty, -1 stepping down to newDuty

  if curDuty != newDuty:
    print(f"Pin {pin} transitioning to {newDuty} from {curDuty} over {seconds}s ({stepTime}s/step for {steps} steps)")
    for duty in range (curDuty, newDuty, int(step)*dirMultiplier):
      pwms[pin].duty_u16(round(duty,0))
      pwmDuties[pin] = duty
      await uasyncio.sleep(stepTime)

    # ensure new value is set
    pwms[pin].duty_u16(newDuty)
    pwmDuties[pin] = newDuty
    return None

  else: # old and new are equivalent
    print(f"C. Pin {pin} old and new duties are equivalent ... no transition")
    return None



# set tiko to move forward
async def tikoForward():
  tasks = [
    uasyncio.create_task(transitionPMW(16, 65535, .25)),
    uasyncio.create_task(transitionPMW(17, 00000, .25)),
    uasyncio.create_task(transitionPMW(18, 65535, .25)),
    uasyncio.create_task(transitionPMW(19, 00000, .25))
  ]
  await uasyncio.gather(*tasks)



# set tiko to move backward
async def tikoReverse():
  tasks = [
    uasyncio.create_task(transitionPMW(16, 00000, .25)),
    uasyncio.create_task(transitionPMW(17, 65535, .25)),
    uasyncio.create_task(transitionPMW(18, 00000, .25)),
    uasyncio.create_task(transitionPMW(19, 65535, .25))
  ]
  await uasyncio.gather(*tasks)



# main logic loop
async def main():
  while True:
    await tikoForward()
    await uasyncio.sleep(1)
    await tikoReverse()
    await uasyncio.sleep(1)

uasyncio.run(main())
