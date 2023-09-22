#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      zj2187
#
# Created:     19/08/2023
# Copyright:   (c) zj2187 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#0.导入库（具体这个库参考其他资料）
import win32com.client #主要库
import time #不重要
import numpy as np

#1.连接VISSIM并创建VISSIM对象
Vissim = win32com.client.gencache.EnsureDispatch("Vissim.Vissim.23") #最后数字为版本号
print(Vissim)

#2.加载路网(我们在绘制路网的时候通常会导入一张背景图，然后在上面绘制，注意这里仅加载路网不加载背景图)
filename = r"C:\Users\zj2187\Desktop\9.11\Double_sig1_test.inpx" #好像不能用相对路径
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\9.11\Double_sig1_test.layx"
Vissim.LoadLayout(Filename)

#3.仿真参数设置
End_of_simulation = 3000 # simulation second [s]
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)
Random_Seed = 41
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)
step_time = 1
Vissim.Simulation.SetAttValue('SimRes', step_time)
# Set the state of a signal controller:
# Note: Once a state of a signal group is set, the attribute "ContrByCOM" is automatically set to True. Meaning the signal group will keep this state until another state is set by COM or the end of the simulation
# To switch back to the defined signal controller, set the attribute signal "ContrByCOM" to False (example see below).
for i in range(5):
    Vissim.Simulation.RunSingleStep()
    t = Vissim.Simulation.AttValue('SimSec')

time.sleep(5)

SC_number = 1 # SC = SignalController
SG_number = 1 # SG = SignalGroup
SignalController = Vissim.Net.SignalControllers.ItemByKey(SC_number)
SignalGroup = SignalController.SGs.ItemByKey(SG_number)

'''
SCATS: minimize maximum degree of saturation of all links
DS definition for SCATS = used green time / available green time
variation of each stage length by +- 4% using the ratios of DS with cycle length
'''
SH_numbers = [1,2]
total_cycle = 120
act_stage_lengths = [total_cycle/2 for i in range(len(SH_numbers))]
calc_stage_lengths = [total_cycle/2 for i in range(len(SH_numbers))]


# Note: The signal controller can only be called at whole simulation seconds, so the state will be set in Vissim at the next whole simulation second, here 199s
# Simulate so that the new state is active in the Vissim simulation:
Sim_end = 3000 # simulation second [s]
Sim_start = time.time() # simulation second [s]
Vissim.Simulation.SetAttValue("SimBreakAt", Sim_end)

degree_saturation = [0.5, 0.5]
SignalGroup.SetAttValue("ContrByCOM", True) 
while time.time() - Sim_start < Sim_end:
    # Cycle level
    print("cycle level", Vissim.Simulation.AttValue('SimSec'))
    All_Vehicles = Vissim.Net.Vehicles.GetAll()
    b = np.zeros(5, dtype=float)
    if len(All_Vehicles) == 0: # if no cars come yet, we let it continous run
        Vissim.Simulation.RunSingleStep()
        print("No car")
    else: # if there get cars, we control their speed
        for cur_Veh in All_Vehicles: # get buffer size for each link
            lane = str(cur_Veh.AttValue('Lane'))
            if(len(lane)==3):
                idx = int(lane[0])-1
                b[idx] += 1
        if b[0]+b[2]>=550/4 or b[1]+b[3]>=550/4:
            Break = 1
            print("MAX CAPACITY:",time.time())
            break
    # If all equal, no change
    equal = True
    for s in degree_saturation:
        if s != degree_saturation[0]:
            equal = False
            break
    
    # else for higher degree increment time, for lower degree decrement
    if not equal:
        saturation = list(zip(range(2), degree_saturation))
        sorted_saturation = sorted(saturation, key= lambda item : item[1])
        act_stage_lengths[sorted_saturation[0][0]] = calc_stage_lengths[sorted_saturation[0][0]] - 4
        calc_stage_lengths[sorted_saturation[0][0]] -= 1
        act_stage_lengths[sorted_saturation[-1][0]] = calc_stage_lengths[sorted_saturation[0][0]] + 4
        calc_stage_lengths[sorted_saturation[-1][0]] += 1

        print("sat", degree_saturation)

    for i in range(len(SH_numbers)):
        # Stage level
        print("stage level", Vissim.Simulation.AttValue('SimSec'), SH_numbers[i], calc_stage_lengths[i])
       
        # Enable stage by activating signal and deactivating all others
        for j in range(len(SH_numbers)):
            SignalGroup = SignalController.SGs.ItemByKey(SH_numbers[j])
            if j == i:
                SignalGroup.SetAttValue("SigState", "GREEN")
            else:
                SignalGroup.SetAttValue("SigState", "RED")
        
        # Calculate used green time and discharge rate
        All_Vehicles = Vissim.Net.Vehicles.GetAll()
        vehicles_in_lane = [veh for veh in All_Vehicles if veh.AttValue('Lane') == f"{i+1}-1"]
        stage_start_time = time.time()

        available_green_time = act_stage_lengths[i]
        used_green_time = act_stage_lengths[i]
        cars_exited = 0
        
        Vissim.Simulation.RunSingleStep()    

        for t in range(int(act_stage_lengths[i])):
            New_All_Vehicles = Vissim.Net.Vehicles.GetAll()
            new_vehicles_in_lane = [veh for veh in New_All_Vehicles if veh.AttValue('Lane') == f"{i+1}-1"]

            car_exited = False
            for veh in vehicles_in_lane:                
                car_present = False
                for out_veh in new_vehicles_in_lane:
                    if veh.AttValue('No') == out_veh.AttValue('No'):
                        car_present = True
                if not car_present:
                    cars_exited += 1
                    car_exited = True

            if not car_exited:
                used_green_time -= 1
            
            vehicles_in_lane = [veh for veh in New_All_Vehicles if veh.AttValue('Lane') == f"{i+1}-1"]
            
            Vissim.Simulation.RunSingleStep()    

        discharge_rate = cars_exited / act_stage_lengths[i] 
        if (discharge_rate * used_green_time) != 0:
            degree_saturation[i] = len(vehicles_in_lane)  / (discharge_rate * used_green_time) 
        else:
            degree_saturation[i] = 0

Vissim.Simulation.Stop()
# Give the control back:
SignalGroup.SetAttValue("ContrByCOM", False) 
 
