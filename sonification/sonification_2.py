## Leyla Ulku, Senior Design Project, 4/20/25
# Final sonification function
from midiutil import MIDIFile
import numpy as np
import pandas as pd
from collections import deque
import mingus
from mingus.containers import Note
import process
import note_utils
import pretty_midi as pm
from pretty_midi import Instrument
from pretty_midi import Note


NOTE_BOOK = {'pos_1': ['G', 'C', 'D'], 'neg_1': ['E', 'A', 'B'],
              'pos_2': ['A', 'E', 'F#'], 'neg_2': ['D', 'Bb', 'A'],
              'pos_3': ['C', 'D','E'], 'neg_3': ['C', 'G', 'E'],
              'pos_4': ['B', 'F', 'G'], 'neg_4': ['F', 'F', 'Gb']}
CHORD_BOOK = [[60,64,67,72], # C-major 3 midi nums
               [65,69,72,76], # Fmajor 3 midi nums
               [67,71,74,78]] # G major 3 midi nums

NOTE_OCTAVE = 5
CHORD_OCTAVE = 3

pm = pm.PrettyMIDI()
instrument = Instrument(program=0)

def sonification(data, lg_window, fs):
    sm_win = data
    lg_window.append(sm_win)
    chord_note_freq = []

    (avg, std) = process.stats(sm_win)
    note_key = process.z_score(sm_win, std, avg)
    scale_change = process.lev_test(sm_win, lg_window)

    if scale_change == 1:
        chord_prog += 1
        if chord_prog == 2:
            scale_change = 2
        elif chord_prog > 2:
            change_chords += 1
            if (change_chords > 3):
                change_chords = 0

    out_note = NOTE_BOOK[note_key][scale_change]
    out_chord = CHORD_BOOK[scale_change]
    note_num = note_utils.note_to_number(out_note, NOTE_OCTAVE)

    for note_num in out_chord:
        chord_note = Note(velocity=100, pitch=note_num, start=0, end=1)
        instrument.notes.append(chord_note)

    note = Note(velocity=100, pitch=note_num, start=time, end=time + duration)
    instrument.notes.append(note)
    pm.instruments.append(instrument)

    note_freq = note_utils.midi_to_freq(note_num)
    
    i = 0
    for note_num in out_chord:
        chord_note_freq[i] = note_utils.midi_to_freq(note_num)
        i += 1

    chord_wave = (1/4)*sum(np.sin(2 * np.pi * f * t) for f in chord_note_freq)
    note_wave = 1.5*(np.sin(2*np.pi*note_freq*t))
    return chord_wave + note_wave

        


    
    


