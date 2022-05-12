import utils_cstar as ctsarCalc
import sys
import time 

print(time.time())
start_time = time.time()

sys.setrecursionlimit(15000)

# file = open('sample_input.txt', 'r')
file = open('nairobi_input.txt', 'r')
Lines = file.readlines()
 
linkCount = len(Lines)
source = set()
sink = set()
merges = set()
junctions = set()
linkMap = dict()
linkNum = 1;
junctionInputMap = dict()
junctionOutputMap = dict()
mergeInputMap = dict()
mergeOutputMap = dict()
linkCStarDelayMap = dict()
junctionIsAllGreenMap = dict()
routes_result = []
visitedNodes = []
# burst = [
# [1,3600,60]
# ]
# burst = [
# [1,3600,240]
# ]
# burst = [
# [1,3600,480]
# ]
burst = [
[1,300 ,60],
[300, 600 ,120],
[600, 900 ,180],
[900, 1200 ,240],
[1200, 1500 ,300],
[1500, 1800 ,360],
[1800, 2100 ,420],
[2100, 2400, 480],
[2400, 2700 ,420],
[2700, 3000 ,360],
[3000, 3300 ,300],
[3300, 3600 ,240],
[3600, 3900 ,180],
[3900, 4200 ,120],
[4200, 4800 ,60]
]
output_file = open('nairobi_input_output.txt','w')
numroutes = 0

def convertSpeedToMperSec(speedInKmph):
    speed = round(speedInKmph*5/18)
    return speed

def dfs(source, sink, path, linkMap):
    print("DFS {} {}".format(source, sink))
    global routes_result
    global visitedNodes
    
    if source == sink:
        if len(path) != 0:
            routes_result.append(path.copy())
        return

    visitedNodes.append(source)
    for node in linkMap.get(source,[]):
        if node[1] not in visitedNodes:
            path.append(node[0])
            dfs(node[1],sink,path,linkMap)
            path.remove(node[0])
    # visitedNodes.remove(source)



def findPathSourceToSink(source, sink, linkMap):
    global visitedNodes
    print("FIND PATHS TO SINK {} {}".format(source, sink))
    # time.sleep(5)
    visitedNodes = []
    path = []
    dfs(source, sink, path, linkMap)
    return


def findRoutesForEachSources(source, linkMap, sinkList):
    print("FIND ROUTES FOR EACH SOURCES")
    key1 = source
    for sink in sinkList:
        findPathSourceToSink(source, sink, linkMap)
    return




