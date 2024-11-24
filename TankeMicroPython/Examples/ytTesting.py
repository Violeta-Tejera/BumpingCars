import machine
from time import sleep

led = machine.Pin(2, machine.Pin.OUT)

while True:
  # ON
  led.on()
  sleep(1)
  
  # OFF
  led.off()
  sleep(1)
  