#!/usr/bin/env python3
"""Play a sine signal."""
import numpy as np
import sounddevice as sd
import sys

# Hardcoded parameters
frequency = 400.0  # Hz
device = None      # Use default device (set to specific ID or name if needed, e.g., 2)
amplitude = 0.2    # Safe amplitude to avoid clipping
samplerate = 44100 # Standard sample rate, matches MAX98357
duration = 2

start_idx = 0

try:
    def callback(outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        
        note_num_C = 5*12
        C_freq = 440.0 * (2 ** ((note_num_C - 69) / 12.0))
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        wave1 = (amplitude * np.sin(2 * np.pi * C_freq * t))
        #wave2 = (amplitude * np.sin(2 * np.pi * frequency2 * t))
        outdata[:] = wave1[0:383].reshape(-1, 1) #+ wave2
        

    with sd.OutputStream(device=device, channels=1, callback=callback,
                        samplerate=samplerate):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    sys.exit('')
except Exception as e:
    sys.exit(type(e).__name__ + ': ' + str(e))