if __name__ == '__main__':

    print("STARTING MAIN")
    # time.sleep(5)

    for line in Lines:
        print("PROCESSING LINE")
        print(line)
        src, dest, distanceInMeters, speedInKmph  = map(int, line.split())
        if src > 1000 and src < 2000:
            source.add(src)
        if src > 2000 and src < 3000:
            sink.add(src)
        if src > 3000 and src < 5000:
            merges.add(src)
        if src > 5000:
            junctions.add(src)
        # if src > 4000 and src < 5000:
            

        if dest > 1000 and dest < 2000:
            source.add(dest)
        if dest > 2000 and dest < 3000:
            sink.add(dest)
        if dest > 3000 and dest < 5000:
            merges.add(dest)
        if dest > 5000:
            junctions.add(dest)
        # if dest > 4000 and dest < 5000:
            
        linkMap[src] = linkMap.get(src,[]) + [[linkNum, dest]]
        delay = round(distanceInMeters / convertSpeedToMperSec(speedInKmph))
        ## WHAT HAPPENS IF DELAY IS 0. Can we increment it to 1?
        if delay ==0: delay+=1
        cstar = round(ctsarCalc.get_exitrate(speedInKmph))
        linkCStarDelayMap[linkNum] = [cstar, delay]
        linkNum+=1

    file.close()
    print("DONE PROCESSING LINE")
    # time.sleep(5)



    # file1 = open('isAllGreen_nairobi_input.txt', 'r')
    # lines_isAllGreen = file1.readlines()

    # for line in lines_isAllGreen:
    #     junction, isAllGreen = map(int, line.split())
    #     junctionIsAllGreenMap[junction] = isAllGreen

    # file1.close()

    # print("LINK MAP")
    # print(linkMap)
    # print("\n")
    print("CREATING MAPS")
    for line in Lines:
        print(line)
        src, dest, distanceInMeters, speedInKmph = map(int, line.split())
        # if src > 3000 and src < 4000:
        if src >5000 :
            junctionOutputMap[src] = junctionOutputMap.get(src,set())
            for nodesList in linkMap.get(src):
                junctionOutputMap[src].add(nodesList[0])
        if src > 3000 and src < 5000:
            mergeOutputMap[src] = mergeOutputMap.get(src,set())
            for nodesList in linkMap.get(src):
                mergeOutputMap[src].add(nodesList[0])

        # if dest > 3000 and dest < 4000:
        if dest > 5000:
            junctionInputMap[dest] = junctionInputMap.get(dest,set())
            for nodesList in linkMap.get(src):
                if nodesList[1] == dest:
                    junctionInputMap[dest].add(nodesList[0])

    print("DONE CREATING MAPS")
    # time.sleep(5)
    print("MERGE INPUT MAP")
    for key in linkMap.keys():
        nodesList = linkMap.get(key)
        for node in nodesList:
            dest = node[1]
            if dest > 3000 and dest < 5000:
                mergeInputMap[dest] = mergeInputMap.get(dest,set())
                mergeInputMap[dest].add(node[0])

    print("DONE MERGE INPUT MAP")
    # time.sleep(5)

    output_file.write(str(linkCount)+'\n')
    output_file.write('\n')
    c = 1

    print("WRITE LINK")
    while c<= linkCount:
        cstr, d = linkCStarDelayMap[c]
        string = str(cstr)+ ' '+ str(d)+'\n'
        output_file.write(string)
        c+=1
    output_file.write('\n')
    output_file.write(str(len(source))+'\n')
    output_file.write('\n')
    print("DONE WRITE LINK")
    # time.sleep(5)
    print("WRITE SOURCE")
    for s in  source:
        print(s)
        output_file.write(str(s)+'\n')
        linkID = linkMap[s][0][0]
        output_file.write(str(linkID)+'\n')
        output_file.write(str(len(burst))+'\n')
        print("writing burst")
        # time.sleep(5)
        for b in burst:
            res = ''
            for i in b:
                res+= str(i)+' '
            output_file.write(res+'\n')
        print("done writing burst")
        routes_result = []
        print("finding route")
        # time.sleep(5)
        findRoutesForEachSources(s, linkMap, sink)
        print("done finding route")
        # time.sleep(5)
        output_file.write(str(len(routes_result))+'\n')
        print("writing path")
        # time.sleep(5)
        for path in routes_result:
            output_file.write(str(len(path))+'\n')
            res = ''
            for i in path:
                res += str(i)+' '
            output_file.write(res+'\n')
        output_file.write('\n')
        print("done writing path")

    print("DONE WRITE SOURCE")
    # time.sleep(5)
    
    output_file.write(str(len(sink))+'\n')
    output_file.write('\n')

    print("WRITE SINK")
    for nodeList in linkMap.keys():
        for n in linkMap[nodeList]:
            if n[1] in sink:
                output_file.write(str(n[1])+ ' ' + str(n[0])+'\n')
    output_file.write('\n')

    output_file.write(str(len(junctions))+'\n')
    output_file.write('\n')
    print("DONE WRITE SINK")
    # time.sleep(5)
    print("JUNCIONS")
    print(junctionInputMap)
    print(junctionOutputMap)
    for j in junctions:
        print(j)
        output_file.write(str(j)+'\n')
        # output_file.write(str(junctionIsAllGreenMap[j])+'\n')
        output_file.write("0"+'\n')
        output_file.write(str(len(junctionInputMap[j]))+'\n')
        inp = junctionInputMap[j]
        res = ''
        for i in inp:
            res += str(i)+ ' '
        res += '\n'
        output_file.write(res)
        output_file.write(str(len(junctionOutputMap[j]))+'\n')
        output = junctionOutputMap[j]
        res = ''
        for i in output:
            res += str(i)+ ' '
        res += '\n'
        output_file.write(res)
        output_file.write('\n')

    output_file.write(str(len(merges))+'\n')
    output_file.write('\n')

    print("DONE JUNCTIONS")
    # time.sleep(5)
    print("MERGE")
    for m in merges:
        print(m)
        output_file.write(str(m)+'\n')
        output_file.write(str(len(mergeInputMap[m]))+'\n')
        inp = mergeInputMap[m]
        res = ''
        for i in inp:
            res += str(i)+ ' '
        res += '\n'
        output_file.write(res)
        output = mergeOutputMap[m]
        res = ''
        for i in output:
            res += str(i)+ ' '
        res += '\n'
        output_file.write(res)
        output_file.write('\n')

    print("DONE MERGE")
    # time.sleep(5)
    output_file.close()
print(time.time())
print("--- %s seconds ---" % (time.time() - start_time))






