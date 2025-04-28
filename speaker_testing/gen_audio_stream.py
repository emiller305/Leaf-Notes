import pyaudio
import numpy as np
import socket
from threading import Thread
from threading import Lock


def music(shared_vars):
	print("\nrunning music thread!\n")
	data_to_proc = []
	got_new_data = False
	i = 0
	try:
		while 1:
			i += 1
			# while lock.locked():
				# print("\n\nchecking lock status: ", lock.locked())
				# pass
			lock.acquire()
			# print("lock acquired in music func")
			if shared_vars["new_data"]:
				print("found new data in music func")
				got_new_data = True
				data_to_proc = np.array(shared_vars["data"])
				shared_vars["new_data"] = False
			lock.release()
			if got_new_data:
				print("got new data")
				got_new_data = False
				print("\ndata_to_proc: ", data_to_proc, "\n")
				# Music stuff - replace w/sonification script
				sample_rate = 44100      
				duration = 5             # in seconds
				frequency = 200

				t = np.linspace(0, duration, int(sample_rate * duration), False)
				sine_wave = np.sin(2 * np.pi * frequency * t)

				audio_data = sine_wave.astype(np.float32)
				# audio_data2 = sine_wave.astype(np.float32)

				# Send raw PCM data to speaker

				p = pyaudio.PyAudio()
				stream = p.open(format=pyaudio.paFloat32,  # 32-bit float PCM
								channels=1,                # Mono audio - can't do serial?
								rate=sample_rate,
								output=True)
								
				stream.write(audio_data.tobytes())
				#stream.write(audio_data2.tobytes())
				print("\nwrote data\n")
	except:
		stream.stop_stream()
		stream.close()
		p.terminate()
			
def read_adc(shared_vars):
	data_stored = []
	while True:
		data_from_adc = client_socket.recv(1024)
		if data_from_adc:
			decoded_data = float(data_from_adc.decode().strip())
			print("Received:", decoded_data)
			data_stored.append(decoded_data)
			print("data_stored: ", data_stored)
		if len(data_stored) == 5:
			lock.acquire()
			print("data: ", shared_vars["data"])
			print("new_data: ", shared_vars["new_data"])
			if shared_vars["new_data"] == True:
				shared_vars["data"] = np.concatenate((shared_vars["data"], np.array(data_stored)))
			else:
				shared_vars["data"] = np.array(data_stored)
			print("sent new data")
			shared_vars["new_data"] = True
			print("new_data: ", shared_vars["new_data"])
			lock.release()
			data_stored = []
	
           
 
# Socket stuff
PI_IP = "172.20.10.4"  # Replace with Raspberry Pi's IP
PORT = 12344
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((PI_IP, PORT))
global data
data = np.array([])
lock = Lock()
global new_data
new_data = False
shared_vars = {
    "new_data": False,
    "data": np.array([])
}
t_music = Thread(target=music, args=(shared_vars,))
t_adc = Thread(target=read_adc, args=(shared_vars,))
t_adc.start()
t_music.start()
