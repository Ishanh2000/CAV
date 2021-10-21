# AUM SHREEGANESHAAYA NAMAH||
import numpy as np
from threading import Lock

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
    self.lock.acquire()
    localTs = info["timestamp"]
    if localTs > self.maxLocalTs: self.maxLocalTs = localTs
    self.infoBucket[info["ID"]] = info
    if len(self.infoBucket) == self.carNum: # prepare for next receive
      self.rxRemain = self.carNum
      self.mode = "rx"
    self.lock.release()

  def receive(self):
    while self.mode != "rx" : pass
    offset = np.random.poisson(lam = 10000) # 10000 us = 10 ms
    retVal = (self.infoBucket, self.maxLocalTs + offset)
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

def testServer(): pass
