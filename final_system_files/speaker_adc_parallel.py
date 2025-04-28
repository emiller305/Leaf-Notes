import os
import subprocess
import signal

try:
	disp_proc = subprocess.Popen(["python /home/pi/senior-design-2025/display/display.py"], shell=True)

	adc_proc = subprocess.Popen(["python adc_interfacing_sckt.py"], shell = True, preexec_fn=os.setsid)
	#adc_proc = subprocess.Popen(["python adc_interfacing_sckt_sql.py"], shell=True)

	#speaker_proc = subprocess.Popen(["python gen_audio_stream.py"], shell = True)
	speaker_proc = subprocess.Popen(["python gen_audio_stream_sd.py"], shell = True, preexec_fn=os.setsid)
	
	adc_proc.wait()
	speaker_proc.wait()
	
except KeyboardInterrupt:
	try:
		os.killpg(os.getpgid(speaker_proc.pid), signal.SIGTERM)
		os.killpg(os.getpgid(adc_proc.pid), signal.SIGTERM)
		print("\n\nkilled subprocs\n\n")
	except:
		print("\n\ncouldn't kill one or more subprocs\n\n")

	# speaker_proc = subprocess.Popen(["aplay /usr/share/sounds/alsa/Front_Center.wav", "-c2"], shell = True)
	#os.system("speaker-test -c2")
	#os.system("/usr/bin/aplay -D dmix:1,0 -t raw -r 48000 -c 2 -f S32_LE /dev/zero")

