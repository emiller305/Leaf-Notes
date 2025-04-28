import numpy as np
import sounddevice as sd

fs = 44100
duration = 2.0
freq = 440
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
wave = 0.4 * np.sin(2 * np.pi * freq * t)


fs = 44100
duration = 2.0
freq = 350
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
wave2 = 0.4 * np.sin(2 * np.pi * freq * t)

wave_total = (wave + wave2)

sd.play(wave_total, samplerate=fs)
sd.wait()
