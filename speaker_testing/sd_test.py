import numpy as np
import sounddevice as sd
import threading
import queue
import time

sample_rate = 44100
channels = 1
dtype = 'float32'
blocksize = 1024  # Matches stream block size
frequency = 500.0  # Hz
device = None      # Use default device (set to specific ID or name if needed, e.g., 2)
amplitude = 0.2    # Safe amplitude to avoid clipping
samplerate = 44100 # Standard sample rate, matches MAX98357

audio_queue = queue.Queue()

# Generator thread: generate blocksize-length sine chunks
def generate_music_chunks():
    t = np.arange(blocksize) / sample_rate
    next_time = time.time()
    while True:
        sine_wave = amplitude * np.sin(2 * np.pi * frequency * t).astype(np.float32)
        audio_queue.put(sine_wave.tobytes())
        next_time += blocksize / sample_rate
        sleep_duration = max(0, next_time - time.time())
        time.sleep(sleep_duration)

# Audio stream callback
def callback(outdata, frames, time_info, status):
    if status:
        print('Stream status:', status)
    try:
        data = audio_queue.get_nowait()
    except queue.Empty:
        outdata.fill(0)
        return

    audio_data = np.frombuffer(data, dtype=dtype)

    # Ensure size matches frames * channels
    expected = frames * channels
    if len(audio_data) < expected:
        audio_data = np.pad(audio_data, (0, expected - len(audio_data)))
    elif len(audio_data) > expected:
        audio_data = audio_data[:expected]

    outdata[:] = audio_data.reshape(-1, channels)

# Start generator thread
threading.Thread(target=generate_music_chunks, daemon=True).start()

# Start audio stream
with sd.OutputStream(
            samplerate=44100,
            dtype='float32',
            channels=1,
            callback=callback,
            blocksize=1024,
            latency='high'
    ):
    print('#' * 80)
    print('Press Return to quit')
    print('#' * 80)
    input("?? Playing sine wave... Press Enter to stop.\n")
