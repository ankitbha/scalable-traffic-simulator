import queue
import numpy as np
import math
import matplotlib.pyplot as plt
import random
random.seed(10)


class simulator:
    def __init__(self, edges, lengths, input_edges, next_edge, merges, curve):
        self.edges = edges
        self.lengths = lengths
        self.input_edges = input_edges
        self.next_edge = next_edge
        self.curve = curve
        self.merges = merges
        self.time = 0
        self.throughput = []
        self.buffers = {}
        self.edge_inputs = {}
        self.edge_outputs = {}
        self.eligible = {}
        for edge in self.edges:
            self.buffers[edge] = queue.Queue(int(self.lengths[edge]/4))
            self.edge_inputs[edge] = 0
            self.edge_outputs[edge] = 0
            self.eligible[edge] = 0
    
    def iteration_nosignal(self,input_rate):
        self.time = self.time + 1
        for edge in self.edges:
            for i in range(self.buffers[edge].qsize()):
                if(self.buffers[edge].qsize()):
                    if(self.buffers[edge].queue[i][1]>self.time):
                        self.eligible[edge] = i
                        break
            b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
            if(self.eligible[edge]):
                self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]
                if(self.edge_outputs[edge]>=1):
                    _ = self.buffers[edge].get()
                    self.edge_outputs[edge] -= 1
                    next_edge = random.choice(self.next_edge[edge])
                    if(next_edge is not None):
                        b_next = self.buffers[next_edge].qsize()/(self.lengths[next_edge]/4)
                        self.buffers[next_edge].put((self.time,self.time+(self.lengths[next_edge]/self.curve[self.curve[:,0]==b_next][0][2])),\
                                                   timeout=0.1)
                    else:
                        self.throughput.append(self.time)
            if edge in self.input_edges:
                self.edge_inputs[edge] += input_rate[edge]
                if(self.edge_inputs[edge]>=1):
                    self.buffers[edge].put((self.time,self.time+(self.lengths[edge]/self.curve[self.curve[:,0]==b][0][2])), timeout=0.1)
                    self.edge_inputs[edge] -= 1    
    
    def iter_merge_equisignal(self,in_edges,out_edge):
        schedule = {i:in_edges[i] for i in range(len(in_edges))}
        for edge in in_edges+[out_edge]:
            b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
            scheduled_edge = schedule[(self.time//30)%len(in_edges)]
            if(self.eligible[edge]):
                if(edge in in_edges):
                    if(edge==scheduled_edge):
                        self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]
                        if(self.edge_outputs[edge]>=1):
                            _ = self.buffers[edge].get()
                            self.edge_outputs[edge] -= 1
                            b_out = self.buffers[out_edge].qsize()/(self.lengths[out_edge]/4)
                            self.buffers[out_edge].put((self.time,self.time+(self.lengths[out_edge]/self.curve[self.curve[:,0]==b_out][0][2])),\
                                                       timeout=0.1)
                else:
                    
                    self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]
                    if(self.edge_outputs[edge]>=1):
                        _ = self.buffers[edge].get()
                        self.edge_outputs[edge] -= 1
                        next_edge = random.choice(self.next_edge[edge])
                        if(next_edge is not None):
                            b_next = self.buffers[next_edge].qsize()/(self.lengths[next_edge]/4)
                            self.buffers[next_edge].put((self.time,self.time+(self.lengths[next_edge]/self.curve[self.curve[:,0]==b_next][0][2])),\
                                                       timeout=0.1)
                        else:
                            self.throughput.append(self.time)
    
    def iteration_equisignal(self,input_rate):
        self.time = self.time + 1
        for edge in self.edges:
            for i in range(self.buffers[edge].qsize()):
                if(self.buffers[edge].qsize()):
                    if(self.buffers[edge].queue[i][1]>self.time):
                        self.eligible[edge] = i
                        break
            b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
            if edge in self.input_edges:
                self.edge_inputs[edge] += input_rate[edge]
                if(self.edge_inputs[edge]>=1):
                    self.buffers[edge].put((self.time,self.time+(self.lengths[edge]/self.curve[self.curve[:,0]==b][0][2])), timeout=0.1)
                    self.edge_inputs[edge] -= 1
                    
        all_edges = set(self.edges)
        union_merge = set()
        for merge in self.merges:
            in_edges, out_edge = merge[0], merge[1]
            self.iter_merge_equisignal(in_edges,out_edge)
            union_merge = union_merge.union(set(in_edges))
            union_merge = union_merge.union({out_edge})
        rem_edges = all_edges - union_merge
        if(len(rem_edges)):
            for edge in rem_edges:
                b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
                if(self.eligible[edge]):
                    self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]
                    if(self.edge_outputs[edge]>=1):
                        _ = self.buffers[edge].get()
                        self.edge_outputs[edge] -= 1
                        next_edge = random.choice(self.next_edge[edge])
                        if(next_edge is not None):
                            b_next = self.buffers[next_edge].qsize()/(self.lengths[next_edge]/4)
                            self.buffers[next_edge].put((self.time,self.time+(self.lengths[next_edge]/self.curve[self.curve[:,0]==b_next][0][2])),\
                                                       timeout=0.1)
                        else:
                            self.throughput.append(self.time)
                    
    def iter_merge_self_regulate(self,in_edges,out_edge):
        for edge in in_edges+[out_edge]:
            if(edge not in in_edges):
                b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
                if(self.eligible[edge]):
                    self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]
                    if(self.edge_outputs[edge]>=1):
                        _ = self.buffers[edge].get()
                        self.edge_outputs[edge] -= 1
                        self.throughput.append(self.time)
            else:
                if(self.eligible[edge]):
                    b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
                    alpha = self.get_alpha(in_edges,out_edge)
                    self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]*min(1,alpha)
                    if(self.edge_outputs[edge]>=1):
                        _ = self.buffers[edge].get()
                        self.edge_outputs[edge] -= 1
                        next_edge = random.choice(self.next_edge[edge])
                        b_next = self.buffers[next_edge].qsize()/(self.lengths[next_edge]/4)
                        self.buffers[next_edge].put((self.time,self.time+(self.lengths[next_edge]/self.curve[self.curve[:,0]==b_next][0][2])),\
                                                   timeout=0.1)
    
    
    def iteration_self_regulate(self,input_rate):
        self.time += 1
        for edge in self.edges:
            for i in range(self.buffers[edge].qsize()):
                if(self.buffers[edge].qsize()):
                    if(self.buffers[edge].queue[i][1]>self.time):
                        self.eligible[edge] = i
                        break
            b = self.buffers[edge].qsize()/(self.lengths[edge]/4)                             
            if edge in self.input_edges:
                    self.edge_inputs[edge] += input_rate[edge]
                    if(self.edge_inputs[edge]>=1):
                        self.buffers[edge].put((self.time,self.time+(self.lengths[edge]/self.curve[self.curve[:,0]==b][0][2])), timeout=0.1)
                        self.edge_inputs[edge] -= 1    
                        
        all_edges = set(self.edges)
        union_merge = set()
        for merge in self.merges:
            in_edges, out_edge = merge[0], merge[1]
            self.iter_merge_self_regulate(in_edges,out_edge)
            union_merge = union_merge.union(set(in_edges))
            union_merge = union_merge.union({out_edge})
        rem_edges = all_edges - union_merge
        if(len(rem_edges)):
            for edge in rem_edges:
                b = self.buffers[edge].qsize()/(self.lengths[edge]/4)
                if(self.eligible[edge]):
                    self.edge_outputs[edge] += self.curve[self.curve[:,0]==b][0][1]
                    if(self.edge_outputs[edge]>=1):
                        _ = self.buffers[edge].get()
                        self.edge_outputs[edge] -= 1
                        next_edge = random.choice(self.next_edge[edge])
                        if(next_edge is not None):
                            b_next = self.buffers[next_edge].qsize()/(self.lengths[next_edge]/4)
                            self.buffers[next_edge].put((self.time,self.time+(self.lengths[next_edge]/self.curve[self.curve[:,0]==b_next][0][2])),\
                                                       timeout=0.1)
                        else:
                            self.throughput.append(self.time)
            
              
    def get_throughput(self):
        return(self.throughput)
    
    def get_alpha(self,in_edges,out_edge):
        b_lim = 0.33
        c_lim = self.curve[self.curve[:,0]==b_lim][0][1]
        b_out = self.buffers[out_edge].qsize()/(self.lengths[out_edge]/4)
        b_ratio = {}
        for edge in in_edges:
            b_ratio[edge] = (self.buffers[edge].qsize()/(self.lengths[edge]/4))
        factor = 1/sum(b_ratio.values())
        c_norm = {}
        for edge in in_edges:
            b_ratio[edge] = b_ratio[edge]*factor
            b = (self.buffers[edge].qsize()/(self.lengths[edge]/4))
            c = self.curve[self.curve[:,0]==b][0][1]
            c_norm[edge] = c*b_ratio[edge]
        
        if(sum(b_ratio.values())):
            if(b_lim-b_out>0):
                alpha = (b_lim-b_out+c_lim)/(sum(c_norm.values()))
            else:
                alpha=0
        else:
            alpha = 1        
        return(alpha)
    