# AUM SHREEGANESHAAYA NAMAH||
from numpy.random import poisson
from copy import deepcopy
from threading import Lock

poi_avg_server = 25000 # Average computing times (Poisson distribution) in microseconds (us)

class Server2:
  def __init__(self, carNum = 0):
    self.carNum = carNum
    self.infoBucket = {}
    self.lock = Lock()
    self.maxLocalTs = -1
    self.mode = "bc" # "bc" (broadcast) / "rx" (receive)
    self.rxRemain = 0 # remaining cars to receive infoBucket

  def broadcast(self, info):
    # assume info is dictionary with keys "ID", "timestamp" at the least
    while self.mode != "bc" : pass
    infoCopy = deepcopy(info)
    self.lock.acquire()
    localTs = infoCopy["timestamp"] # this is the broadasting start timestamp, not the fpStartTs
    if localTs > self.maxLocalTs: self.maxLocalTs = localTs
    self.infoBucket[infoCopy["ID"]] = infoCopy
    if len(self.infoBucket) == self.carNum: # prepare for next receive
      self.rxRemain = self.carNum
      self.mode = "rx"
    self.lock.release()

  def receive(self):
    while self.mode != "rx" : pass
    offset = poisson(poi_avg_server)
    retVal = (deepcopy(self.infoBucket), self.maxLocalTs + offset)
    self.lock.acquire()
    self.rxRemain -= 1
    if self.rxRemain == 0: # prepare for next broadcast
      self.infoBucket = {}
      self.maxLocalTs = -1
      self.mode = "bc"
    self.lock.release()
    return retVal

  def dontCare(self): # ID not even required
    self.lock.acquire()
    self.carNum -= 1
    if len(self.infoBucket) == self.carNum:
      self.rxRemain = self.carNum
      self.mode = "rx"
    self.lock.release()
