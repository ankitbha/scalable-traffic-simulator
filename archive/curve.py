import numpy as np
import math

def get_traffic_curve():
    speed_lim = []
    for i in range(0,22):
        b = i/100
        s = 9.9
        c = (b*s)/4
        speed_lim.append([b,c,s])

    lookup = []
    for i in range(54,100):
        s = i/10
        b = 4.0/(4.0+0.675*s+0.076*(s**2))
        c = s/(4.0+0.675*s+0.076*(s**2))
        lookup.append([b,c,s])
    lookup = lookup[::-1]

    lookup = speed_lim + lookup

    for i in range(41,76):
        b = i/100
        c = 0.54*math.exp(-(b-0.40)*6.799)
        s = (4*c)/b
        lookup.append([b,c,s])

    for i in range(76,101):
        b = i/100
        c = 0.05
        s = 0.27
        lookup.append([b,c,s])

    lookup = np.array(lookup)

    curve = []
    for i in range(0,101):
        l = i/100
        row = lookup[(lookup[:,0]>=l) & (lookup[:,0]<l+0.01)].mean(axis=0).tolist()
        row[0] = l
        row[1] = round(row[1],2)
        row[2] = round(row[2],2)
        curve.append(row)

    curve = np.array(curve)
    
    return(curve)