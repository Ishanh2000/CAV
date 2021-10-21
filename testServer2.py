# AUM SHREEGANESHAAYA NAMAH||
from server2 import Server2 as Server
from numpy.random import poisson
import random
from threading import Thread

S = None

def randStr():
  return ''.join(random.choice(['0', '1', '2', '3', '4', '5']) for x in range(10))

class MinCAV:
  def __init__(self, ID, maxIter):
    self.ID = ID
    self.timestamp = poisson(100000) # 100 ms boot time
    self.maxIter = maxIter
    self.iter = 0
    self.thread = Thread(target = self.execute)
    self.logFile = open(f"minCav_{self.ID}.txt", "w")
    self.logFile.write(f"ID = {self.ID}, Boot Time = {self.timestamp}, Max Iterations = {self.maxIter}\n")

  def __del__(self):
    self.logFile.write(f"\nExiting...\n")
    self.logFile.close()

  def execute(self):
    while True:
      self.logFile.write(f"\nITERATION {self.iter}:\n")
      if self.iter == (self.maxIter - 1): # like reaching destination
        S.dontCare()
        self.logFile.write(f"TS-{self.timestamp}: Reached Destination.\n")
        self.logFile.write(f"Iterations Executed: {self.iter + 1} / {self.maxIter}\n")
        exit(0)      

      self.timestamp += poisson(10000) # 10 ms

      bcInfo = { "ID" : self.ID, "timestamp" : self.timestamp, "other": randStr() }
      self.logFile.write(f"TS-{self.timestamp}: Sending info = {bcInfo}\n")
      S.broadcast(bcInfo)

      otherInfo, self.timestamp = S.receive()
      self.logFile.write(f"TS-{self.timestamp}: Receiving info = {otherInfo}\n")

      self.timestamp += poisson(10000) # 10 ms

      bcInfo = { "ID" : self.ID, "timestamp" : self.timestamp, "other": randStr() }
      self.logFile.write(f"TS-{self.timestamp}: Sending info = {bcInfo}\n")
      S.broadcast(bcInfo)

      otherInfo, self.timestamp = S.receive()
      self.logFile.write(f"TS-{self.timestamp}: Receiving info = {otherInfo}\n")

      self.timestamp += poisson(10000) # 10 ms

      self.iter += 1

carNum = 5
cavs = []

if __name__ == "__main__":
  S = Server(carNum = carNum)
  for i in range(carNum):
    cav = MinCAV(ID = i, maxIter = poisson(10))
    cavs.append(cav)
    cav.thread.start()
  
  for cav in cavs:
    cav.thread.join()
    

  
