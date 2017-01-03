import sys
import numpy
import pickle
from array import *
from threading import Thread
from time import sleep
from socket import *

allRoutersDict = {}
ackDict = {}

def client(*args):
    routerId = args[0]
    allroutersPath = args[1]
    allroutersPort = args[2]
    
    routersInfo = [routerId, allRoutersDict]
        
    clientSocket = socket(AF_INET,SOCK_DGRAM)
    while(1):
	for port in allroutersPort:
	    portNumber = allroutersPort[port]
	    address = ("127.0.0.1", int(portNumber))
	    if not (clientSocket.sendto(pickle.dumps(routersInfo),address)):
		for key in allRoutersDict.keys:
		    if port in key:
			del allRoutersDict[key]
		    True
	# receive ACK
	sleep(1)


def sendAck(arg, arg2):
    clientSocket = socket(AF_INET, SOCK_DGRAM) 
    message = [arg2, 200]
    message = pickle.dumps(message) 
    if(clientSocket.sendto(message,arg)):
	print arg
    return True



def server(*args):
    portNumber = args[0]
    routersPort = args[1]
    routerId = args[2]
        
    serverSocket=socket(AF_INET,SOCK_DGRAM)
    serverSocket.bind(("127.0.0.1",int(portNumber)))

    while(1):
	message,addr = serverSocket.recvfrom(4096)
	
	incomingRouterInfo = pickle.loads(message) 
	
	if(incomingRouterInfo[1] == 200):
	    if(ackDict.has_key(incomingRouterInfo[0])):
		ackDict[incomingRouterInfo[0]] = 0
	    else:
		ackDict.setdefault(incomingRouterInfo[0], 0)
	else:
	    cAddr = (addr[0], routersPort[incomingRouterInfo[0]])
	    sendAck(cAddr, routerId)
	    
	    for key in ackDict:
		ackDict[key] = ackDict[key] + 1
	    
	    iRouterId = incomingRouterInfo[0]
	    iRouterDict = incomingRouterInfo[1]
	    
	    for router in iRouterDict:
		if not (allRoutersDict.has_key((router[0], router[1])) or allRoutersDict.has_key((router[1], router[0]))):
		    allRoutersDict.setdefault(router, iRouterDict[router])
		
	#print allRoutersDict
	print ackDict
	    

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

    print "server: current dict = ", allRoutersDict
    
    thread1 = Thread(target = server, args = [routerPortNumber, routersPort, routerId])
    thread2 = Thread(target = client, args = [routerId, routersPath, routersPort])
    thread1.start()
    thread2.start()
    thread1.join()  
    thread2.join()
