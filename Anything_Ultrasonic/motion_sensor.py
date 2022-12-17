from gpiozero import MotionSensor

PIN = 4
pir = MotionSensor(PIN)

while True:
    pir.wait_for_motion()
    print("Motion detected!")
    pir.wait_for_no_motion()
    print("Motion ended!")
