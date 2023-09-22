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
filename = r"C:\Users\zj2187\Desktop\9.2\no1.inp0" #好像不能用相对路径
Vissim.LoadNet(filename)
Filename = r"C:\Users\zj2187\Desktop\9.2\no1.layx"
Vissim.LoadLayout(Filename)

#3.仿真参数设置
End_of_simulation = 30000 # simulation second [s]
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)
Random_Seed = 42
Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)

Cars = []
Cars_now = []
Cars_prev = [[0,0,0,0,0,0]]

for i in range(0,30000): #仿真时长
    Cars_now = []
    
    print(i)
    Vissim.Simulation.RunSingleStep()#一步一步仿真直到仿真时间结束
    All_Vehicles = Vissim.Net.Vehicles.GetAll() # get all vehicles in the network at the actual simulation second
    if len(All_Vehicles) == 0:
        Cars_now = [[0,0,0,0,0,0]]
        #print(Cars_prev)
        #print(Cars_now)
        print("No car")
    else:
        for cur_Veh in All_Vehicles:
            veh_number      = cur_Veh.AttValue('No')
            veh_linklane    = cur_Veh.AttValue('Lane')
            veh_position    = cur_Veh.AttValue('Pos')
            Cars_now.append([veh_number,veh_linklane,veh_position,i/10,0,0])

        for n in range(0,len(Cars_now)):
            count = 0
            for p in range(0,len(Cars_prev)):
                if Cars_now[n][0] == Cars_prev[p][0]:
                    count = 1
            if count == 0:
                Cars.append(Cars_now[n])
     
        for n in range(0,len(Cars_now)):
            print(Cars_now[n][0], len(Cars))
            if Cars_now[n][1] == "10000-1" and Cars_now[n][2] >= 3 and Cars_now[n][2] <= 9:
                Cars[Cars_now[n][0]-1][4] = i/10
            elif Cars_now[n][1] == "10001-1" and Cars_now[n][2] >= 3 and Cars_now[n][2] <= 9:
                Cars[Cars_now[n][0]-1][4] = i/10
            elif Cars_now[n][1] == "10002-1" and Cars_now[n][2] >= 3 and Cars_now[n][2] <= 9:
                Cars[Cars_now[n][0]-1][4] = i/10
            elif Cars_now[n][1] == "10003-1" and Cars_now[n][2] >= 3 and Cars_now[n][2] <= 9:
                Cars[Cars_now[n][0]-1][4] = i/10
            elif Cars_now[n][1] == "5-1" and Cars_now[n][2] >= 144:
                Cars[Cars_now[n][0]-1][5] = i/10
    
   
print(Cars)
Vissim.Simulation.Stop()
