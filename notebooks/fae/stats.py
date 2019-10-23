from os import listdir

def read_file(fn):
    datapoints = list()
    lastp = lastm = None
    for l in open(fn):
        arr = l.split(" ")
        ctime = float(arr[1])
        if ctime == -1:
            continue
        if arr[0] == "p":
            lastp = arr
        if arr[0] == "m":
            lastm = arr
        if lastm and lastp and abs(float(lastm[1])-float(lastp[1]))<0.03:
            datapoints.append([float(x) for x in lastp[1:]+lastm[2:]])
    return datapoints

dp = list()
for fn in listdir("raw/good"):
    ffn="raw/good/"+fn
    print(ffn)
    stats(read_file(ffn))
for fn in listdir("raw/manual/"):
    ffn="raw/manual/"+fn
    print(ffn)
    stats(read_file(ffn))

def stats(datapoints):
    zcount = 0
    onecount = 0
    seqnum = 0
    lasttime=dp[0][0]
    for d in dp:
        #print(d)
        zzc=0
        #print(d[0]-lasttime, seqnum)
        if d[0]-lasttime>0.3:
            print("seq "+str(seqnum))
            seqnum=0
        else:
            seqnum+=1
        lasttime = d[0]
        for dd in d[8:12]:
            if dd==0:
                zzc+=1
        if zzc==4:
            zcount+=1
        if zzc==3:
            onecount+=1

    print(len(dp))
    print(zcount)
    print(onecount)

"""inputs=list()
outputs=list()
for i,d in enumerate(datapoints[1:]):
    if abs(d[0]-datapoints[i-1][0] - 0.2)<0.05:
        inputs.append(datapoints[i-1][1:])
        # transform outputs into deltas
        outputs.append([result-start for (result, start) in zip(d[1:8],datapoints[i-1][1:8])])

outputs = np.array(outputs)
inputs = np.array(inputs)
"""
