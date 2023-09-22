import win32com.client
import time
import numpy as np

Vissim = win32com.client.gencache.EnsureDispatch("Vissim.Vissim.23")
print(Vissim)


filename = r"C:\Users\zj2187\Desktop\9.11\no1_inc.inp0"
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\9.11\no1_inc.layx"
Vissim.LoadLayout(Filename)

# simulation time
End_of_simulation = 30000
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)

Random_Seed = 42
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)


B_star = [15,15] # critical density
c = 2 # safety constant
speed = [50,50]
avg_speed = [50,50]
length = 400 # length of incoming links
speed_min = 5 # minimum speed
speed_max = 50 # maximum speed
db = Vissim.Net.DrivingBehaviors
bd_l = [db.ItemByKey(106),db.ItemByKey(107)]
time = 0


for i in range(0,30000):
    All_Vehicles = Vissim.Net.Vehicles.GetAll()
    num_sdc = 0
    for cur_Veh in All_Vehicles:
        if(cur_Veh.AttValue('VehType')=="100"):
            num_sdc += 1
    if(len(All_Vehicles)>0):
        ratio = num_sdc/len(All_Vehicles)
    b = np.zeros(5, dtype=float)
    a = np.ones(2, dtype=float)
    if(num_sdc==0): # if no cars come yet, we let it continous run
        Vissim.Simulation.RunSingleStep()
        time += 1
        print("No control car")
    else: # if there get cars, we control their speed
        for cur_Veh in All_Vehicles: # get buffer size for each link
            lane = str(cur_Veh.AttValue('Lane'))
            if(len(lane)==3):
                idx = int(lane[0])-1
                b[idx] += 1
        if b[0]+b[2]>=550/8 or b[1]+b[3]>=550/8:
            Break = 1
            print("MAX CAPACITY:",time/10)
            break
        for k in range(0,len(a)):
            remain_cap = B_star[k] - b[k+2] - c
            fra_link = (5*avg_speed[k]*(1000/3600))/length
            a[k] = remain_cap /(fra_link *b[k]) # calculate the 'a' (rate of changing speed)
            speed[k] = a[k]*speed[k]
            if speed[k] <= speed_min:
                speed[k] = speed_min
            if speed[k] > speed_max: # set the maximum speed
                speed[k] = speed_max
            avg_speed[k] = ratio*speed[k] + (1-ratio)*50

        for cur_Veh in All_Vehicles: # we only control the car in link 1-4 and let the output link 5 keep 120km/h
            lane = cur_Veh.AttValue('Lane')
            veh_Type = cur_Veh.AttValue('VehType')
            if(len(lane)==3):
                idx = int(lane[0])-1
            if((idx < len(a)) and (veh_Type=='100')):
                cur_Veh.SetAttValue('DesSpeed', speed[idx])
            else:
                cur_Veh.SetAttValue('DesSpeed', speed_max)
        
        for t in range(0,50):# 10 simulation steps = 1s. so we run 300 steps to simulate the 30s cycle
            print(i,":",t)
            Vissim.Simulation.RunSingleStep()
        time += 50

Vissim.Simulation.Stop()
