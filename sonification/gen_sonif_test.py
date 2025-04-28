from midiutil import MIDIFile
import numpy as np
import random
from collections import deque
from scipy.stats import bartlett
import process

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

NOTE_BOOK = {
    'pos_1': ['F#'], 'neg_1': ['F'],
    'pos_2': ['G'],  'neg_2': ['E'],
    'pos_3': ['A'],  'neg_3': ['D'],
    'pos_4': ['B'],  'neg_4': ['C']
}

OCTAVE = 5
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FREQS = {
    'C': 523.25, 'D': 587.33, 'E': 659.26, 'F': 698.46,
    'B': 987.77, 'A': 880.00, 'G': 783.99, 'F#': 739.99
}


def note_to_number(note, octave):
    note = NOTES.index(note)
    return note + (octave * 12)


def create_music_arr(frames, duration, sample_rate, prev_freq, phase, phase_C, phase_E, amplitude, prev_win):
    bpm = 60/duration
    num_samples = int(sample_rate * duration)
    fs = 64
    sm_frame_sz = 0.25
    lg_frame_sz = 10
    
    NOTE_BOOK = {'pos_1': ['F#', 'F#'], 'neg_1': ['F', 'F'],
              'pos_2': ['G', 'G'], 'neg_2': ['E', 'E'],
              'pos_3': ['A', 'A'], 'neg_3': ['D', 'D'],
              'pos_4': ['B', 'B'], 'neg_4': ['C', 'C']}

    # OCTAVE = 5
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    FREQS = {
        'C': 523.25, 'D': 587.33, 'E': 659.26, 'F': 698.46,
        'B': 987.77, 'A': 880.00, 'G': 783.99, 'F#': 739.99
    }

    sm_win = deque(maxlen=int(fs * sm_frame_sz))
    #prev_win = deque(maxlen=int(fs * sm_frame_sz))
    lg_win = deque(maxlen=int(fs * lg_frame_sz))
    wave_out = np.array([])
    
    for val in frames:
        #if len(sm_win) == sm_win.maxlen:
            #prev_win = deque(sm_win, maxlen=sm_win.maxlen)
        sm_win.append(val)

        # Only act once sm_win is filled
        if len(sm_win) == sm_win.maxlen:
            avg = np.mean(sm_win)
            std = np.std(sm_win)
            z = (sm_win[-1] - avg) / std if std != 0 else 0
            abs_z = abs(z)

            if abs_z < 1:
                note_key = 'pos_1' if z > 0 else 'neg_1'
            elif abs_z < 2:
                note_key = 'pos_2' if z > 0 else 'neg_2'
            elif abs_z < 3:
                note_key = 'pos_3' if z > 0 else 'neg_3'
            else:
                note_key = 'pos_4' if z > 0 else 'neg_4'

            # Default scale change
            scale_change = 0
            if prev_win != None:
                scale_change = process.lev_test(sm_win, prev_win)
            if (scale_change):
                OCTAVE = 4
            else:
                OCTAVE = 5

            out_note = NOTE_BOOK[note_key][scale_change]
            note_num = note_to_number(out_note, OCTAVE)
            frequency = 440.0 * (2 ** ((note_num - 69) / 12.0))
            
            note_num_chord1 = note_to_number('C', 6)
            note_num_chord2 = note_to_number('E', 6)
            freq_chord1 = 440.0 * (2 ** ((note_num_chord1 - 69) / 12.0))
            freq_chord2 = 440.0 * (2 ** ((note_num_chord2 - 69) / 12.0))

            duration = 60 / bpm
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            #waveform_single = 0.5 * np.sin(2 * np.pi * frequency * t)

            
            # Smooth frequency transitions
            glide_time_ms = 2  # Very short smoothing (e.g. 2 ms)
            glide_samples = int(sample_rate * glide_time_ms / 1000)
            glide_samples = min(glide_samples, num_samples)  # safety

            hold_samples = num_samples - glide_samples

            # Smooth just the beginning of the transition
            freqs = np.concatenate([
                np.linspace(prev_freq, frequency, glide_samples),
                np.full(hold_samples, frequency)
            ])

            # Generate phase increments
            phase_increments = 2 * np.pi * freqs / sample_rate
            phase_array = np.cumsum(phase_increments) + phase
            sine_wave_single = amplitude * np.sin(phase_array)
            phase = phase_array[-1] % (2 * np.pi)
            wave_out_single_note = sine_wave_single.astype(np.float32)
            
            # Adding chord note 1
            #t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Smooth just the beginning of the transition
            freqs_C = np.concatenate([
                np.linspace(freq_chord1, freq_chord1, glide_samples),
                np.full(hold_samples, freq_chord1)
            ])

            # Generate phase increments
            phase_increments_C = 2 * np.pi * freqs_C / sample_rate
            phase_array_C = np.cumsum(phase_increments_C) + phase_C
            sine_wave_C = amplitude * np.sin(phase_array_C)
            
            # Adding chord note 2
            # Smooth just the beginning of the transition
            freqs_E = np.concatenate([
                np.linspace(freq_chord2, freq_chord2, glide_samples),
                np.full(hold_samples, freq_chord2)
            ])

            # Generate phase increments
            phase_increments_E = 2 * np.pi * freqs_E / sample_rate
            phase_array_E = np.cumsum(phase_increments_E) + phase_E
            sine_wave_E = amplitude * np.sin(phase_array_E)
            
            # Adding chord notes together
            sine_wave_chord = (sine_wave_C + sine_wave_E)/2
            wave_out_chord = sine_wave_chord.astype(np.float32)
            
            # Increment the phase for next frame
            phase_C = phase_array_C[-1] % (2 * np.pi)
            phase_E = phase_array_E[-1] % (2 * np.pi)
            
            # Adding chord and note??
            wave_out_total = (sine_wave_single + sine_wave_chord).astype(np.float32)
            
            # Only generate once
            break

    return wave_out_total, frequency, phase, phase_E, phase_C, sm_win
