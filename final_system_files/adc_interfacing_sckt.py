import RPi.GPIO as GPIO
import smbus2
import time
import socket



HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 12342  # Choose any available port

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server listening on port {PORT}...")

sock_conn, addr = server_socket.accept()
print(f"Connected by {addr}")

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.add_event_detect(5, GPIO.FALLING, bouncetime=5)

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
			
			#print("voltage: ", v_data)
			data = str(v_data/gain)
			#if i < 10:
			sock_conn.sendall((data + '\n').encode())

			i += 1
			#time.sleep(0.01)
except KeyboardInterrupt:
	print("closing socket")
finally:
	GPIO.cleanup()
	sock_conn.close()
	server_socket.close()
