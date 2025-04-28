# sonification example
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from midiutil import MIDIFile
import dask.array as da
import dask.dataframe as dd
import itertools as it
from math import log2, isinf, isnan

MIDI_A4 = 69   # MIDI Pitch number
FREQ_A4 = 440. # Hz
SEMITONE_RATIO = 2. ** (1. / 12.) # Ascending


filename = 'plant2_1min_033125.txt'
output_filename = 'out'
bpm = 20
duration_beats = 1
y_scale = 1

note_names = ['C1','C2','G2',
             'C3','E3','G3','A3','B3',
             'D4','E4','G4','A4','B4',
             'D5','E5','G5','A5','B5',
             'D6','E6','F#6','G6','A6']

def map_value(value, min_value,max_value,min_result,max_result):
    result = min_result + (value - min_value)/(max_value-min_value)*(max_result - min_result)
    return result

def str2midi(note_string):
    """
    Given a note string name (e.g. "Bb4"), returns its MIDI pitch number.
    """
    if note_string == "?":
        return nan
    data = note_string.strip().lower()
    name2delta = {"c": -9, "d": -7, "e": -5, "f": -4, "g": -2, "a": 0, "b": 2}
    accident2delta = {"b": -1, "#": 1, "x": 2}
    accidents = list(it.takewhile(lambda el: el in accident2delta, data[1:]))
    octave_delta = int(data[len(accidents) + 1:]) - 4
    return (MIDI_A4 +
          name2delta[data[0]] + # Name
          sum(accident2delta[ac] for ac in accidents) + # Accident
          12 * octave_delta # Octave
         )

df = dd.read_csv(filename, skiprows=1, 
    header=None, sep=' ', usecols=[2], dtype=str)

data = df[2].str.split('\t', n=3, expand=True)
col = data[1].astype(float)
col = col.compute()

sig_len = len(col)
time = np.linspace(0, sig_len - 1, sig_len)

t_data = map_value(time, min(time), max(time), duration_beats, 0)
duration_sec = (sig_len/200)/bpm
print('Duration:',duration_sec,'seconds')

y_data = map_value(col, min(col), max(col), 0, 1)

y_data = y_data**y_scale
y_data = np.array(y_data)

note_midis = [str2midi(n) for n in note_names]
n_notes = len(note_midis)
print('Resolution:',n_notes,'notes')

midi_data = []
vel_data = []
for i in range(sig_len):
    y = y_data[i]
    note_index = int(round(map_value(y, 0, 1, n_notes - 1, 0)))
    midi_data.append(note_midis[note_index])

my_midi_file = MIDIFile(1)
my_midi_file.addTempo(track=0, time=0, tempo=bpm)

my_midi_file.addProgramChange(0, 0, 0, 0)

for i in range(sig_len):
    my_midi_file.addNote(track=0, channel=0, pitch=midi_data[i], duration=2, volume=100, time=t_data[i])

with open(output_filename + '.mid', "wb") as f:
    my_midi_file.writeFile(f)
print('Saved', output_filename + '.mid')



