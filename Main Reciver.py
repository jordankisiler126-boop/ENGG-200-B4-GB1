import aioble
import bluetooth
import uasyncio as asyncio
from machine import Pin, PWM
from time import sleep

# RENAME THIS FILE TO main.py WHEN SAVING TO THE PI PICO (Boat)

# ===============================
# RECEIVER CONFIG
# ===============================

_REMOTE_NAME = "B4_B1"                               # Your group name, i.e 'B1_A1' for Block 1, Group A1
_GENERIC_SERVICE_UUID = bluetooth.UUID(0x1848)      
_JOYSTICK_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

connected = False
led = Pin("LED", Pin.OUT)       # LED on Pi Pico
led_green = Pin(2, Pin.OUT)     # Make sure pin number matches wiring
                                #E is for throttle, Mi s direction of motor rotation
E1 = PWM(Pin(17), freq = 500, duty_u16 = 0)
M1 = Pin((16), Pin.OUT)

E2 = PWM(Pin(19), freq = 500, duty_u16 = 0)
M2 = Pin((18), Pin.OUT)
                                #Setup extra components here
morse_led = Pin((15), Pin.OUT)
buzzer = PWM(Pin(14), duty_u16 = 0)

trtl_L = 0
trtl_R = 0

deadzone = 0.2

def clamp(val):
    '''
    clamps values between -1 and 1
    input: unclamped value
    return:clamped value
    '''
    return(max(-1.0, min(val, 1.0)))

def stop_motors():
    '''
    
    '''
    E1.duty_u16(0)
    E2.duty_u16(0)
    
def drive(L, R):
    '''
    discription: send control signals to the motor controller
    inputs: left and right throttle
    returns: none
    '''
    if abs(L) > deadzone or abs(R) > deadzone:
        
        L_flag = 0
        R_flag = 0
        
        if L > deadzone:
            M1.off()
        else:
            M1.on()
            L_flag = 1
            
            
        if R > deadzone:
            M2.off()
        else:
            M2.on()
            R_flag = 1
            
            
        E1.duty_u16(int((abs(L) * 65335)))
        E2.duty_u16(int((abs(R) * 65335)))
        #print((int((abs(R) * 100) * 65335)))
        
        print(f'Left:{L_flag}, Right:{R_flag}')
        
        sleep(0.001)
        
    else:
        
        stop_motors()
        
        print('idle')


def handle_command(cmd: bytes):         # Reading and using joystick data from transmitter
    """
    Expects format: "<trtl_stk>,<str_stk>,<btn1>,<btn2>"
    """
    #make them global so they can be itteratied
    global trtl_L
    global trtl_R
    # Decode data from transmitter
    try:
        msg = cmd.decode().strip()
        trtl_stk = float(msg.split(",")[0])
        str_stk = float(msg.split(",")[1])
        btn1 = int(msg.split(",")[2])
        btn2 = int(msg.split(",")[3])
    except Exception as e:
        print("Parse error:", e)
        stop_motors()
        return
    
    #def adc_convert(trtl):
        
        #target = round(float((trtl - 32768)/ 32768),2)		#Center at 0 and go from -1 to 1
        
        #return target 
    # convert adc into throttle and steering range: -1 to 1
    
    if btn1 == 1:
        morse_led.on()
    else:
        morse_led.off()
        
    if btn2 == 1:
        buzzer.freq(130)
        buzzer.duty_u16(65000)
    else:
        buzzer.duty_u16(0)
    
    #print(trtl_stk)
    
    #set a target for the throttle to reach
    target_L = clamp((trtl_stk + str_stk))
    target_R = clamp((trtl_stk - str_stk))
    
    #ramp function
    trtl_L += (target_L - trtl_L) / 5
    trtl_R += (target_R - trtl_R) / 5
    
    #print(trtl_L)
    
    drive(trtl_L, trtl_R)
    
    print(f'Throttle L {trtl_L}, Throttle R {trtl_R}')
    
    sleep(0.001)
    
# ===============================
# BLUETOOTH CONNECT
# ===============================

# DO NOT modify any code in this section, this handles Bluetooth communication.

async def find_remote():        # Finding bluetooth transmitter
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == _REMOTE_NAME:
                return result.device
    return None

async def connect_task():       # Connecting to bluetooth transmitter
    global connected
    while True:
        device = await find_remote()
        print("Connecting...")
        if not device:
            await asyncio.sleep(2)
            continue
        try:
            connection = await device.connect()
            print('Connected')
        except asyncio.TimeoutError:
            continue

        async with connection:
            connected = True
            led.on()            # Green LED on (blinking) when connected
            service = await connection.service(_GENERIC_SERVICE_UUID)
            characteristic = await service.characteristic(_JOYSTICK_CHARACTERISTIC_UUID)
            await characteristic.subscribe(notify=True)
            
            while True:
                try:
                    cmd = await characteristic.notified()
                    handle_command(cmd)
                except Exception as e:
                    print("Error:", e)
                    connected = False
                    led.off()
                    stop_motors()
                    break

        connected = False
        led.off()               # Green LED off when not connected
        stop_motors()           # Make sure motors turn off when connection is lost
        await asyncio.sleep(2)

# ===============================
# LED BLINKER
# ===============================

async def blink_task():             # LEDs blink while bluetooth connected
    toggle = True
    while True:
        led.value(toggle)           # Pico LED
        led_green.value(toggle)     # Green LED
        toggle = not toggle
        await asyncio.sleep_ms(250 if not connected else 1000)

# ===============================
# MAIN LOOP
# ===============================

async def main():
    await asyncio.gather(connect_task(), blink_task())
    
asyncio.run(main())

'''
while True:
    str_stk = round(float((trtl - 32768)/ 32768),2)		#Center at 0 and go from -1 to 1
    trtl_stk = round(float((str_ - 32768)/ 32768),2)		#Center at 0 and go from -1 to 1
    
    target_L = clamp((trtl_stk + str_stk))
    
    target_R = clamp((trtl_stk - str_stk))
    
    trtl_L += (target_L - trtl_L) / 50
    trtl_R += (target_R - trtl_R) / 50
                                            #Drive the motors
    drive(trtl_L, trtl_R)
    
    print(f'Throttle L {trtl_L}, Throttle R {trtl_R}')
    
    sleep(0.001)
'''