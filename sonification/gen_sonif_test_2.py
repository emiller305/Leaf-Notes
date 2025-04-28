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

NOTE_BOOK = {'pos_1': ['G', 'C', 'D'], 'neg_1': ['E', 'A', 'B'],
              'pos_2': ['A', 'E', 'F#'], 'neg_2': ['D', 'Bb', 'A'],
              'pos_3': ['C', 'D','E'], 'neg_3': ['C', 'G', 'E'],
              'pos_4': ['B', 'F', 'G'], 'neg_4': ['F', 'F', 'Gb']}
CHORD_BOOK = [[60,64,67,72], # C-major 3 midi nums
               [65,69,72,76], # Fmajor 3 midi nums
               [67,71,74,78]] # G major 3 midi nums

NOTE_OCTAVE = 5
CHORD_OCTAVE = 3


FREQS = {
    'C': 523.25, 'D': 587.33, 'E': 659.26, 'F': 698.46,
    'B': 987.77, 'A': 880.00, 'G': 783.99, 'F#': 739.99
}


def create_music_arr(data, duration, sample_rate, prev_freq, prev_chord_freqs, phase, chord_phases, amplitude, prev_win, chord_prog, change_chords):
    
    sm_win = data
    chord_note_freqs = []
    
    (avg, std) = process.stats(sm_win)
    note_key = process.z_score(sm_win, std, avg)
    if len(prev_win) != 0:
        scale_change = process.lev_test(sm_win, prev_win)
        if scale_change == 1:
            chord_prog += 1
            if chord_prog == 2:
                scale_change = 2
            elif chord_prog > 2:
                chord_prog = 0
                change_chords += 1
                if (change_chords > 3):
                    change_chords = 0
    else:
        scale_change = 0

    out_note = NOTE_BOOK[note_key][scale_change]
    out_chord = CHORD_BOOK[scale_change]
    note_num = note_utils.note_to_number(out_note, NOTE_OCTAVE)
    
    note_freq = note_utils.midi_to_freq(note_num)
    
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

    return wave_out_total, note_freq, chord_note_freqs, phase, chord_phases, sm_win, chord_prog, change_chords
