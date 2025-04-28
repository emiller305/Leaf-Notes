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


PROG_145 = {'pos_1': ['G', 'C', 'D', 'G'], 'neg_1': ['E', 'A', 'B', 'E'], # 145 Chord Progression
              'pos_2': ['A', 'E', 'F#', 'A'], 'neg_2': ['D', 'Bb', 'A', 'D'],
              'pos_3': ['C', 'D','E', 'C'], 'neg_3': ['C', 'G', 'E', 'C'],
              'pos_4': ['B', 'F', 'G', 'B'], 'neg_4': ['F', 'F', 'Gb', 'F']}

PROG_1564 = {'pos_1': ['G', 'D', 'E', 'C'], 'neg_1': ['E', 'B', 'C#', 'A'], # 1564 Chord progression
              'pos_2': ['A', 'F#', 'G#', 'E'], 'neg_2': ['D', 'A', 'A', 'Bb'],
              'pos_3': ['C', 'E', 'B', 'D'], 'neg_3': ['C', 'E', 'B', 'G'],
              'pos_4': ['B', 'G', 'F', 'F'], 'neg_4': ['F', 'Gb', 'D', 'F'] }

PROG_4415 = { 'pos_1': ['C', 'C', 'G', 'D'], 'neg_1': ['A', 'A', 'E', 'B'], # 4415 Chord progression 
              'pos_2': ['E', 'E', 'A', 'F#'], 'neg_2': ['Bb', 'Bb', 'D', 'A'],
              'pos_3': ['D', 'D', 'C', 'E'], 'neg_3': ['G', 'G', 'C', 'E'],
              'pos_4': ['F', 'F', 'B', 'G'], 'neg_4': ['F', 'F', 'F', 'Gb'] }

PROG_1645 = {'pos_1': ['G', 'E', 'C', 'D'], 'neg_1': ['E', 'C#', 'A', 'B'], # 1645 Chord Progression
              'pos_2': ['A', 'G#', 'E', 'F#'], 'neg_2': ['D', 'A', 'Bb', 'A'],
              'pos_3': ['C', 'B', 'D', 'E'], 'neg_3': ['C', 'B', 'G', 'E'],
              'pos_4': ['B', 'F', 'F', 'G'], 'neg_4': ['F', 'D', 'F', 'Gb'] }

NOTE_BOOK = [PROG_145, PROG_1564, PROG_4415, PROG_1645]
    
CHORD_BOOK = {0:[[60,64,67], # Chord prog 1: 1-4-5-1
               [65,69,72], # Fmajor 3 midi nums
               [67,71,74], # G major 3 midi nums
               [60,64,67]], # C-major 3 midi nums

               1: [[48, 52, 55], # Chord prog 2: 1-5-6-4
                [55, 59, 50],
                [ 57, 59, 52],
                [53, 57, 48]], 

               2: [[53, 57, 48], # Chord prog 3: 4-4-1-5
                [53, 57, 48],
                [48, 52, 55],
                [55, 59, 50]],

               3: [[48, 52, 55], # Chord prog 4: 1-6-4-5
                [57, 59, 52],
                [53, 57, 48], 
                [55, 59, 50]]
}

NOTE_OCTAVE = 5
CHORD_OCTAVE = 3

pm = pm.PrettyMIDI()
instrument = Instrument(program=0)

def sonification(data, prev_window, fs, chord_change, scale_change, stim, stim_temp duration):
    prev_window = sm_win
    sm_win = data
    chord_note_freq = []

    (avg, std) = process.stats(sm_win)
    note_key = process.z_score(sm_win, std, avg)
    scale_change = process.lev_test(sm_win, prev_window)
    stim = process.pear_test(sm_win, prev_window)

    if scale_change == 1:
        chord_prog += 1
        if chord_prog == 2:
            scale_change = 2
        elif chord_prog > 2:
            change_chords += 1
            if (change_chords > 3):
                change_chords = 0

    out_note = NOTE_BOOK[note_key][scale_change]
    out_chord = CHORD_BOOK[chord_change][scale_change]
    note_num = note_utils.note_to_number(out_note, NOTE_OCTAVE)

    for note_num in out_chord:
        chord_note = Note(velocity=100, pitch=note_num, start=0, end=duration)
        instrument.notes.append(chord_note)

    note = Note(velocity=100, pitch=note_num, start=0, end=duration)
    instrument.notes.append(note)
    if (stim):
        stim_note = Note(velocity=120, pitch=116,start=0, end=duration)
        instrument.notes.append(stim_note)
        stim_temp = 1
        stim_note = 0

    pm.instruments.append(instrument)

    note_freq = note_utils.midi_to_freq(note_num)
    
    i = 0
    for note_num in out_chord:
        chord_note_freq[i] = note_utils.midi_to_freq(note_num)
        i += 1
    
    chord_wave = (1/4)*sum(np.sin(2 * np.pi * f * t) for f in chord_note_freq)
    note_wave = 1.5*(np.sin(2*np.pi*note_freq*t))
    return chord_wave + note_wave, stim_temp, stim

        


    
    


