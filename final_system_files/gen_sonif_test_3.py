from midiutil import MIDIFile
import numpy as np
import random
from collections import deque
from scipy.stats import bartlett
import process
import note_utils

fs = 64
sm_frame_sz = 0.25
lg_frame_sz = 10

# F# = 739.99
# G = 783.99
# A = 880.00
# B = 987.77
# F = 698.46
# E = 659.26
# D = 587.33
# C = 523.25

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


def create_music_arr(data, duration, sample_rate, prev_freq, prev_chord_freqs, phase, chord_phases, amplitude, prev_win, chord_prog, change_chords, stim_temp, stim_note, avg):

    def rolling_avg(win1, prev_avg):
        output = np.mean((win1, prev_avg))
        return output
    sm_win = np.array(data)
    chord_note_freqs = []
    #print("sm_win: ", sm_win)
    #print("prev_win: ", prev_win)
    stim_temp = stim_note

    
    if len(prev_win) != 0:
        #new_avg = rolling_avg(sm_win, avg)
        scale_change = process.lev_test(sm_win, prev_win)
        #stim_note = process.pear_test(sm_win, prev_win)
        if scale_change == 1:
            chord_prog += 1
            if chord_prog == 2:
                scale_change = 2
            elif chord_prog > 2:
                change_chords += 1
                if (change_chords > 3):
                    change_chords = 0
    else:
        scale_change = 0
        #new_avg = np.mean(sm_win)
    
    (avg, std) = process.stats(sm_win)
    data_min = np.min(sm_win)   # range: data_min > 0.002 and data_min > 0.006
    data_max = np.max(sm_win)
    if (data_max < 0.002 and data_min > -0.012):
        note_key = process.z_score(sm_win, std, avg)
        out_note = NOTE_BOOK[change_chords][note_key][scale_change]
        note_num = note_utils.note_to_number(out_note, NOTE_OCTAVE)
        note_freq = note_utils.midi_to_freq(note_num)
        stim_note = 0
    else:
        stim_note = 1
        note_freq = 800
        

    out_chord = CHORD_BOOK[change_chords][scale_change]

    i = 0
    for note_num in out_chord:
        chord_note_freqs.append(note_utils.midi_to_freq(note_num))
        i += 1
    
    
    bpm = 60/duration
    num_samples = int(sample_rate * duration)
    sm_frame_sz = 0.5
    lg_frame_sz = 3

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
     
    # Smooth frequency transitions
    glide_time_ms = 2  # Very short smoothing (e.g. 2 ms)
    glide_samples = int(sample_rate * glide_time_ms / 1000)
    glide_samples = min(glide_samples, num_samples)  # safety
    hold_samples = num_samples - glide_samples

    # Smoothing - note freq
    freqs = np.concatenate([
        np.linspace(prev_freq, note_freq, glide_samples),
        np.full(hold_samples, note_freq)
    ])

    # Generate phase increments - note freq
    phase_increments = 2 * np.pi * freqs / sample_rate
    phase_array = np.cumsum(phase_increments) + phase
    single_note_wave = np.sin(phase_array)
    phase = phase_array[-1] % (2 * np.pi)
            
    
    # Adding chords
    
    chord_waves = []
    
    # Adding chord notes
    # Smoothing and phase - chord
    i = 0
    for c_freq in chord_note_freqs:
        freqs_chord = np.concatenate([
            np.linspace(prev_chord_freqs[i], c_freq, glide_samples),
            np.full(hold_samples, c_freq)
        ])

        # Generate phase increments
        phase_increments_ch = 2 * np.pi * freqs_chord / sample_rate
        phase_array_ch = np.cumsum(phase_increments_ch) + chord_phases[i]
        
        sine_wave_ch = np.sin(phase_array_ch)
        
        chord_phases[i] = phase_array_ch[-1] % (2*np.pi)
        chord_waves.append(sine_wave_ch)
        i += 1
    
    chord_waves = np.array(chord_waves)
    full_chord_wave = (np.sum(chord_waves, axis=0)) / 4 
            
    # Adding chord and note
    wave_out_total = (((single_note_wave + full_chord_wave).astype(np.float32))/2)*amplitude

    return wave_out_total, note_freq, chord_note_freqs, phase, chord_phases, sm_win, chord_prog, change_chords, stim_temp, stim_note, avg
