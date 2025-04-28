import numpy as np
import socket
import queue
import time
import sounddevice as sd
from threading import Thread, Lock, Event
import random
import RPi.GPIO as GPIO
from gen_sonif_test_3 import *
from functools import partial


def music(shared_vars, audio_queue, stop_event):
    current_audio = None
    current_pos = 0

    def callback(outdata, frames, time_info, status):
        nonlocal current_audio, current_pos

        if status:
            print(f'Stream status: {status}')

        if stop_event.is_set():
            outdata.fill(0)
            return

        while current_audio is None or current_pos + frames > len(current_audio):
            try:
                data = audio_queue.get_nowait()
                new_audio = np.frombuffer(data, dtype='float32')
                if current_audio is None:
                    current_audio = new_audio
                else:
                    remaining = current_audio[current_pos:] if current_pos < len(current_audio) else np.array([])
                    current_audio = np.concatenate((remaining, new_audio))
                current_pos = 0
            except queue.Empty:
                #print(f"Queue empty, playing silence. Queue size: {audio_queue.qsize()}")
                outdata.fill(0)
                return

        samples_to_copy = min(frames, len(current_audio) - current_pos)
        outdata[:samples_to_copy, :] = current_audio[current_pos:current_pos + samples_to_copy].reshape(-1, 1)

        if samples_to_copy < frames:
            print(f"Underflow: only {samples_to_copy} samples available, needed {frames}")
            outdata[samples_to_copy:, :] = 0

        current_pos += samples_to_copy
    try:
        with sd.OutputStream(
            samplerate=44100,
            dtype='float32',
            channels=1,
            callback=callback,
            blocksize=1024,
            latency='high'
    ):
            print("Audio stream started.")
            while not stop_event.is_set():
                time.sleep(0.1)
            print("Stopping audio stream.")
    except KeyboardInterrupt:
        print("stopping music")
    except e as Exception:
        print(e)

def gen_music(shared_vars, audio_queue, stop_event, shared_amp):
    print("\nRunning music generation thread...\n")
    last_data = np.array([])  # Holds the last data received
    frequency = 400  # Default frequency
    prev_frequency = frequency
    chord_freqs = [400, 400, 400, 400]
    phase = 0  # Phase accumulator
    chord_phases = [0, 0, 0, 0]
    add_data_to_q  = 0
    duration = 0.55
    sample_rate = 44100
    sm_window = []
    chord_prog = 0
    change_chords = 0
    stim_temp = 0
    stim_note = 0
    avg = 0
    
    while not stop_event.is_set():
        with amp_lock:
            amplitude = shared_amp["amplitude"]
            #print("\n\nnew amp: ", amplitude)
        with lock:
            if shared_vars["new_data"]:
                print("Found new data in music func")
                last_data = np.array(shared_vars["data"])  # Update data
                shared_vars["new_data"] = False  # Reset flag
                
                audio_data_son, frequency, chord_freqs, phase, chord_phases, sm_window, chord_prog, change_chords, stim_temp, stim_note, avg = create_music_arr(last_data, duration, sample_rate, prev_frequency, chord_freqs, phase, chord_phases, amplitude, sm_window, chord_prog, change_chords, stim_temp, stim_note, avg)
                prev_frequency = frequency
                if stim_note == 1 and stim_temp == 0:
                    with open(stim_filename, "w") as f:
                        f.write("1")
                        print("wrote to file")
                elif stim_note == 0 and stim_temp == 1:
                    with open(stim_filename, "w") as f:
                        f.write("0")
                        print("wrote 0 to file")
                print("audio_data_son_length: ", len(audio_data_son))
                
                try:
                    if len(audio_data_son) > 0:
                        if int(sample_rate * duration) != len(audio_data_son):
                            print("mismatched lengths! audio_data_son is ", len(audio_data_son), ", but should ben", int(sample_rate * duration))
                        audio_queue.put(audio_data_son.tobytes(), timeout=1)
                        #print("byte stream:", audio_data.tobytes())
                        print(f"Generated chunk, queue size: {audio_queue.qsize()}")
                except queue.Full:
                    print("Queue full, skipping chunk.")
                # Checking if watered:
                print("average: ", avg)

        # Short delay to prevent CPU overuse
        time.sleep(0.0005)


