# AUM SHREEGANESHAAYA NAMAH|| AUM NAMAH SHIVAAYA||

# Connected Autonomous Vehicle (CAV) model class file

import os
import numpy as np
import config
from utils import dist, contiguous
from server import broadcast, receive

class CAV:
  ID, timestamp = None, 0 # microseconds (will later set to a random positive number)
  hasReached = False
  cont_end = 0 # microseconds

  # Graph Related Members
  wp, dest = None, None
  nbWts = None # similar to graph["neighbours"], but weights get updated in each iteration
  SP = None # waypoints indices
  FP = None # granula (FP) indices
  CZ = None # Conflict Zones (will be dictionary with CAV IDs as keys)
  PDG = None # Partial Dependency Graph

  # Dynamics Related Members
  x, y = None, None # m
  phi = None # radians
  v, v_max = None, None # m/s  (check if v_max is parameter)
  a, a_max = None, None # m/s2 (check if a_max is parameter)
  d_max = None

  Others_Info, Others_PDG = None, None # will be dictionary with CAV IDs as keys

  def __init__(self, car = None):
    self.nbWts = config.NBs # do not set when declaring as member - graph may not have been loaded
    if car == None:
      return
    self.ID = car["id"]
    self.wp, self.dest = car["closest_wp"], car["dest"]
    self.x, self.y = (car["x"]/100), (car["y"]/100) # LHS is metres
    self.phi, self.v, self.a = car["angle"], car["speed"], car["acc"]

  ######## GRAPH ALGORITHMS' STUFF ########
  #########################################

  def shortest_path(self):
    """ [Slow] Dijkstra Algorithm for Shortest Path between `self.wp` and `self.dest` """

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
    """ Computing Future Path """

    self.shortest_path() # self.SP gets updated
    l_sp = len(self.SP)

    fp, total_dist = [], 0.0 # future points, total distance (cm) covered by these future points
    for i in range(1 , l_sp):
      rem = (100.0 * self.d_max) - total_dist # remaining distance (cm)
      e_start, e_end = config.WPs[self.SP[i-1]], config.WPs[self.SP[i]] # points of edge
      d = dist(e_start, e_end) # edge length (cm)
      num_fp = np.ceil(np.min([rem, d]) / (config.b * 100))
      for j in range(int(num_fp)):
        fp.append({
          "x" : ( (d-100*j*config.b)*e_start["x"] + 100*j*config.b*e_end["x"] ) / d,
          "y" : ( (d-100*j*config.b)*e_start["y"] + 100*j*config.b*e_end["y"] ) / d,
          "e_start" : self.SP[i-1], "e_end" : self.SP[i], # indicates which edge these granulae were a part of
        })
      if (rem <= d):
        break
      if i == (l_sp-1):
        fp.append({ "x" : e_end["x"], "y" : e_end["y"], "e_start" : self.SP[i-1], "e_end" : self.SP[i] })
        break
      total_dist += d

    self.FP = fp # FP consists of granulae (xy coordinates)

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
    ts_other, v_other, fp_other = other["timestamp"], other["v"], other["FP"]
    
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
      toa1, toa2 = (self.timestamp + (10000*d1_begin/self.v)), (ts_other + (10000*d2_begin/v_other))
      diff, adv = (toa2-toa1), None
      if np.abs(diff) <= config.CLOCK_ACCURACY:
        adv = self.ID if (self.ID < other_cav_id) else other_cav_id
      else:
        adv = self.ID if (diff > 0) else other_cav_id
      
      C[i] = { # "cz" is array of indices in self.FP/other.FP
        "self" : { "begin" : (d1_begin/100), "end" : (d1_end/100), "toa" : toa1, "cz" : v1 },
        "other" : { "begin" : (d2_begin/100), "end" : (d2_end/100), "toa" : toa2, "cz" : v2 },
        "advantage" : adv
      }

    self.CZ[other_cav_id] = C
    # TODO: Calculate PDG. Ask Anshul how he will utilize the only self.CZ for computing entire CDG


  ######## BROADCASTING STUFF ########
  ####################################

  def get_info(self): # mainly for broadcasting/testing purposes
    return {
      "ID" : self.ID, "timestamp" : self.timestamp,
      "x" : self.x, "y" : self.y, "v" : self.v,
      "FP" : self.FP
    }

  def broadcast_info(self):
    broadcast(self.get_info(), config.CHANNEL_INFO)

  def receive_others_info(self):
    self.Others_Info = receive(config.CHANNEL_INFO, str(self.ID))

  def broadcast_PDG(self):
    broadcast({
      "ID" : self.ID, "timestamp" : self.timestamp,
      "PDG" : self.PDG
    }, config.CHANNEL_PDG)
  
  def receive_others_PDGs(self):
    self.Others_PDG = receive(config.CHANNEL_PDG, str(self.ID))

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


def test_cav_init():
  print("######## TEST CAV INIT ########")
  print("###############################\n")
  c = CAV()
  c.ID, c.timestamp = 0, 90990
  c.wp, c.dest = 0, 3
  c.x, c.y, c.phi, c.v, c.a = 90, 906, 0.785, 10, -1
  print(c)
  print()


def test_cav_sp_and_fp():
  print("######## TEST CAV SHORTEST PATH AND FUTURE PATH ########")
  print("########################################################\n")
  for car in config.cars:
    cav = CAV(car)
    cav.d_max = 10 # TODO: How and where to compute this correctly?
    cav.compute_future_path()
    print(cav)
    print(f"Shortest Path = {cav.SP}")
    print(f"Future Path = {cav.FP}")
    print()
  print()


def test_cav_find_conflict_zones():
  print("######## TEST CAV FIND CONFLICT ZONES ########")
  print("##############################################\n")
  CAVs, infos = [], []
  for car in config.cars:
    cav = CAV(car)
    cav.d_max = 10
    cav.compute_future_path()
    CAVs.append(cav)
    infos.append(cav.get_info())
  
  for i in range(3):
    # manually broadcasting for now
    other_a, other_b = infos[(i+1)%3], infos[(i+2)%3]
    id_a, id_b = other_a["ID"], other_b["ID"]
    CAVs[i].Others_Info = { id_a : other_a, id_b : other_b }
    CAVs[i].find_conflict_zones_all_CAVs()
    print(CAVs[i])
    print(CAVs[i].CZ)
    print()
  
  print()


def conductTests():
  test_cav_init()
  test_cav_sp_and_fp()
  test_cav_find_conflict_zones()


if __name__ == "__main__":
  config.importParentGraph(os.path.join(os.getcwd(), "samples/hex2.json"))
  conductTests()


