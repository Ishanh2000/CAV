# AUM SHREEGANESHAAYA NAMAH|| AUM NAMAH SHIVAAYA||

# Connected Autonomous Vehicle (CAV) model class file

import numpy as np
import config
from utils import dist, contiguous
from numpy.random import poisson
from threading import Thread

class CAV:
  ID, timestamp = None, 0 # microseconds (will later set to a random positive number)
  hasReached = False
  logFile = None
  cont_end = 0 # microseconds

  # Graph Related Members
  wp, dest = None, None
  nbWts = None # similar to graph["neighbours"], but weights get updated in each iteration
  SP = None # waypoints indices
  FP = None # granula (FP) indices
  fpStartTs = None
  CZ = None # Conflict Zones (will be dictionary with CAV IDs as keys)
  PDG = None # Partial Dependency Graph

  # Dynamics Related Members
  x, y = None, None # m
  phi = None # radians
  v, v_max = None, None # m/s  (check if v_max is parameter)
  a, a_max, a_brake = None, None, None # m/s2 (check if a_max is parameter)

  Others_Info, Others_PDG = None, None # will be dictionary with CAV IDs as keys

  def __init__(self, car):
    self.nbWts = config.NBs
    self.ID = car["id"]
    self.wp, self.dest = car["closest_wp"], car["dest"]
    self.x, self.y = (car["x"]/100), (car["y"]/100) # LHS is metres
    self.phi, self.v, self.a = car["angle"], car["speed"], car["acc"]
    self.timestamp = poisson(100000) # 100 ms "average" boot time
    self.thread = Thread(target = self.execute)
    self.logFile = open(f"./logFiles/CAV_{self.ID}.txt", "w")
    self.logFile.write(f"ID = {self.ID}, Boot Time = {self.timestamp}\n")
  
  def __del__(self):
    self.logFile.write("\nExiting...\n")
    self.logFile.close()


  ######## GRAPH ALGORITHMS' STUFF ########
  #########################################

  def find_closest_wp(self):
    """
    Find closest waypoint to (`self.x`, `self.y`) for starting journey. Do not consider which
    waypoint gives further shortest path (that requires all-pairs shortest distance algorithm).
    """
    self.wp, closest_dist = None, float('inf')
    l_WPs = len(config.WPs)
    for i in range(l_WPs):
      d = dist({ "x" : (self.x * 100), "y" : (self.y * 100) }, config.WPs[i])
      if d < closest_dist:
        self.wp = i
        closest_dist = d
    # assume self.wp != None after this

  def find_shortest_path(self):
    """
    [Slow] Dijkstra Algorithm for Shortest Path between `self.wp` and `self.dest`
    Output in `self.SP` (consists only of waypoints)
    """

    self.find_closest_wp() # updates self.wp
    l_WPs = len(config.WPs)

    cost = [float('inf') for i in range(l_WPs)] # costs are in time (milliseconds)
    parent = [None for i in range(l_WPs)] # parents
    cost[self.wp] = 0 # cost from source = 0
    Q = [i for i in range(l_WPs)] # all vertices in Min-Priority Queue (TODO: MAKE THIS EFFICIENT)

    while len(Q) > 0:
      min_q_idx = np.array([cost[u] for u in Q]).argmin() # get vertex with smallest distance (TODO: MAKE THIS EFFICIENT)
      u = Q[min_q_idx]
      del Q[min_q_idx]
      for nb in self.nbWts[u]:
        v, wt = nb["idx"], nb["wt"]
        if v in Q:
          alt = cost[u] + wt
          if alt < cost[v]:
            cost[v] = alt
            parent[v] = u
    
    sp = [self.dest] # list of vertices
    while parent[sp[-1]] != None:
      sp.append(parent[sp[-1]])
    sp.reverse()
    self.SP = sp # consists of waypoints (indices in config.WPs)

  def compute_future_path(self):
    """ Computing Future Path (made of granulae, which include CAV's current position) """
    
    self.fpStartTs = self.timestamp # used in computing TOA in CZ
    
    self.find_shortest_path() # self.SP gets updated
    
    # must add self position if not close enough to self.SP[0]
    mustAddSelf = dist({ "x" : (self.x * 100), "y" : (self.y * 100) }, config.WPs[self.wp]) >= config.FP_INCLUSION_THRESHOLD
    d_max = self.v_max * ((config.rho/1000) + (self.v_max/np.abs(self.a_brake)))
    l_sp = len(self.SP)

    fp, total_dist = [], 0.0 # future points, total distance (cm) covered by these future points

    for i in range(0 if mustAddSelf else 1 , l_sp):
      rem = (100.0 * d_max) - total_dist # remaining distance (cm)
      e_start = config.WPs[self.SP[i-1]] if (i > 0) else { "x" : (self.x * 100), "y" : (self.y * 100) } # starting waypoint of edge
      e_end = config.WPs[self.SP[i]] # ending waypoint of edge
      d = dist(e_start, e_end) # edge length (cm)
      num_fp = np.ceil(np.min([rem, d]) / (config.b * 100))
      for j in range(int(num_fp)):
        fp.append({
          "x" : ( (d-100*j*config.b)*e_start["x"] + 100*j*config.b*e_end["x"] ) / d,
          "y" : ( (d-100*j*config.b)*e_start["y"] + 100*j*config.b*e_end["y"] ) / d,
          "e_start" : self.SP[i-1] if (i > 0) else None, "e_end" : self.SP[i] # indicates the edge these granulae come from
        })
      if (rem <= d):
        break
      if i == (l_sp-1):
        fp.append({
          "x" : e_end["x"], "y" : e_end["y"],
          "e_start" : self.SP[i-1] if (i > 0) else None, "e_end" : self.SP[i] # indicates the edge these granulae come from
        })
        break
      total_dist += d

    self.FP = fp # FP consists of granulae (xy coordinates)

    self.timestamp += poisson(5000) # 5 ms "average" compute time

  def find_conflict_zones_all_CAVs(self):
    self.CZ = {} # empty previous results
    for other_cav_id in self.Others_Info:
      self.find_conflict_zones(other_cav_id)
  
  def find_conflict_zones(self, other_cav_id):
    """
    Find conflict zones between future paths (consists of granulae and associated
    edges) `self.FP` and `other.FP`. Also make Partial Dependency Graph (PDG) in parallel.
    """
    other = self.Others_Info[other_cav_id]
    v_other, fp_other = other["v"], other["FP"]
    
    l_fp, l_fp_other = len(self.FP), len(fp_other)
    mp, mp_other = [], [] # edge midpoints (mp[i] is midpoint of fp[i] and fp[i+1])
    for i in range(1, l_fp):
      tstart, tend = self.FP[i-1], self.FP[i]
      mp.append({ "x" : (tstart["x"] + tend["x"]) / 2, "y" : (tstart["y"] + tend["y"]) / 2 })
    for i in range(1, l_fp_other):
      tstart, tend = fp_other[i-1], fp_other[i]
      mp_other.append({ "x" : (tstart["x"] + tend["x"]) / 2, "y" : (tstart["y"] + tend["y"]) / 2 })
    
    # calculate conflicting pairs first
    C = []
    for i in range(l_fp-1):
      for j in range(l_fp_other-1):
        if dist(mp[i], mp_other[j]) < (config.d_th * 100): # LHS is in cm
          C.append({ "self" : [i], "other" : [j] })

    # merge conflicting pairs into conflicting zones (caution: C is a variable length array now)
    curr = 0
    while True:
      if curr >= (len(C)-1):
        break
      k = curr + 1
      while True:
        if k >= len(C):
          curr += 1
          break
        combinedZone = contiguous(zone = C[curr], pair = C[k])
        if combinedZone == None:
          k += 1
          continue
        C[curr] = combinedZone
        del C[k] # no need to increment k after this deletion

    l_C = len(C)
    for i in range(l_C):
      v1, d1_begin, d1_end = C[i]["self"], 0, 0 # d1_begin, d1_end in cm
      p, q, special = v1[0], v1[-1], (len(v1) <= 1)
      for k in range(p):
        d1_begin += dist(self.FP[k], self.FP[k+1])  
      d1_end = d1_begin
      for k in range(p, q):
        d1_end += dist(self.FP[k], self.FP[k+1])
      d1_begin += 0 if special else (0.5 * dist(self.FP[p], self.FP[p+1]))
      d1_end += (1 if special else 0.5) * dist(self.FP[q], self.FP[q+1])
      v1 = [p, p+1] if special else v1[1:]

      v2, d2_begin, d2_end = C[i]["other"], 0, 0 # d2_begin, d2_end in cm
      p, q, special = v2[0], v2[-1], (len(v2) <= 1)
      for k in range(p):
        d2_begin += dist(fp_other[k], fp_other[k+1])
      d2_end = d2_begin
      for k in range(p, q):
        d2_end += dist(fp_other[k], fp_other[k+1])
      d2_begin += 0 if special else (0.5 * dist(fp_other[p], fp_other[p+1]))
      d2_end += (1 if special else 0.5) * dist(fp_other[q], fp_other[q+1])
      v2 = [p, p+1] if special else v2[1:]

      # Times of Arrival (microseconds)
      toa1, toa2 = (self.fpStartTs + (10000*d1_begin/self.v)), (other["fpStartTs"] + (10000*d2_begin/v_other))
      diff, adv = (toa2-toa1), None
      if np.abs(diff) <= config.CLOCK_ACCURACY:
        adv = self.ID if (self.ID < other_cav_id) else other_cav_id
      else:
        adv = self.ID if (diff > 0) else other_cav_id
      
      C[i] = { # "cz" is array of indices in self.FP/other.FP, `begin` and `end` are in cm
        "self" : { "begin" : (d1_begin/100), "end" : (d1_end/100), "toa" : toa1, "cz" : v1 },
        "other" : { "begin" : (d2_begin/100), "end" : (d2_end/100), "toa" : toa2, "cz" : v2 },
        "advantage" : adv
      }

    self.CZ[other_cav_id] = C
    # TODO: Calculate PDG. Ask Anshul how he will utilize the only self.CZ for computing entire CDG
    self.timestamp += poisson(5000) # 5 ms "average" compute time


  ######## BROADCASTING STUFF ########
  ####################################

  def broadcast_info(self):
    config.S.broadcast({
      "ID" : self.ID, "timestamp" : self.timestamp, # this TS is broadcast start time
      "x" : self.x, "y" : self.y, "v" : self.v,
      "FP" : self.FP, "fpStartTs" : self.fpStartTs # this TS is fpStart start time
    })

  def receive_others_info(self):
    others_Info, self.timestamp = config.S.receive()
    del others_Info[self.ID]
    self.Others_Info = others_Info

  def broadcast_PDG(self):
    config.S.broadcast({
      "ID" : self.ID, "timestamp" : self.timestamp,
      "PDG" : self.PDG
    })
  
  def receive_others_PDGs(self):
    others_PDG, self.timestamp = config.S.receive()
    del others_PDG[self.ID]
    self.Others_PDG = {}
    for ID in others_PDG:
      self.Others_PDG[ID] = others_PDG[ID]["PDG"]

  # Stringifying object
  def __str__(self):
    ts = "%.3f" % (self.timestamp / 1000)
    dest = config.WPs[self.dest]
    wp = config.WPs[self.wp]
    retStr = f"CAV : ID = {self.ID}, Timestamp = {ts} ms, Has Reached = {self.hasReached}\n"
    retStr += f"Current WP = {self.wp} ({round(wp['x']/100, 3)} m, {round(wp['y']/100, 3)} m), "
    retStr += f"Destination WP = {self.dest} ({round(dest['x']/100, 3)} m, {round(dest['y']/100, 3)} m)\n"
    retStr += f"Position = ({self.x} m, {self.y} m), Angle (phi) = {self.phi} rad, "
    retStr += f"Velocity = {self.v} m/s, Acc. = {self.a} m/s2"
    return retStr

  def execute(self): pass
    # while True:
    #   self.logFile.write(f"\nITERATION {self.iter}:\n")
    #   if self.iter == (self.maxIter - 1): # like reaching destination
    #     config.S.dontCare()
    #     self.logFile.write(f"TS-{self.timestamp}: Reached Destination.\n")
    #     self.logFile.write(f"Iterations Executed: {self.iter + 1} / {self.maxIter}\n")
    #     exit(0)      

    #   self.timestamp += poisson(10000) # 10 ms

    #   bcInfo = { "ID" : self.ID, "timestamp" : self.timestamp, "other": randStr() }
    #   self.logFile.write(f"TS-{self.timestamp}: Sending info = {bcInfo}\n")
    #   S.broadcast(bcInfo)

    #   otherInfo, self.timestamp = S.receive()
    #   self.logFile.write(f"TS-{self.timestamp}: Receiving info = {otherInfo}\n")

    #   self.timestamp += poisson(10000) # 10 ms

    #   bcInfo = { "ID" : self.ID, "timestamp" : self.timestamp, "other": randStr() }
    #   self.logFile.write(f"TS-{self.timestamp}: Sending info = {bcInfo}\n")
    #   S.broadcast(bcInfo)

    #   otherInfo, self.timestamp = S.receive()
    #   self.logFile.write(f"TS-{self.timestamp}: Receiving info = {otherInfo}\n")

    #   self.timestamp += poisson(10000) # 10 ms

    #   self.iter += 1