def read_adc(shared_vars, audio_queue, stop_event):
    data_stored = []
    try:
        while not stop_event.is_set():
            buff = ''
            data_from_adc = client_socket.recv(1024)
            if data_from_adc:
                buff += data_from_adc.decode()
                # print("Received before splitting if needed: ", data_from_adc.decode())
                while '\n' in buff:
                    try:
                        line, buff = buff.split('\n', 1)
                        decoded_data = float(line.strip())
                        #print("Received:", decoded_data)
                        if decoded_data < 2.5:
                            data_stored.append(decoded_data)
                    except ValueError:
                        print(f"Value Error: can't parse line, skipping this data: {line}")
                    if len(data_stored) == 64:
                        #print("sending data")
                        with lock:
                            if shared_vars["new_data"]:
                                shared_vars["data"] = np.concatenate((shared_vars["data"], np.array(data_stored)))
                                print("appended two windows")
                            else:
                                shared_vars["data"] = np.array(data_stored)
                                shared_vars["new_data"] = True
                        data_stored = []
    except OSError as e:
        print(f"Socket error: {e}")
    finally:
        print("ADC thread exiting.")


def up_callback(_, shared_amp):
    with amp_lock:
        print("up was pressed: increasing volume")
        curr_amplitude = shared_amp["amplitude"]
        if curr_amplitude < 0.6:
            curr_amplitude += 0.2
            shared_amp["amplitude"] = curr_amplitude
    with open(amp_filename, "w") as f:
        f.write('Volume: {0}'.format(int(curr_amplitude*5)))

def down_callback(_, shared_amp):
    with amp_lock:
        print("down was pressed: lowering volume")
        curr_amplitude = shared_amp["amplitude"]
        if curr_amplitude >= 0.2:
            curr_amplitude -= 0.2
            shared_amp["amplitude"] = curr_amplitude
    with open(amp_filename, "w") as f:
        if curr_amplitude == 0.0:
            f.write('Volume: OFF')
            print("wrote OFF")
        else:
            f.write('Volume: {0}'.format(int(curr_amplitude*5)))


def music_toggle_callback(_, shared_amp):
    with amp_lock:
        print("center was pressed: turning off music")
        shared_amp["amplitude"] = 0.0
    with open(amp_filename, "w") as f:
        f.write('Volume: OFF')


# --- Main setup ---

PI_IP = "172.20.10.4"
PORT = 12342
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((PI_IP, PORT))


# initialize shared vars
lock = Lock()
audio_queue = queue.Queue(maxsize=2)
stop_event = Event()
shared_vars = {
    "new_data": False,
    "data": np.array([])
}
initial_amplitude = 0.2
shared_amp = {"amplitude": initial_amplitude}
amp_lock = Lock()

amp_filename = "/home/pi/senior-design-2025/display/volume.txt"
stim_filename = "/home/pi/senior-design-2025/display/stimulus.txt"
# Nav Switch Setup - GPIO pins 6 (increase vol), 26 (turn on/off vol), 16 (decrease vol)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(26, GPIO.IN)
GPIO.setup(16, GPIO.IN)

up_callback_w_args = partial(up_callback, shared_amp=shared_amp)
down_callback_w_args = partial(down_callback, shared_amp=shared_amp)
music_toggle_callback_w_args = partial(music_toggle_callback, shared_amp=shared_amp)

GPIO.add_event_detect(6,GPIO.RISING,callback=up_callback_w_args, bouncetime=200)
GPIO.add_event_detect(16,GPIO.RISING,callback=down_callback_w_args, bouncetime=200)
GPIO.add_event_detect(26,GPIO.RISING,callback=music_toggle_callback_w_args, bouncetime=200)

#start threads
t_play_music = Thread(target=music, args=(shared_vars, audio_queue, stop_event))
t_adc = Thread(target=read_adc, args=(shared_vars, audio_queue, stop_event))
t_gen_music = Thread(target=gen_music, args=(shared_vars, audio_queue, stop_event, shared_amp))

t_adc.start()
t_gen_music.start()
t_play_music.start()

# --- Graceful shutdown ---
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nReceived Ctrl+C, shutting down...")
    stop_event.set()
    client_socket.close()

    t_adc.join(timeout=2)
    t_gen_music.join(timeout=2)
    t_play_music.join(timeout=2)

    if t_adc.is_alive():
        print("Warning: ADC thread did not terminate.")
    if t_gen_music.is_alive():
        print("Warning: Music generation thread did not terminate.")
    if t_play_music.is_alive():
        print("Warning: Music playback thread did not terminate.")

    print("Shutdown complete.")
