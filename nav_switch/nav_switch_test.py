import RPi.GPIO as GPIO

def up_callback(channel):
	print("nav switch up was presssed!")

def down_callback(channel):
	print("nav switch down was pressed!")
	
def center_callback(channel):
	print("nav switch center was pressed!")

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN)
GPIO.setup(26, GPIO.IN)
GPIO.setup(16, GPIO.IN)

GPIO.add_event_detect(6,GPIO.RISING,callback=up_callback)
GPIO.add_event_detect(26,GPIO.RISING,callback=center_callback)
GPIO.add_event_detect(16,GPIO.RISING,callback=down_callback)

input("Waiting for button to be pressed...\n")
GPIO.cleanup()
print("cleaned up")
