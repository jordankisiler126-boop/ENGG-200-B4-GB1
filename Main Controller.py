import aioble
import bluetooth
import uasyncio as asyncio
from micropython import const
from machine import ADC, Pin
import gc

# RENAME THIS FILE TO main.py WHEN SAVING TO THE PI PICO (Controller)

# ===============================
# TRANSMITTER CONFIG
# ===============================

_DEVICE_NAME = "B4_B1"                               # Your group name, i.e 'B1_A1' for Block 1, Group A1
_GENERIC_SERVICE_UUID = bluetooth.UUID(0x1848)          
_JOYSTICK_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E) 
_ADV_INTERVAL_MS = 250_000
_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

# ===============================
# HARDWARE SETUP
# ===============================

# Make sure pin numbers match wiring

adc_trtl = ADC(27)          # throttle joystick (L)
adc_str = ADC(26)         # steer joystick (R)
led = Pin("LED", Pin.OUT)   # LED on Pi Pico
led1 = Pin(2,Pin.OUT)   #Led on Controller
btn_1 = Pin(16, Pin.IN, Pin.PULL_DOWN)
btn_2 = Pin(17, Pin.IN, Pin.PULL_DOWN)
# Set default as disconnected
connected = False
connection = None

# ===============================
# BLE SERVICE
# ===============================

remote_service = aioble.Service(_GENERIC_SERVICE_UUID)
joystick_char = aioble.Characteristic(remote_service,
                                       _JOYSTICK_CHARACTERISTIC_UUID,
                                       read=True,
                                       notify=True)
aioble.register_services(remote_service)

# ===============================
# BLE TASKS
# ===============================

# DO NOT modify either advertise_task() or blink_task() unless absoloutely required.

async def advertise_task():     # Connecting to bluetooth receiver
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(_ADV_INTERVAL_MS,
                                          name=_DEVICE_NAME,
                                          appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL,
                                          services=[_GENERIC_SERVICE_UUID]) as connection:
            connected = True
            await connection.disconnected()

async def joystick_task():      # Sending joystick data to receiver
    global connected
    last_left = last_right = last_btn1 = last_btn2 = -1
    
    def adc_convert(trtl):
        
        target = round(float((trtl - 32768)/ 32768),3)		#Center at 0 and go from -1 to 1
        
        return target
    
    while True:
        # Read data if connected
        if connected:
            left_val = adc_convert(adc_trtl.read_u16())
            right_val = adc_convert(adc_str.read_u16())
            
            print(f'L:{left_val}, R:{right_val}')

            # IF ADDING NEW COMPONENTS, READ INPUTS HERE.
            btn1 = btn_1.value()
            btn2 = btn_2.value()
            print(f'btn1:{btn1}, btn2:{btn2}')
            
            
            # Send only if changed
            if left_val != last_left or right_val != last_right or last_btn1 != btn1 or last_btn2 != btn2:
                msg = f"{left_val},{right_val},{btn1},{btn2}"			#20 characters MAX
                joystick_char.notify(connection, msg.encode())
                last_left, last_right, last_btn1, last_btn2 = left_val, right_val, btn1, btn2
                print("Sent →", msg)

        await asyncio.sleep_ms(1)

async def blink_task():     # Pico LED blinks when bluetooth connected
    toggle = True
    while True:
        gc.collect()
        led.value(toggle)
        led1.value(toggle)
        toggle = not toggle
        await asyncio.sleep_ms(1000 if connected else 250)

# ===============================
# MAIN LOOP
# ===============================

async def main():
    gc.collect()
    await asyncio.gather(advertise_task(), joystick_task(), blink_task())

asyncio.run(main())

