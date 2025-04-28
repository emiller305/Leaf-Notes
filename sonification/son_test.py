from midiutil import MIDIFile
import numpy as np
import random
from collections import deque
from scipy.stats import bartlett

fs = 64
sm_frame_sz = 0.25
lg_frame_sz = 10

NOTE_BOOK = {'pos_1': ['F#'], 'neg_1': ['F'],
              'pos_2': ['G'], 'neg_2': ['E'],
              'pos_3': ['A'], 'neg_3': ['D'],
              'pos_4': ['B'], 'neg_4': ['C']}

OCTAVE = 5
NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

def note_to_number(note, octave):
    note = NOTES.index(note)
    return note + (octave * 12)

# === SETUP ===
sm_win = deque(maxlen=int(fs * sm_frame_sz))
prev_win = deque(maxlen=int(fs * sm_frame_sz))
lg_win = deque(maxlen=int(fs * lg_frame_sz))

signal = [[random.random() for _ in range(64)] for _ in range(720)]

# Create MIDI file
outM = MIDIFile(1)
track = 0
channel = 0
time = 0
duration = 1
tempo = 60
volume = 100
outM.addTempo(track, time, tempo)

# Loop over signal
for frame in signal:
    for val in frame:
        if len(sm_win) == sm_win.maxlen:
            prev_win = deque(sm_win, maxlen=sm_win.maxlen)
        sm_win.append(val)
        lg_win.append(val)

        if len(sm_win) < sm_win.maxlen or len(lg_win) < lg_win.maxlen:
            continue

        avg = np.mean(sm_win)
        std = np.std(sm_win)
        z = (sm_win[-1] - avg) / std if std != 0 else 0
        abs_z = abs(z)

        # Determine note key
        if abs_z < 1:
            note_key = 'pos_1' if z > 0 else 'neg_1'
        elif abs_z < 2:
            note_key = 'pos_2' if z > 0 else 'neg_2'
        elif abs_z < 3:
            note_key = 'pos_3' if z > 0 else 'neg_3'
        else:
            note_key = 'pos_4' if z > 0 else 'neg_4'

        scale_change = 0
        try:
            _, p = bartlett(sm_win, prev_win)
            if p < 0.05:
                scale_change = 0  # optional switch
        except:
            pass

        out_note = NOTE_BOOK[note_key][scale_change]
        note_num = note_to_number(out_note, OCTAVE)
        outM.addNote(track, channel, note_num, time, duration, volume)
        time += 1

# Save the MIDI file
with open("output.mid", "wb") as f:
    outM.writeFile(f)

print("? MIDI file written as 'output.mid'")
