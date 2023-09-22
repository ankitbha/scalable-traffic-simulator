import win32com.client
import time
import numpy as np

Vissim = win32com.client.gencache.EnsureDispatch("Vissim.Vissim.23")
print(Vissim)


filename = r"C:\Users\zj2187\Desktop\9.11\no1_test.inp0"
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\9.11\no1_test.layx"
Vissim.LoadLayout(Filename)

# simulation time
End_of_simulation = 30000
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)

Random_Seed = 42
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)

db = Vissim.Net.DrivingBehaviors
bd_l = [db.ItemByKey(106),db.ItemByKey(107)]
time = 0
Green = [60,60]
Max = 90


for i in range(0,30000):
    All_Vehicles = Vissim.Net.Vehicles.GetAll()
    b = np.zeros(5, dtype=float)
    if len(All_Vehicles) == 0: # if no cars come yet, we let it continous run
        Vissim.Simulation.RunSingleStep()
        time += 1
        print("No car")
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
        p1 = b[0]+b[2]-b[4]
        p2 = b[1]+b[3]-b[4]
        Green[0] = 120*(p1/(p1+p2))
        Green[1] = 120*(p2/(p1+p2))
        if Green[0] >=90:
            Green = [90,30]
        if Green[1] >= 90:
            Green = [30, 90]
        
        if b[0]+b[2] > b[1]+b[3]:
            bd_l[0].SetAttValue('W99cc1Distr',3)
            bd_l[1].SetAttValue('W99cc1Distr',2)
        elif b[0]+b[2] < b[1]+b[3]:
            bd_l[0].SetAttValue('W99cc1Distr',2)
            bd_l[1].SetAttValue('W99cc1Distr',3)
        else:
            bd_l[0].SetAttValue('W99cc1Distr',3)
            bd_l[1].SetAttValue('W99cc1Distr',3)
            
        for t in range(int(Green[0])):
            All_Vehicles = Vissim.Net.Vehicles.GetAll()
            for cur_Veh in All_Vehicles:
                lane = cur_Veh.AttValue('Lane')
                if lane == "3-1" or lane == '10000-1':
                    cur_Veh.SetAttValue('DesSpeed', 50)
                elif lane == "4-1" or lane == '10004-1':
                    cur_Veh.SetAttValue('DesSpeed', 20)
                else:
                    cur_Veh.SetAttValue('DesSpeed', 50)
            Vissim.Simulation.RunSingleStep()
            time += 1
        for t in range(120-int(Green[0])):
            All_Vehicles = Vissim.Net.Vehicles.GetAll()
            for cur_Veh in All_Vehicles: # we only control the car in link 1-4 and let the output link 5 keep 120km/h
                lane = cur_Veh.AttValue('Lane')
                if lane == "3-1" or lane == '10000-1':
                    cur_Veh.SetAttValue('DesSpeed', 20)
                elif lane == "4-1" or lane == '10004-1':
                    cur_Veh.SetAttValue('DesSpeed', 50)
                else:
                    cur_Veh.SetAttValue('DesSpeed', 50)
            Vissim.Simulation.RunSingleStep()
            time += 1



Vissim.Simulation.Stop()
