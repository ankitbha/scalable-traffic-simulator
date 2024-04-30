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
import torch
import torch.nn as nn
import torch.optim as optim


FEEDBACK_STEP = 5 # seconds between each state snapshot

'''
boilerplate definition of NN
'''
device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {device} device")

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(10, 128),
            nn.ReLU(),
            nn.Linear(128, 16),
            nn.ReLU(),
            nn.Linear(16, 2),
        )
    
    def forward(self, x):
        x = nn.Flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

# features = []
# X = np.array(features) # density, 
# model = NeuralNetwork().to(device)
# print(model)


#1.连接VISSIM并创建VISSIM对象
Vissim = win32com.client.gencache.EnsureDispatch("Vissim.Vissim.23") #最后数字为版本号
print(Vissim)

#2.加载路网(我们在绘制路网的时候通常会导入一张背景图，然后在上面绘制，注意这里仅加载路网不加载背景图)
filename = r"C:\\Users\\ra3106\Desktop\\neurips24\\base case\\base.inpx" #好像不能用相对路径
Vissim.LoadNet(filename)
Filename = r"C:\\Users\\ra3106\Desktop\\neurips24\\base case\\base.layx"
Vissim.LoadLayout(Filename)

#3.仿真参数设置
End_of_simulation = 30 # simulation second [s]
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)
Random_Seed = 41
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)
step_time = 1
Vissim.Simulation.SetAttValue('SimRes', step_time)
# Set the state of a signal controller:
# Note: Once a state of a signal group is set, the attribute "ContrByCOM" is automatically set to True. Meaning the signal group will keep this state until another state is set by COM or the end of the simulation
# To switch back to the defined signal controller, set the attribute signal "ContrByCOM" to False (example see below).
# SC_number = 1 # SC = SignalController
# SG_number = 1 # SG = SignalGroup
# SignalController = Vissim.Net.SignalControllers.ItemByKey(SC_number)
# SignalGroup = SignalController.SGs.ItemByKey(SG_number)

# Note: The signal controller can only be called at whole simulation seconds, so the state will be set in Vissim at the next whole simulation second, here 199s
# Simulate so that the new state is active in the Vissim simulation:
Sim_start = time.time() # simulation second [s]
Vissim.Simulation.SetAttValue("SimBreakAt", End_of_simulation)

# exit()


data = {}
# for link in range(len(Vissim.Net.Links)):
#     link_obj = Vissim.Net.Links.ItemByKey(link)

#     data[link]["model"] = NeuralNetwork().to(device)
#     data[link]["length"] = link_obj.Length2D
#     data[link]["num_lanes"] = link_obj.NumLanes
#     data[link]["input_rate"] = 0
#     data[link]["exit_rate"] = 0

#     data[link]["next_link"] = link + 1 # 

# BASE CASE config
links = [7,12,11]
for i in range(len(links)):
    link_obj = Vissim.Net.Links.ItemByKey(links[i])

    data[links[i]] = {}
    data[links[i]]["model"] = NeuralNetwork().to(device)
    data[links[i]]["length"] = link_obj.AttValue('Length2D')
    data[links[i]]["num_lanes"] = link_obj.AttValue('NumLanes')
    data[links[i]]["density"] = 0
    data[links[i]]["density_prev"] = 0
    data[links[i]]["input_rate"] = 0
    data[links[i]]["exit_rate"] = 0
    data[links[i]]["all_vehicles"] = []
    data[links[i]]["prev_all_vehicles"] = []

    data[links[i]]["next_link"] = 0 # 
    if i < len(links) - 1:
        data[links[i]]["next_link"] = links[i + 1] # 


# print(data)

while Vissim.Simulation.AttValue('SimSec') < End_of_simulation - 1:
    print(Vissim.Simulation.AttValue('SimSec'))
    Vissim.Simulation.RunSingleStep()

    if Vissim.Simulation.AttValue('SimSec') % FEEDBACK_STEP:
       continue

    
    for link in links:
        link_obj = Vissim.Net.Links.ItemByKey(link)

        link_length = data[link]["length"]
        data[link]['all_vehicles'] = link_obj.Vehs.GetAll()
        num_cars = len(data[link]['all_vehicles'])

        density = num_cars / link_length
        data[link]["density"] = density
        num_lanes = data[link]["num_lanes"]
        # desired_speed = link_obj.AttValue('MesoSpeed')
        avg_speed = np.mean([veh.AttValue('Speed') for veh in data[link]["all_vehicles"]]) 
        avg_gap = np.mean([veh.AttValue('FollowDistGr') for veh in data[link]["all_vehicles"]]) 
        # avg_gap = link_obj.AttValue('MesoFollowUpGap')
        input_rate = len([vehs for vehs in data[link]['all_vehicles'] if vehs not in data[link]["prev_all_vehicles"]])
        exit_rate = len([vehs for vehs in data[link]["prev_all_vehicles"] if vehs not in data[link]['all_vehicles']])

        data[link]["prev_all_vehicles"] = [vehs for vehs in data[link]["all_vehicles"]]
        data[link]["input_rate"] = input_rate
        data[link]["exit_rate"] = exit_rate
        if link != 11: # last link
            next_input_rate = data[ data[link]["next_link"] ]["input_rate"]
            next_exit_rate = data[ data[link]["next_link"] ]["exit_rate"]


            features = [density, num_lanes, avg_speed, avg_gap, input_rate, exit_rate, next_input_rate, next_exit_rate]
            pred = data[link]["model"](features)

            max_speed = 60
            min_speed = 5
            desired_speed = (pred * (max_speed - min_speed)) + min_speed
            for veh in data[link]["all_vehicles"]:
                veh.SetAttValue("DesSpeed", desired_speed) 

            alpha = 0.5
            beta = 0.5
            cost = alpha * (data[link]["density"] - data[link]["density_prev"]) + beta * (data[ data[link]["next_link"] ]["density"] - data[ data[link]["next_link"] ]["density_prev"])

            data[link]["density_prev"] = density

    

end = Vissim.Simulation.AttValue('SimSec')
print(end)
Vissim.Simulation.Stop()
 
