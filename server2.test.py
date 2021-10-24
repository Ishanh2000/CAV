# AUM SHREEGANESHAAYA NAMAH||
from server2 import Server2 as Server
from numpy.random import poisson
import csv
import random
from threading import Thread
from config import poi_avg


S = None

def randStr():
  return ''.join(random.choice(['0', '1', '2', '3', '4', '5']) for x in range(10))

class MinCAV:
  def __init__(self, ID, maxIter):
    self.ID = ID
    self.timestamp = poisson(poi_avg["boot_time"]) # 100 ms boot time
    self.maxIter = maxIter
    self.iter = 0
    self.thread = Thread(target = self.execute)
    self.logFile = open(f"./logFiles/minCav_{self.ID}.txt", "w")
    self.dataFile = open(f"./logFiles/minCav_{self.ID}_stats.csv", "w")
    self.logFile.write(f"ID = {self.ID}, Boot Time = {self.timestamp}, Max Iterations = {self.maxIter}\n")
    self.lastBcTime = None
    self.bcDiff = []

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
        l_bcDiff = len(self.bcDiff)
        total_bcDiff = 0
        for diff in self.bcDiff: total_bcDiff += diff
        self.dataFile.write("totalBcDiff,numBcDiff,avgBcDiff\n")
        self.dataFile.write(f"{total_bcDiff},{l_bcDiff},{total_bcDiff/l_bcDiff}\n")
        self.dataFile.close()
        exit(0)

      self.timestamp += poisson(poi_avg["compute_future_path_1"])
      self.timestamp += poisson(poi_avg["compute_future_path_2"])

      # record apparent periodicity
      if self.lastBcTime != None: self.bcDiff.append(self.timestamp - self.lastBcTime)
      self.lastBcTime = self.timestamp

      bcInfo = { "ID" : self.ID, "timestamp" : self.timestamp, "other": randStr() }
      self.logFile.write(f"TS-{self.timestamp}: Sending info = {bcInfo}\n")
      S.broadcast(bcInfo)
      otherInfo, self.timestamp = S.receive()
      self.logFile.write(f"TS-{self.timestamp}: Receiving info = {otherInfo}\n")

      self.timestamp += poisson(poi_avg["find_conflict_zones"])

      bcInfo = { "ID" : self.ID, "timestamp" : self.timestamp, "other": randStr() }
      self.logFile.write(f"TS-{self.timestamp}: Sending info = {bcInfo}\n")
      S.broadcast(bcInfo)
      otherInfo, self.timestamp = S.receive()
      self.logFile.write(f"TS-{self.timestamp}: Receiving info = {otherInfo}\n")

      self.timestamp += poisson(poi_avg["construct_CDG"])
      self.timestamp += poisson(poi_avg["deadlock_resolution"])
      self.timestamp += poisson(poi_avg["motion_planner"])
      self.timestamp += poisson(poi_avg["motion_controller"])

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
  
  # now analyze from JSON files
  totalBcDiff, numBcDiff = 0, 0
  for i in range(carNum):
    with open(f"./logFiles/minCav_{i}_stats.csv", "r") as f:
      data = list(csv.reader(f))
      # print(data[1])
      totalBcDiff += float(data[1][0])
      numBcDiff += float(data[1][1])
  print(f"totalBcDiff = {totalBcDiff/1000} ms, numBcDiff = {numBcDiff}, avgBcDiff = {(totalBcDiff/numBcDiff)/1000} ms")
    

  
