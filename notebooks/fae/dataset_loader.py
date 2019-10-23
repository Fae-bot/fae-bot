# 2019-10-19, Loads the 2019-10-18 dataset into ndarrays

import os
import numpy as np

# State machine:
# 0: skip everything until a "f -1 ..." line happens, which means a new record session is happening and the timestamps are being reset
# 1: wait until the positions returned by "f ..." change. It takes me typically a few seconds to set artoolkit and to start the random sequence
# 2: use the data

def parse_file(f):
    #print(f)
    state = 0
    ticks = list()
    poses = list()
    for l in open(f).read().split("\n"):
        arr=l.rstrip(" ").split(" ")
        if len(arr)>2:
            if state == 0:
                if arr[0]=="f" and arr[1]=="-1":
                    old_ticks = " ".join(arr[2:])
                    state = 1
            if state == 1:
                if arr[0]=="f" and " ".join(arr[2:]) != old_ticks:
                    state = 2
            if state == 2:
                if arr[0]=="f":
                    ticks.append([float(arr[1])]+[int(x) for x in arr[2:]])
                if arr[0]=="p":
                    poses.append([float(x) for x in arr[1:]])
    return ticks, poses

# Now we have ticks and poses, with aligned timestamps, we can create data points which will comprise 
# two poses and a delta of ticks.
# A few things I know from how the data is generate:
# - it is guaranteed that each "f" line will have a "p" line with the exact same timestamp
# - movements were generated as 3 seconds straight movements
# - There were all kind of oscillations and imperfections in the movements so I am expecting +/- 15° error in the
#   orientation and mayb +/- 5 cm in the position
# - As a consequence, I think pairs that are a long time (and distance) apart bring more information than pairs 
#   that are close

def create_training_pairs(ticks, poses):
    # match ticks and poses of same timestamp:
    t_ts=dict()
    p_ts=dict()
    for t in ticks:
        t_ts[t[0]] = t[1:]
    for p in poses:
        p_ts[p[0]] = p[1:]
    fullposes=list()
    for ts in t_ts.keys():
        if ts in p_ts:
            fullposes.append([ts]+t_ts[ts]+p_ts[ts])
            
    # Now we make pairs of decreasing length until we arrive at 3 sec of timestamp delta
    start_ind = 0
    end_ind = len(fullposes)-1
    pairs=list()
    while(fullposes[end_ind][0]-fullposes[start_ind][0]>3.0):
        delta_ticks = [fullposes[end_ind][i]-fullposes[start_ind][i] for i in range(1,5)]
        pairs.append(fullposes[start_ind][5:] + delta_ticks + fullposes[end_ind][5:])
        start_ind+=1
        end_ind-=1
    # Note: it is possible to generate MUCH MORE pairs from these data.
    # update 2019-10-21: Is it? Let's do it!
    #
    # Let's make pairs over a 3 seconds window:
    start_ind = 0
    end_ind = 1
    while fullposes[end_ind][0]-fullposes[start_ind][0]<3.0 and end_ind<len(fullposes)-1:
        end_ind+=1
    while end_ind<len(fullposes)-1:
        delta_ticks = [fullposes[end_ind][i]-fullposes[start_ind][i] for i in range(1,5)]
        pairs.append(fullposes[start_ind][5:] + delta_ticks + fullposes[end_ind][5:])
        start_ind+=1
        end_ind+=1
    
    # Let's make pairs over a 6 seconds window:
    start_ind = 0
    end_ind = 1
    while fullposes[end_ind][0]-fullposes[start_ind][0]<6.0 and end_ind<len(fullposes)-1:
        end_ind+=1
    while end_ind<len(fullposes)-1:
        delta_ticks = [fullposes[end_ind][i]-fullposes[start_ind][i] for i in range(1,5)]
        pairs.append(fullposes[start_ind][5:] + delta_ticks + fullposes[end_ind][5:])
        start_ind+=1
        end_ind+=1
    
    # Let's make pairs over a 9 seconds window:
    start_ind = 0
    end_ind = 1
    while fullposes[end_ind][0]-fullposes[start_ind][0]<6.0 and end_ind<len(fullposes)-1:
        end_ind+=1
    while end_ind<len(fullposes)-1:
        delta_ticks = [fullposes[end_ind][i]-fullposes[start_ind][i] for i in range(1,5)]
        pairs.append(fullposes[start_ind][5:] + delta_ticks + fullposes[end_ind][5:])
        start_ind+=1
        end_ind+=1
    
    # Let's make pairs over a 12 seconds window:
    start_ind = 0
    end_ind = 1
    while fullposes[end_ind][0]-fullposes[start_ind][0]<6.0 and end_ind<len(fullposes)-1:
        end_ind+=1
    while end_ind<len(fullposes)-1:
        delta_ticks = [fullposes[end_ind][i]-fullposes[start_ind][i] for i in range(1,5)]
        pairs.append(fullposes[start_ind][5:] + delta_ticks + fullposes[end_ind][5:])
        start_ind+=1
        end_ind+=1
    

    return pairs

def normalize_columns(arr, cols=[]):
    norm_factors=list()
    for c in cols:
        v = arr[:, c]
        offset = v.min()
        scale = v.max() - v.min()
        arr[:, c] = (v - v.min()) / (v.max() - v.min())
        norm_factors.append((c, offset, scale))
    return norm_factors

def load_dataset(dirname):
    pairs = list()
    for f in os.listdir(dirname):
        t,p = parse_file(dirname+f)
        pairs += create_training_pairs(t,p)
    src_poses = np.array(pairs)[...,0:7]
    delta_ticks = np.array(pairs)[...,7:11]
    dst_poses = np.array(pairs)[...,11:]

    # mp_ = Motors Prediction model
    # pp_ = Position Prediction model

    pp_input = np.concatenate((src_poses, delta_ticks), axis=1)
    pp_output = np.array(dst_poses)

    mp_input = np.concatenate((src_poses, dst_poses), axis=1)
    mp_output = np.array(delta_ticks)
    
    normalize_columns(pp_input, [4,5,6,7,8,9,10])
    normalize_columns(pp_output, [4,5,6])
    normalize_columns(mp_input, [4,5,6,11,12,13])
    normalize_columns(mp_output, [0,1,2,3])
    
    return(pp_input, pp_output, mp_input, mp_output)

