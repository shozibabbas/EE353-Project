import sys
import numpy
import pickle
from array import *
from threading import Thread
from time import sleep
from socket import *
import djikstra
import os
import subprocess as sp

allRoutersDict = {}
ackDict = {}
activeRouters = {}
deletedKeys = []
djikstraTable = []

def client(*args):
    routerId = args[0]
    allroutersPath = args[1]
    allroutersPort = args[2]
    
    routersInfo = [routerId, allRoutersDict, ackDict]
        
    clientSocket = socket(AF_INET,SOCK_DGRAM)
    while(1):
	for port in allroutersPort:
	    portNumber = allroutersPort[port]
	    address = ("127.0.0.1", int(portNumber))
	    clientSocket.sendto(pickle.dumps(routersInfo),address)
	sleep(1)

def server(*args):
    portNumber = args[0]
    routersPort = args[1]
    routerId = args[2]
        
    serverSocket=socket(AF_INET,SOCK_DGRAM)
    serverSocket.bind(("127.0.0.1",int(portNumber)))

    while(1):
	message,addr = serverSocket.recvfrom(4096)
	
	incomingRouterInfo = pickle.loads(message) 
	    
	iRouterId = incomingRouterInfo[0]
	iRouterDict = incomingRouterInfo[1]
	iRouterAckDict = incomingRouterInfo[2]
	
	for router in iRouterAckDict:
	    if(activeRouters.has_key(router)):
		activeRouters[router] = iRouterAckDict[router]
	    else:
		activeRouters.setdefault(router, iRouterAckDict[router])
	for router in ackDict:
	    if(activeRouters.has_key(router)):
		activeRouters[router] = ackDict[router]
	    else:
		activeRouters.setdefault(router, ackDict[router])		

	for key in ackDict:
	    ackDict[key] = ackDict[key] + 1
	
	ackDict[iRouterId] = 0
	"""
	for delKey in ackDict:
	    if(delKey > 3):
		for key in allRoutersDict:
		    if(key[0] == delKey or key[1] == delKey):
			deletedKeys.append(key)
	for key in deletedKeys:
	    if allRoutersDict.has_key(key):
		del allRoutersDict[key]"""
			
	for router in iRouterDict:
	    if not (allRoutersDict.has_key((router[0], router[1])) or allRoutersDict.has_key((router[1], router[0]))):
		allRoutersDict.setdefault(router, iRouterDict[router])
	sleep(0.1)
    return true
	    
def djikstraShortestPath(*args):
    while(1):
	sleep(30)
	os.system('cls')
	edgeNodes = []
	djikstraTable = []
	allNodes = set()
	for key in allRoutersDict:
	    if key[0] in activeRouters and activeRouters[key[0]] > 3 or key[1] in activeRouters and activeRouters[key[1]] > 3:
		continue
	    fromNode = ""
	    toNode = ""
	    path = 0.0
	    fromNode = key[0]
	    toNode = key[1]
	    path = allRoutersDict[key]
	    allNodes.add(fromNode)
	    allNodes.add(toNode)
	    s = (fromNode, toNode, path)
	    edgeNodes.append(s)
	for n in allNodes: 
	    if not (n == args[0]):
		djikstraTable.append((args[0], n, djikstra.dijkstra(edgeNodes, args[0], n)))
	
	print "I am Router ", args[0]
	
	for row in djikstraTable:
	    if row[1] == float("inf") or row[1] in activeRouters and activeRouters[row[1]] <= 3:
		print "Least cost path to router ", row[1],":", convertToPath(row[2][1]), " and the cost: ", row[2][0]
    return True

def convertToPath(dPath):
    if(dPath[1] == ()):
	if not dPath[0] == None:
	    print (dPath[0]),
    else:   
	convertToPath(dPath[1])
	if not dPath[0] == None:
	    print (dPath[0]),
    return
    

if __name__ == "__main__":
   
    routerId = sys.argv[1]
    routerPortNumber = sys.argv[2]
    routerConfigFile = sys.argv[3]
    
    routers = []
    
    fLines = [line.rstrip('\n') for line in open(routerConfigFile, "r")]
    
    numberOfRouters = fLines[0]
    del fLines[0]
    
    for line in fLines:
        routers.append(line.split())

    
    routersPath = {}
    routersPort = {}
    
    for x in routers:
        routersPath.setdefault(x[0], float(x[1]))
	routersPort.setdefault(x[0], int(x[2]))
	allRoutersDict.setdefault((routerId, x[0]), float(x[1]))
	ackDict.setdefault(x[0], 0)
    
    thread1 = Thread(target = server, args = [routerPortNumber, routersPort, routerId])
    thread2 = Thread(target = client, args = [routerId, routersPath, routersPort])
    thread3 = Thread(target = djikstraShortestPath, args = [routerId])
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

