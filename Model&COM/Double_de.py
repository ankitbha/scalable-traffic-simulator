import win32com.client
import time
import numpy as np

Vissim = win32com.client.gencache.EnsureDispatch("Vissim.Vissim.23")
print(Vissim)


filename = r"C:\Users\zj2187\Desktop\1r3\Double_our.inp0"
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\1r3\Double_our.layx"
Vissim.LoadLayout(Filename)

# simulation time
End_of_simulation = 150000
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)

Random_Seed = 41
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)


B_star = 16 # critical density
c = 2 # safety constant
speed = 50
avg_speed = 50
length = 400 # length of incoming links
speed_min = 5 # minimum speed
speed_max = 50 # maximum speed
db = Vissim.Net.DrivingBehaviors
bd_l = [db.ItemByKey(106),db.ItemByKey(107)]
#bd_l[0].SetAttValue('W99cc1Distr',3)
#bd_l[1].SetAttValue('W99cc1Distr',3)
time = 0

link_lengths = {'1': 400, '2': 400, '3': 150, '4': 150}

# Function to get vehicles in range 300 meters
def get_vehicles_in_range(cur_Veh, link_lengths, range_meters=150):
    link = str(cur_Veh.AttValue('Lane'))
    if(len(lane)==3):
        current_link = link[0]
    current_position = cur_Veh.AttValue('Pos')
    vehicles_in_range = 0

    # Check vehicles on the current link
    for veh in Vissim.Net.Vehicles.GetAll():
        if str(veh.AttValue('Lane'))[0] == current_link:
            if abs(veh.AttValue('Pos') - current_position) <= range_meters:
                vehicles_in_range += 1

    # Check vehicles on the connected link if near link end
    if current_link in ['1', '2'] and current_position > link_lengths[current_link] - range_meters:
        connected_link = '3' if current_link == '1' else '4'
        for veh in Vissim.Net.Vehicles.GetAll():
            if str(veh.AttValue('Lane'))[0] == connected_link:
                if veh.AttValue('Pos') <= range_meters - (link_lengths[current_link] - current_position):
                    vehicles_in_range += 1

    return vehicles_in_range

for i in range(0,150000):
    All_Vehicles = Vissim.Net.Vehicles.GetAll()
    num_sdc = 0
    for cur_Veh in All_Vehicles:
        if(cur_Veh.AttValue('VehType')=="100"):
            num_sdc += 1
    if(len(All_Vehicles)>0):
        ratio = num_sdc/len(All_Vehicles)

    if(num_sdc==0): # if no cars come yet, we let it continous run
        Vissim.Simulation.RunSingleStep()
        time += 1
    else: # if there get cars, we control their speed
        for cur_Veh in All_Vehicles: # get buffer size for each link
            lane = str(cur_Veh.AttValue('Lane'))
            if(len(lane)==3):
                idx = int(lane[0])-1
                b[idx] += 1
        if b[0]+b[2]>=550/5 or b[1]+b[3]>=550/5:
            Break = 1
            print("MAX CAPACITY:",time/10)
            break

        for cur_Veh in All_Vehicles: # we only control the car in link 1-4 and let the output link 5 keep 120km/h
            lane = cur_Veh.AttValue('Lane')
            veh_Type = cur_Veh.AttValue('VehType')
            if(len(lane)==3):
                idx = int(lane[0])-1

            if((idx < len(a)) and (veh_Type=='100')):

                b = get_vehicles_in_range(cur_Veh, 400, range_meters=150)
                remain_cap = B_star - b - c
                fra_link = (5*avg_speed*(1000/3600))/length
                a = remain_cap /(fra_link *b) # calculate the 'a' (rate of changing speed)
                speed = a*speed
                if speed <= speed_min:
                    speed = speed_min
                if speed > speed_max: # set the maximum speed
                    speed = speed_max
                avg_speed = ratio*speed[k] + (1-ratio)*50


                cur_Veh.SetAttValue('DesSpeed', speed)
            else:
                cur_Veh.SetAttValue('DesSpeed', speed_max)
        
        for t in range(0,50):# 10 simulation steps = 1s. so we run 300 steps to simulate the 30s cycle
            Vissim.Simulation.RunSingleStep()
        time += 50

Vissim.Simulation.Stop()
