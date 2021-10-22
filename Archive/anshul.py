# AUM SHREEGANESHAAYA NAMAH|| AUM SHREEHANUMATE NAMAH||

import numpy as np

def constructCDG(PDG_list):
    n = len(PDG_list)
    CDG = np.zeros((n,n))
    for PDG in PDG_list:
        CDG = np.logical_or(CDG,PDG)
    return CDG

def DFS(CDG, visited, parent,start,n):
    visited[start] = -1
    cycle = []
    flag =0
    for i in range(n):
        if(CDG[start][i]==True):
            if(visited[i]==0):
                parent[i] = start
                cycle = DFS(CDG, visited, parent, i,n)
                if(cycle!=[]):
                    return cycle
            elif(visited[i]==-1):#cycle detected
                # print("entered here")
                # print(start)
                # print(parent)
                # print(i)
                j = start
                while(parent[j]!=i):
                    cycle.append(j)
                    j = parent[j]
                cycle.append(j)
                cycle.append(i)
                return cycle     
                # cycle = [1,4,6]
                # return cycle     

    # print("tf")
    visited[start] = 1
    return cycle

##finding cycles
##function is expected to find exactly one cycle and return the nodes invovled in the cycle
def findCycles(CDG):
    n = CDG.shape[0]
    visited = np.zeros(n)
    parent = np.arange(n)
    for start in range(n):
        if(visited[start]==0):
            cycle = DFS(CDG,visited,parent,start,n)
            print("Cyle: ", cycle)
            if(cycle != []):
                return cycle
    return []

def resolveCycle(CDG, cycle, averagedTOA):
    min_time  = averagedTOA[cycle[0]]
    leader = cycle[0]
    for vehicle in cycle:
        if(averagedTOA[vehicle]<min_time):
            min_time = averagedTOA[vehicle]
            leader = vehicle
    
    n = CDG.shape[0]
    for i in range(n):
        if(CDG[i][leader]):
            CDG[i][leader] = False
            CDG[leader][i] = True
    return CDG


averageTOA = [1,0,1,1,1,1,1]

def ResolveDeadlock(PDG_list, averaged_TOA):
    CDG = constructCDG(PDG_list)
    while(findCycles(CDG)!= []):
        cycle = findCycles(CDG)
        resolveCycle(CDG, cycle, averageTOA)

    return CDG