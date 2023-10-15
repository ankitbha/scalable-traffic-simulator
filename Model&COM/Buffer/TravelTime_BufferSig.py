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

#1.连接VISSIM并创建VISSIM对象
Vissim = win32com.client.gencache.EnsureDispatch("Vissim.Vissim.23") #最后数字为版本号
print(Vissim)

#2.加载路网(我们在绘制路网的时候通常会导入一张背景图，然后在上面绘制，注意这里仅加载路网不加载背景图)
filename = r"C:\Users\zj2187\Desktop\Buffer_sig2.inp0" #好像不能用相对路径
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\Buffer_sig2.layx"
Vissim.LoadLayout(Filename)

#3.仿真参数设置
End_of_simulation = 12000 # simulation second [s]
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)

Random_Seed = 42
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)

Cars = []
Cars_now = []
Cars_prev = [0]
Num = 0
Sp = 125
count = 0
for i in range(0,12000): #仿真时长
    Cars_now = []
    count += 1
    if count == 1000:
        Sp -= 10
        count = 0
        
    print(i)
    Vissim.Simulation.RunSingleStep()#一步一步仿真直到仿真时间结束
    All_Vehicles = Vissim.Net.Vehicles.GetAll() # get all vehicles in the network at the actual simulation second
    if len(All_Vehicles) == 0:
        Cars_now = [0]
        print(Cars_prev)
        print(Cars_now)

        if Cars_prev[0] != 0:
            Cars[Cars_prev[0]-1][1] = i/10
        
        Cars_prev = Cars_now
        print("No car")
    else:
        Vissim.Log(16384, 'All vehicles by GetAll():')
        print(All_Vehicles[0])
        for cur_Veh in All_Vehicles:
            veh_number      = cur_Veh.AttValue('No')
            veh_position    = cur_Veh.AttValue('Pos')
            if veh_position <= 201:
                #cur_Veh.SetAttValue('Speed', Sp)
                cur_Veh.SetAttValue('DesSpeed', Sp)
            Cars_now.append(veh_number)
        print(Cars_prev)
        print(Cars_now)

        if Cars_prev[0] == 0 or Cars_prev[-1] != Cars_now[-1]:
            Cars.append([i/10,0])
        if Cars_prev[0] != Cars_now[0]:
            Cars[Cars_prev[0]-1][1] = i/10
        
        Cars_prev = Cars_now
print(Cars)
Vissim.Simulation.Stop()
