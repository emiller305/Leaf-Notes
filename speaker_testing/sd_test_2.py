import sounddevice as sd
import numpy as np

# Audio parameters
sample_rate = 44100  # Hz, standard for audio, supported by MAX98357
frequency = 400.0    # Hz
duration = 5.0       # seconds
amplitude = 0.5      # Lower amplitude to prevent clipping

# Set sounddevice defaults
sd.default.samplerate = sample_rate
sd.default.channels = 1  # Mono for MAX98357
sd.default.dtype = 'int16'  # 16-bit PCM, matches MAX98357
sd.default.blocksize = 2048  # Larger buffer to prevent underruns

# Generate time array and 400 Hz sine wave
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
y = amplitude * np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM
y_int16 = (y * 32767).astype(np.int16)

# Play the sound
sd.play(y_int16, sample_rate)
sd.wait()  # Wait until playback is complete
