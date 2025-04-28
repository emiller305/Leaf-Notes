import numpy as np
from scipy.stats import bartlett
from scipy.stats import levene
from scipy.stats import pearsonr
def stats(window):
    '''
    Finds mean + st. dev of window; returns in tuple
    '''
    avg = np.mean(window)
    stdev = np.std(window)

    return (avg, stdev)

def map_value(value, min, max, min_result, max_result):
    result = min_result + (value - min)/(max-min)*(max_result - min_result)
    return result

def f_test(win1, win2):
    '''
    Use f test to determine if stat. different 
    '''
    # 2 deg of freedom
    alpha = .05
    stat, p = bartlett(win1, win2)

    if (p < alpha):
        # no change in variance
        return 0
    # elif (p < .1):
    #     return 1
    else: 
        # change in variance
        return 1

def lev_test(win1, win2):
    stat, p = levene(win1, win2)
    
    alpha = .05

    if (p < alpha):
        # no change in variance
        return 0
    # elif (p < .1):
    #     return 1
    else: 
        
        # change in variance
        return 1
    
def pear_test(win1, win2):
    #print("win1: ,", win1)
    #print("win2: ,", win2)
    corr, _ = pearsonr(win1, win2)
    #print("corr: ", corr)
    if abs(corr) < .1:
        return 1
    else:
        return 0

def z_score(window, stdev, avg):
    '''
    Calculate z-score; return threshold key (corresponds to music)
    returns string with chord key
    '''
    z = (window[-1] - avg) / stdev 
    abs_z = np.abs(z)

    if (abs_z < .58823529411):
        # within one stdev
        if (z > 0): return 'pos_1'
        else: return 'neg_1'

    elif (abs_z >= .58823529411 and abs_z < 1):
        # within 2 stdev
        if (z > 0): return 'pos_2'
        else: return 'neg_2'

    elif (abs_z >= 1 and abs_z < 1.5):
        # within 3 stdev
        if (z > 0): return 'pos_3'
        else: return 'neg_3'

    else:
        # within 4 stdev
        if (z > 0): return 'pos_4'
        else: return 'neg_4'

def grad(window, time_step):
    grad = (window[-1] - window[0])/time_step
    return grad

