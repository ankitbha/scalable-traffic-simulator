import queue
import numpy as np
import math
import matplotlib.pyplot as plt
import random
import sys
sys.path.append('./')
from simulator import simulator
from tqdm import tqdm
random.seed(10)
import matplotlib.image as mpimg


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


top_G = {'A':['D'],'B':['D'],'C':['D'],'D':['F'],'E':['F'], 'F':['H'], 'G':['H'], 'H':['J'], 'I':['J'], 'J':['K']}
edges = []
for key,val in top_G.items():
    for node in val:
        edges.append(key+node)

lengths = {i:200 for i in edges}

input_edges = ['AD', 'BD', 'CD', 'EF', 'GH', 'IJ']
for edge in input_edges:
    lengths[edge] = 100

next_edge = {'AD':['DF'], 'BD':['DF'], 'CD':['DF'], 'DF':['FH'], 'EF':['FH'], 'FH':['HJ'], 'GH':['HJ'], 'HJ':['JK'], 'IJ':['JK'], 'JK':[None]}

merges = [[['AD', 'BD', 'CD'], 'DF'],[['DF','EF'],'FH'],[['FH','GH'],'HJ'],[['HJ','IJ'],'JK']]

base_input_rate = {'AD':0.088, 'BD':0.088, 'CD':0.088, 'EF':0.088, 'GH':0.088, 'IJ':0.088}
v=0.19
burst_input_rate = {'AD':v, 'BD':v, 'CD':v, 'EF':v, 'GH':v, 'IJ':v}

i1, i2, i3 = 500, 500, 500
tot_i = i1+i2+i3


sign = {'no':'No Signaling', 'eq': 'Equal-Time Signaling', 'bp': 'Backpressure Signaling'}
num = 0

for signal in ['no', 'eq', 'bp']:
    S = simulator(edges, lengths, input_edges, next_edge, merges, curve)
    for k in tqdm(range(tot_i)):
        if(k<i1 or k>=i1+i2):
            input_rate = base_input_rate
        else:
            input_rate = burst_input_rate

        try:
            if(signal == 'bp'):
                S.iteration_self_regulate(input_rate)
            if(signal == 'no'):
                S.iteration_nosignal(input_rate)
            if(signal == 'eq'):
                S.iteration_eqsignal(input_rate)
                
            num+=1
            buff = {}
            for edge in list(S.buffers.keys()):
                buff[edge] = len(S.buffers[edge].queue)/(S.buffers[edge].maxsize*1.0)

            fig = plt.figure(layout='constrained', figsize=(10, 8))
            ax = fig.subplots(2, 2)

            ax_top = ax[0,0]
            img = mpimg.imread('topology.png')
            ax_top.imshow(img)
            ax_top.tick_params(which='both',bottom=False,left=False,top=False,right=False,labelbottom=False,labelleft=False)
            ax_top.set_title('Topology',size=18)

            ax_in = ax[0,1]
            x = list(input_rate.values())
            y = input_edges
            ax_in.bar(y,x,align='center',width=0.5)
            ax_in.axis(ymin=0,ymax=0.22)
            ax_in.set_xlabel('Input Edges', size=14)
            ax_in.set_ylabel('Input Rate (cars/sec)', size=14)
            ax_in.axhline(y=0.088,label='base rate',c='g')
            ax_in.axhline(y=0.19,label='burst rate',c='r')
            ax_in.legend()
            ax_in.set_title('Input Rates',size=18)

            ax_b = ax[1,0]       
            x = list(buff.values())
            y = edges
            ax_b.axis(xmin=0,xmax=1)
            ax_b.barh(y,x,align='center')
            ax_b.set_xlabel('Buffer Capacity',size=14)
            ax_b.set_ylabel('Edges',size=14)
            ax_b.axvline(x=0.33, label='b*')
            ax_b.legend()
            ax_b.set_title('Buffer Capacities',size=18)

            ax_c = ax[1,1]
            ax_c.plot(curve[:,0],curve[:,1],lw=2)
            ax_c.set_xlabel('Buffer Density',size=14)
            ax_c.set_ylabel('Exit Rate (#cars/second)',size=14)
            ax_c.set_title('Exit Rates',size=18)
            for edge in list(S.buffers.keys()):
                ax_c.scatter(buff[edge],curve[curve[:,0]==buff[edge]][0][1],label=edge)
            ax_c.legend()

            fig.suptitle(sign[signal]+' Time '+str(S.time)+' s',size=24)
            fig.savefig('images_for_video/{}.png'.format(num))
            plt.close(fig)
        except:
            break