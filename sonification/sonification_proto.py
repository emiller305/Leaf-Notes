# Sonification script using data processed
import time
import midiutil
import pandas as pd
import numpy as np
from midiutil import MIDIFile
from mingus.core import chords
import matplotlib.pyplot as plt
from collections import deque

NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
RUNNING_AVG = 0

track = 0
channel = 0
time = 0
duration = 1
tempo = 240 # rep. bpm or notes/min
volume = 100

CHORD_BOOK = {'pos_1': [],
              'neg_1': [],
              'pos_2': [],
              'neg_2': [],
              'pos_3': [],
              'neg_3': [],
              'pos_4': [],
              'neg_4': []}
NOTE_BOOK = {'pos_1': [],
              'neg_1': [],
              'pos_2': [],
              'neg_2': [],
              'pos_3': [],
              'neg_3': [],
              'pos_4': [],
              'neg_4': []}

# small window: 2 sec, fs = 64: 128 frames; lg win = 640 frames
fs = 64

var_hist = []
avg_hist = []

sm_frame_sz = .25 # 2 sec long
lg_frame_sz = 10 # 10 sec long
change_chord = 0


sm_win = deque(maxsize=fs*sm_frame_sz)
prev_win = deque(maxsize=fs*sm_frame_sz)
lg_win = deque(maxsize=fs*lg_frame_sz)

# import data - [TO IMPLEMENT]
# set prev = curr
# set curr = imported

while(1): # placeholder for actual loop
    # adjust window (roll)
    prev_win.append(sm_win)
    sm_win.append([data]) # append data pt to small
    #lg_win.append() # append data pt to lg


    ###### WAIT UNTIL DEQUE FULL ###
    if (len(sm_win) != fs*sm_frame_sz):
        time.sleep(1/fs) # may need to push delay
        continue
    
    # need to only do this after every chord plays - lg win
    # if (change_chord):
    #     chord_key = z_score(lg_win, l_std, l_avg)
    #     next_chor_set = CHORD_BOOK[chord_key]

    # map small note (# small_note)
    (s_avg, s_std) = stats(sm_win)
    note_key = z_score(sm_win, s_std, s_avg)
    scale_change = f_test(sm_win, prev_win)

    out_note = NOTE_BOOK[note_key[scale_change]]

    # output midi:
    outM = MIDIFile(2, deinterleave=False)
    outM.addTempo(track, time, tempo)

    # need to convert note -> #
    note_num = note_to_number(out_note, OCTAVE)
    outM.play_note(note_num, 0, time, tempo, channel, duration, volume)

    # end: pop first entry off deque
    sm_win.popleft()
    lg_win.popleft()
    change_chord += 1
    time += 1















# code graveyard
    # ## Ok tbh I'm thinking I want to do this based on z-score instead of gradient, leav
    # # check gradient in small frame
    # prev_sm_grad = curr_sm_grad
    # curr_sm_grad = grad(sm_win, time_step)

    # # check gradient in large frame
    # prev_lg_grad = curr_lg_grad
    # curr_lg_grad = grad(lg_win, time_step)
    # (l_avg, l_std) = stats(lg_win)
