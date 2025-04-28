import numpy as np
import sounddevice as sd
import queue
import time
import threading

def music(audio_queue, stop_event):
    current_audio = None
    current_pos = 0

    def callback(outdata, frames, time_info, status):
        nonlocal current_audio, current_pos

        if status:
            print(f'Stream status: {status}')

        if stop_event.is_set():
            outdata.fill(0)
            return
       # Fetch new audio data if needed
        while current_audio is None or current_pos + frames > len(current_audio):
            try:
                data = audio_queue.get_nowait()
                new_audio = np.frombuffer(data, dtype='float32')
                if current_audio is None:
                    current_audio = new_audio
                    current_pos = 0
                else:
                    # Concatenate remaining audio with new audio
                    remaining = current_audio[current_pos:] if current_pos < len(current_audio) else np.array([])
                    current_audio = np.concatenate((remaining, new_audio))
                    current_pos = 0
            except queue.Empty:
                print(f"Queue empty, playing silence. Queue size: {audio_queue.qsize()}")
                outdata.fill(0)
                return
        # Copy samples to outdata
        samples_to_copy = min(frames, len(current_audio) - current_pos)
        outdata[:samples_to_copy, :] = current_audio[current_pos:current_pos + samples_to_copy].reshape(-1, 1)

        if samples_to_copy < frames:
            print(f"Underflow: only {samples_to_copy} samples available, needed {frames}")
            outdata[samples_to_copy:, :] = 0

        current_pos += samples_to_copy

    with sd.OutputStream(
        samplerate=44100,
        dtype='float32',
        channels=1,
        callback=callback,
        blocksize=1024,  # Increase blocksize for smoother playback
        latency='high'   # Higher latency to reduce underruns
    ) as stream:
        print("Audio stream started.")
        try:
            while not stop_event.is_set():
                time.sleep(0.05)  # Faster polling for responsiveness
                if audio_queue.qsize() < 2:
                    print(f"Low queue size: {audio_queue.qsize()}")
        except Exception as e:
            print(f"Error in music thread: {e}")
        finally:
            print("Stopping audio stream.")

    print("Audio stream closed.")
    
def gen_music(audio_queue, stop_event):
    print("\nGenerating sine wave...\n")
    sample_rate = 44100
    duration = 1  # Shorter duration for faster queuing
    frequency = 400
    amplitude = 0.2

    while not stop_event.is_set():
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
        audio_data = sine_wave.astype(np.float32)
        try:
            audio_queue.put(audio_data.tobytes(), timeout=1)
            print(f"Generated chunk, queue size: {audio_queue.qsize()}")
        except queue.Full:
            print("Queue full, skipping chunk.")
        time.sleep(0.0005)  # Minimal sleep to keep queue filled
def main():
    audio_queue = queue.Queue(maxsize=10)  # Increased queue size
    stop_event = threading.Event()

    t_play_music = threading.Thread(target=music, args=(audio_queue, stop_event))
    t_gen_music = threading.Thread(target=gen_music, args=(audio_queue, stop_event))

    t_play_music.start()
    t_gen_music.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nReceived interrupt, stopping...")
        stop_event.set()

        t_play_music.join(timeout=2)
        t_gen_music.join(timeout=2)

        if t_play_music.is_alive():
            print("Warning: Music thread did not terminate cleanly.")
        if t_gen_music.is_alive():
            print("Warning: Music generation thread did not terminate cleanly.")

        print("Program terminated.")

if __name__ == "__main__":
    main()
