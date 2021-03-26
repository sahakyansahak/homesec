"Lorem Ipsum One love"

from ds18b20S import DsbS
import RPi.GPIO as GPIO
import sqlite3
import ast
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

sensor = DsbS()
conn = sqlite3.connect("DB/evth.db")
c = conn.cursor()

leds = [40, 38, 36, 32, 13, 15, 11]
stepper_motor = [37, 35, 33, 31]

for i in leds: GPIO.setup(i, GPIO.OUT)
for i in stepper_motor: GPIO.setup(i, GPIO.OUT)

start_time = 0

def stepper():
    GPIO.output(11, 1)
    halfstep_seq = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
        ]
    for i in range(100):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(stepper_motor[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.001)

while True:

    temps = sensor.getTemps()   
    data = ast.literal_eval(c.execute("SELECT * FROM hard").fetchall()[0][0])
    GPIO.output(leds[0], data["l1"])
    GPIO.output(leds[1], data["l2"])
    data["temp1"] = temps[0]
    data["temp2"] = temps[1]
    GPIO.output(leds[2], float(data["temp1"]) < float(data["heat1"]))
    GPIO.output(leds[3], float(data["temp2"]) < float(data["heat2"]))
    GPIO.output(leds[4], 1 if int(c.execute("SELECT * FROM sc_s").fetchall()[0][0]) else 0)
    GPIO.output(leds[5], 0 if int(c.execute("SELECT * FROM sc_s").fetchall()[0][0]) else 1)
    c.execute('UPDATE hard SET data = "' + str(data) +  '"')
    if int(c.execute("SELECT * FROM garage").fetchall()[0][0]):
        start_time = time.time()
        c.execute("UPDATE garage SET state = '0'")
    if time.time() - start_time < 11: stepper()
    else:
        GPIO.output(11, 0)
        start_time = 0 
        for i in stepper_motor: GPIO.output(i, 0)
    conn.commit()
    
