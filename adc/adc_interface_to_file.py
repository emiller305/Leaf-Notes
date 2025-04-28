import RPi.GPIO as GPIO
import smbus2
import time

channel = 1
address = 0x48
ADC_bus = smbus2.SMBus(channel)
data = [0b10110100, 0b10000011]
ADC_bus.write_i2c_block_data(address, 0x1, data)

i = 0
with open("output.txt", "a") as file:  # "a" appends to the file
	while 1:
		#output = ADC_bus.read_word_data(address, 0x0)
		output = ADC_bus.read_i2c_block_data(address, 0x0, 2)
		print(output)
		out = (int(output[0]) << 8) | int(output[1])
		print("binary out before negative output adjustment: ", bin(out))
		if out >= 32768:
			b = 0xFFFF
			out = out ^ b
			out += 1
			out = out * (-1)
		print("binary out: ", bin(out))
		int_out = int(out)
		print(int_out)
		# for 6.144 V range
		# print("voltage: ", int_out*0.1875/1000.0)
		# for 1.024 V range
		v_data = int_out*0.00006250095
		print("voltage: ", int_out*0.00006250095)
		data = str(v_data/10)
		file.write(data + "\n")  # Save to file
        file.flush()  # Ensure it writes immediately
