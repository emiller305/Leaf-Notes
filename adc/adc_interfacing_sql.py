import RPi.GPIO as GPIO
import smbus2
import time
import socket
import sqlite3
import os
import sys

DB_PATH = '/home/pi/your_database.db'
MAX_SIZE_BYTES = 1 * 1024 * 1024 * 1024  # 1 GB


GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.add_event_detect(5, GPIO.FALLING)



def check_db_size():
    if os.path.exists(DB_PATH):
        size = os.path.getsize(DB_PATH)
        if size >= MAX_SIZE_BYTES:
            print(f"[!] Database has reached {size / (1024**2):.2f} MB. Exiting.")
            sys.exit(1)

# Set up SQLite database
def create_database():
    conn = sqlite3.connect('adc_data.db')  # Database file
    c = conn.cursor()
    
    # Create table for ADC data if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS adc_readings_test16_stim (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                     adc_value INTEGER
                 )''')
    conn.commit()
    conn.close()
    
create_database()


channel = 1
address = 0x48
ADC_bus = smbus2.SMBus(channel)
data = [0b10111010, 0b10000000]
ADC_bus.write_i2c_block_data(address, 0x1, data)
ADC_bus.write_i2c_block_data(address, 0x03, [0x80, 0x00])
ADC_bus.write_i2c_block_data(address, 0x02, [0x00, 0x00])
gain = 1
i = 0

try:
	while True:
		#try:
		#	GPIO.wait_for_edge(5, GPIO.FALLING)
		#except KeyError as e:
			#print("GPIO alert lost, recovering...")
			#GPIO.cleanup(5)
			#GPIO.setup(5, GPIO.IN)

		#GPIO.wait_for_edge(5, GPIO.FALLING)
		#output = ADC_bus.read_word_data(address, 0x0)
		if GPIO.event_detected(5):
			output = ADC_bus.read_i2c_block_data(address, 0x0, 2)
			#print(output)
			out = (int(output[0]) << 8) | int(output[1])
			#print("binary out before negative output adjustment: ", bin(out))
			if out >= 32768:
				b = 0xFFFF
				out = out ^ b
				out += 1
				out = out * (-1)
			#print("binary out: ", bin(out))
			int_out = int(out)
			#print(int_out)
			
			# RANGE = 6.144 V
			# v_data = int_out*0.0001875
			
			# RANGE = 2.048 V
			# v_data = int_out*0.00006250095
			
			# RANGE = 1.024 V
			# v_data = int_out*0.00003125
			
			# RANGE = 0.512 V
			# v_data = int_out*0.000015625
			
			# RANGE = 0.256 V
			v_data = int_out*0.0000078125
			
			print("voltage: ", v_data)
			
			data = str(v_data/gain)
			adc_value = v_data/gain
			conn = sqlite3.connect('adc_data.db')
			c = conn.cursor()

			# Insert the ADC value into the database
			c.execute("INSERT INTO adc_readings_test16_stim (adc_value) VALUES (?)", (adc_value,))

			conn.commit()  # Save the data
			conn.close()
			print(f"Logged ADC value: {adc_value}")


			i += 1
			#time.sleep(0.01)
except KeyboardInterrupt:
	print("closing socket")
except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")
    raise
finally:
	GPIO.cleanup()
