from machine import Pin, PWM
from time import sleep

# ----------------------------
# BUZZER SETUP
# ----------------------------
BUZZER_PIN = 4   # change if needed
buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty_u16(0)
btn = Pin(3, Pin.IN, Pin.PULL_DOWN)
btn_pr = 0   #indicate button state


# ----------------------------
# NOTE DICTIONARY: C3 to C7
# ----------------------------
NOTES = {
    "C3": 131,
    "CS3": 139,
    "D3": 147,
    "DS3": 156,
    "E3": 165,
    "F3": 175,
    "FS3": 185,
    "G3": 196,
    "GS3": 208,
    "A3": 220,
    "AS3": 233,
    "B3": 247,

    "C4": 262,
    "CS4": 277,
    "D4": 294,
    "DS4": 311,
    "E4": 330,
    "F4": 349,
    "FS4": 370,
    "G4": 392,
    "GS4": 415,
    "A4": 440,
    "AS4": 466,
    "B4": 494,

    "C5": 523,
    "CS5": 554,
    "D5": 587,
    "DS5": 622,
    "E5": 659,
    "F5": 698,
    "FS5": 740,
    "G5": 784,
    "GS5": 831,
    "A5": 880,
    "AS5": 932,
    "B5": 988,

    "C6": 1047,
    "CS6": 1109,
    "D6": 1175,
    "DS6": 1245,
    "E6": 1319,
    "F6": 1397,
    "FS6": 1480,
    "G6": 1568,
    "GS6": 1661,
    "A6": 1760,
    "AS6": 1865,
    "B6": 1976,

    "C7": 2093
}

# ----------------------------
# NOTE LENGTHS (tempo ~120) sc is tempo scaling(1/2 for double speed)
# ----------------------------
sc = 2/3
EIGHTH = 0.25*sc
QUARTER = 0.50*sc
DOTQUARTER = 0.75*sc
HALF = 1.00*sc
REST_GAP = 0.01

# ----------------------------
# PLAY FUNCTIONS
# ----------------------------
def play_note(note, duration):
    if note == "REST":
        buzzer.duty_u16(0)
        sleep(duration)
        return

    buzzer.freq(NOTES[note])
    buzzer.duty_u16(10000)   # volume
    sleep(duration)
    buzzer.duty_u16(0)
    sleep(REST_GAP)

def play_song(song):
    sleep(0.1)#wiat for switch to balance
    for note, duration in song:
        if btn.value() == 1:
            while(btn.value() == 1):
                continue
            btn_pr = 0
            break   #exit loop
        else:
            play_note(note, duration)
            
# ----------------------------
# MELODY (treble line only)
# Transcribed for buzzer use
# ----------------------------
melody = [
    # pickup
    ("A3", EIGHTH), ("C4", EIGHTH),

    # m1-6
    ("D4", QUARTER), ("D4", QUARTER), ("D4", EIGHTH), ("E4", EIGHTH),
    ("F4", QUARTER), ("F4", QUARTER), ("F4", EIGHTH), ("G4", EIGHTH),
    ("E4", QUARTER), ("E4", QUARTER), ("D4", EIGHTH), ("C4", EIGHTH),
    ("C4", EIGHTH), ("D4", DOTQUARTER), ("A3", EIGHTH), ("C4", EIGHTH),
    ("D4", QUARTER), ("D4", QUARTER), ("D4", EIGHTH), ("E4", EIGHTH),
    ("F4", QUARTER), ("F4", QUARTER), ("F4", EIGHTH), ("G4", EIGHTH),

    # m7-13
    ("E4", QUARTER), ("E4", QUARTER), ("D4", EIGHTH), ("C4", EIGHTH),
    ("D4", QUARTER), ("REST", QUARTER), ("A3", EIGHTH), ("C4", EIGHTH),
    ("D4", QUARTER), ("D4", QUARTER), ("D4", EIGHTH), ("F4", EIGHTH),
    ("G4", QUARTER), ("G4", QUARTER), ("G4", EIGHTH), ("A4", EIGHTH),
    ("AS4", QUARTER), ("AS4", QUARTER), ("A4", EIGHTH), ("G4", EIGHTH),
    ("A4", EIGHTH), ("D4", DOTQUARTER), ("D4", EIGHTH), ("E4", EIGHTH),
    ("F4", QUARTER), ("F4", QUARTER), ("G4", QUARTER),

    # m14-20
    ("A4", EIGHTH), ("D4", DOTQUARTER), ("D4", EIGHTH), ("F4", EIGHTH),
    ("E4", QUARTER), ("E4", QUARTER), ("F4", EIGHTH), ("D4", EIGHTH),
    ("E4", QUARTER), ("REST", QUARTER), ("A5", EIGHTH), ("C5", EIGHTH),
    ("D5", QUARTER), ("D5", QUARTER), ("D5", EIGHTH), ("E5", EIGHTH),
    ("F5", QUARTER), ("F5", QUARTER), ("F5", EIGHTH), ("G5", EIGHTH),
    ("E5", QUARTER), ("E5", QUARTER), ("D5", EIGHTH), ("C5", EIGHTH),
    ("C5", EIGHTH), ("D5", DOTQUARTER), ("A4", EIGHTH), ("C5", EIGHTH),

    # m21-27
    ("D5", QUARTER), ("D5", QUARTER), ("D5", EIGHTH), ("E5", EIGHTH),
    ("F5", QUARTER), ("F5", QUARTER), ("F5", EIGHTH), ("G5", EIGHTH),
    ("E5", QUARTER), ("E5", QUARTER), ("D5", EIGHTH), ("C5", EIGHTH),
    ("D5", QUARTER), ("REST", QUARTER), ("A4", EIGHTH), ("C5", EIGHTH),
    ("D5", QUARTER), ("D5", QUARTER), ("D5", EIGHTH), ("F5", EIGHTH),
    ("G5", QUARTER), ("G5", QUARTER), ("G5", EIGHTH), ("A5", EIGHTH),
    ("AS5", QUARTER), ("AS5", QUARTER), ("A5", EIGHTH), ("G5", EIGHTH),

    # m28-end
    ("A5", EIGHTH), ("D5", DOTQUARTER), ("D5", EIGHTH), ("E5", EIGHTH),
    ("F5", QUARTER), ("F5", QUARTER), ("G5", QUARTER),
    ("A5", EIGHTH), ("D5", DOTQUARTER), ("D5", EIGHTH), ("F5", EIGHTH),
    ("E5", QUARTER), ("E5", QUARTER), ("D5", EIGHTH), ("C5", EIGHTH),
    ("D4", HALF)
]

# ----------------------------
# PLAY IT
# ----------------------------
while True:
    
    if btn.value() == 1:
        btn_pr = 1
        print("play")
        while(btn.value() == 1):
            continue
        play_song(melody)
    else:
        buzzer.duty_u16(0)
        btn_pr = 0
    sleep(0.1)
