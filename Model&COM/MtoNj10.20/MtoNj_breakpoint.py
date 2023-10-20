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
filename = r"C:\Users\zj2187\Desktop\MtoNj\MtoNj_no.inp0" #好像不能用相对路径
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\MtoNj\MtoNj_no.layx"
Vissim.LoadLayout(Filename)

#3.仿真参数设置
End_of_simulation = 3600 # simulation second [s]
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)
Random_Seed = 45
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)

Break = 0

for i in range(0,30000): #仿真时长
    All_Vehicles = Vissim.Net.Vehicles.GetAll()
    b = np.zeros(9, dtype=float)
    if len(All_Vehicles) == 0: # if no cars come yet, we let it continous run
        Vissim.Simulation.RunSingleStep()
        print("No car")
    else: # if there get cars, we control their speed
        for cur_Veh in All_Vehicles: # get buffer size for each link
            lane = str(cur_Veh.AttValue('Lane'))
            if(len(lane)==3):
                idx = int(lane[0])-1
                b[idx] += 1
        if b[0]+b[4]>=550/4 or b[1]+b[5]>=550/4 or b[2]+b[6]>=550/4 or b[3]+b[7]>=550/4:
            Break = 1
            print("MAX CAPACITY:",i/10)
            break
        Vissim.Simulation.RunSingleStep()

end = Vissim.Simulation.AttValue('SimSec')
print(end)
Vissim.Simulation.Stop()
