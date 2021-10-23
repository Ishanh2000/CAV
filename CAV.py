# AUM SHREEGANESHAAYA NAMAH|| AUM NAMAH SHIVAAYA||

# Connected Autonomous Vehicle (CAV) model class file

import numpy as np
import config
from utils import dist, contiguous, objStr
from numpy.random import poisson
from threading import Thread

class CAV:
  ID, timestamp = None, 0 # microseconds (will later set to a random positive number)
  logFile = None
  cont_end = 0 # microseconds ### @USELESS ###

  # Graph Related Members
  lookAhead, dest = None, None
  nbWts = None # similar to graph["neighbours"], but weights get updated in each iteration ### @USELESS ###
  SP = None # waypoints indices
  FP = None # granula (FP) indices
  fpStartTs = None
  CZ = None # Conflict Zones (will be dictionary with CAV IDs as keys)
  PDG = None # Partial Dependency Graph
  carIndices = None # dictionary
  CDG = None # Complete Dependency Graph

  # Dynamics Related Members
  x, y = None, None # m
  phi = None # radians
  v, v_max, v_safe = None, None, None # m/s  (check if v_max is parameter)
  a_brake = None # m/s2
  a, a_max = None, None # m/s2 ### @USELESS ###
  lastMcTs = None # us

  Others_Info, Others_PDG = None, None # will be dictionary with CAV IDs as keys

  def __init__(self, car):
    """ Initialization aka `Booting` """
    self.nbWts = config.NBs
    self.ID = car["id"]
    self.dest = car["dest"]
    self.x, self.y = (car["x"]/100), (car["y"]/100) # LHS is metres

    closest_dist, l_WPs = float('inf'), len(config.WPs)
    for i in range(l_WPs):
      d = dist({ "x" : (self.x * 100), "y" : (self.y * 100) }, config.WPs[i])
      if d < closest_dist:
        self.lookAhead = i
        closest_dist = d

    self.phi, self.v, self.a = car["angle"], 0, 0 # removed car["speed"], car["acc"]
    self.timestamp = self.lastMcTs = poisson(config.poi_avg["boot_time"])
    self.thread = Thread(target = self.execute)
    self.logFile = open(f"./logFiles/CAV_{self.ID}.txt", "w")
    self.logFile.write(f"ID = {self.ID}, Boot Time = {self.timestamp}\n")
    self.logFile.write(f"{self.__str__()}\n")
  
  def __del__(self):
    """ Destructor """
    self.logFile.write("\nExiting...\n")
    self.logFile.close()

  def __str__(self):
    """ Stringification """
    ts = "%.3f" % (self.timestamp / 1000)
    dest = config.WPs[self.dest]
    lookAhead = config.WPs[self.lookAhead]
    retStr = f"CAV : ID = {self.ID}, Timestamp = {ts} ms\n"
    retStr += f"Look Ahead WP = {self.lookAhead} ({round(lookAhead['x']/100, 3)} m, {round(lookAhead['y']/100, 3)} m), "
    retStr += f"Destination WP = {self.dest} ({round(dest['x']/100, 3)} m, {round(dest['y']/100, 3)} m)\n"
    retStr += f"fpStartTs = {self.fpStartTs}\n"
    retStr += f"lastMcTs = {self.lastMcTs}\n"
    retStr += f"Position = ({self.x} m, {self.y} m), Angle (phi) = {self.phi} rad\n"
    retStr += f"v = {self.v} m/s, v_max = {self.v_max} m/s, a_brake = {self.a_brake} m/s2\n"
    return retStr

  ######## GRAPH ALGORITHMS' STUFF ########
  #########################################

  def find_shortest_path(self):
    """
    [Slow] Dijkstra Algorithm for Shortest Path between `self.lookAhead` and `self.dest`
    Output in `self.SP` (consists only of waypoints's indices in config.WPs)
    """

    l_WPs = len(config.WPs)
    cost = [float('inf') for i in range(l_WPs)] # costs are in time (milliseconds)
    parent = [None for i in range(l_WPs)] # parents
    cost[self.lookAhead] = 0 # cost from source = 0
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
    mustAddSelf = dist({ "x" : (self.x * 100), "y" : (self.y * 100) }, config.WPs[self.lookAhead]) >= config.FP_INCLUSION_THRESHOLD
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
    self.timestamp += poisson(config.poi_avg["compute_future_path"])
    self.logFile.write(f"\nSHORTEST PATH\n{self.SP}\n")
    self.logFile.write(f"\nFUTURE PATH\n{objStr(self.FP)}\n")

  def find_conflict_zones_all_CAVs(self):
    # first compute self.carIndices
    self.carIndices = {}
    IDs = [self.ID]
    for other_cav_id in self.Others_Info:
      IDs.append(other_cav_id)
    IDs.sort()
    l_IDs = len(IDs)
    for i in range(l_IDs):
      self.carIndices[IDs[i]] = i

    self.PDG = np.zeros((l_IDs, l_IDs)) # lower ID gets lower index (as indicated by above computation)

    self.CZ = {} # empty previous results
    for other_cav_id in self.Others_Info:
      self.find_conflict_zones(other_cav_id)

    self.logFile.write(f"\nCONFLICT ZONES\n{objStr(self.CZ)}\n")
    self.logFile.write(f"\nPDG\n{self.PDG}\n")
  
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
      toa1 = (self.fpStartTs + (10000*d1_begin/self.v)) if (self.v != 0) else float('inf')
      toa2 = (other["fpStartTs"] + (10000*d2_begin/v_other)) if (v_other != 0) else float('inf')
      diff = 0 if ((toa2 == float('inf')) and (toa1 == float('inf'))) else (toa2-toa1)
      adv = None
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
    
    if l_C > 0: # for now considering only C[0] for PDG
      rowIndex, colIndex = self.carIndices[self.ID], self.carIndices[other_cav_id] # self.ID yields to other_cav_id
      if C[0]["advantage"] == self.ID: rowIndex, colIndex = colIndex, rowIndex # other_cav_id yields to self.ID
      self.PDG[rowIndex][colIndex] = 1

    self.timestamp += poisson(config.poi_avg["find_conflict_zones"])

  def construct_CDG(self):
    """ Construct CDG from `self.PDG` and `self.Others_PDG` and store it in `self.CDG` """
    l_carIndices = len(self.carIndices)
    self.CDG = np.zeros((l_carIndices, l_carIndices)) # lower index for lower ID
    self.CDG = np.logical_or(self.CDG, self.PDG)
    for PDG in self.Others_PDG:
      self.CDG = np.logical_or(self.CDG, self.Others_PDG[PDG])
    
    self.timestamp += poisson(config.poi_avg["construct_CDG"])
    self.logFile.write(f"\n{self.CDG}\n")

  def motion_planner(self):
    """ Very basic motion planning: simpl computing safe velocities """

    l_FP = len(self.FP)
    self.v_safe = [ self.v_max for i in range(l_FP - 1) ] # initially
    for other_cav_id in self.CZ:
      if len(self.CZ[other_cav_id]) < 1: continue # no confict with car `other_cav_id`
      c = self.CZ[other_cav_id][0] # consider only first CZ
      if c["advantage"] == self.ID: continue # nothing to do
      cz, begin = c["self"]["cz"], c["self"]["begin"]

      d_c = [] # FP-edge distances (cm) from cz
      for k in range(cz[0]):
        tmp_d_c = None
        if k == 0: tmp_d_c = (100 * begin) - 0.5 * dist(self.FP[0], self.FP[1])
        else: tmp_d_c = d_c[-1] - 0.5 * (dist(self.FP[k-1], self.FP[k]) + dist(self.FP[k], self.FP[k+1]))
        if (-10 < tmp_d_c) and (tmp_d_c < 0): tmp_d_c = 0
        if tmp_d_c < 0: break
        d_c.append(tmp_d_c)
      
      self.logFile.write(f"\noher_cav_id = {other_cav_id}\nd_c = {d_c}\n")
      
      l_d_c = len(d_c)
      rho = config.rho / 1000.0 # s
      b = np.abs(self.a_brake) # m/s2
      for i in range(l_d_c):
        self.logFile.write(f"{i}: {((( ((b*rho)**2) + (2*b*d_c[i]/100) )**0.5) - (b * rho))}\n")
        self.v_safe[i] = min(self.v_safe[i], self.v_max, ((( ((b*rho)**2) + (2*b*d_c[i]/100) )**0.5) - (b * rho)))

    self.timestamp += poisson(config.poi_avg["motion_planner"])
    self.logFile.write(f"\nv_safe\n{self.v_safe}\n")

  def motion_controller(self):
    """ Determine current `self.x` and `self.y`. Compute and save next `self.v` and `self.phi` """

    self.timestamp += poisson(config.poi_avg["motion_controller"])
    dt = self.timestamp - self.lastMcTs # us
    self.lastMcTs = self.timestamp
    self.x += (self.v * np.cos(self.phi) * dt) / (10**6)
    self.y += (self.v * np.sin(self.phi) * dt) / (10**6)
    
    l_FP =  len(self.FP)
    cfp_i, d = None, float('inf') # closest FP index and its distance
    for i in range(l_FP):
      tmp_d = dist({ "x" : (100*self.x), "y" : (100*self.y) }, self.FP[i])
      if tmp_d < d:
        tmp_d = d
        cfp_i = i
    
    if cfp_i == 0 : self.v = self.v_safe[0]
    elif cfp_i == (l_FP - 1) : self.v = self.v_safe[-1]
    else: self.v = 0.5 * ( self.v_safe[cfp_i-1] + self.v_safe[cfp_i] )

    self.lookAhead = self.FP[cfp_i]["e_end"] # always defined (not None)
    self.phi = np.arctan2(
      (config.WPs[self.lookAhead]["y"] * 100) - self.y, # cm
      (config.WPs[self.lookAhead]["x"] * 100) - self.x  # cm
    )

  ######## BROADCASTING STUFF ########
  ####################################

  def broadcast_info(self):
    config.S.broadcast({
      "ID" : self.ID, "timestamp" : self.timestamp, # this TS is broadcast start time
      "v" : self.v,
      "FP" : self.FP, "fpStartTs" : self.fpStartTs # this TS is fpStart start time
    })

  def receive_others_info(self):
    others_Info, self.timestamp = config.S.receive()
    del others_Info[self.ID]
    self.Others_Info = others_Info
    self.logFile.write(f"\nOthers_Info\n{objStr(self.Others_Info)}\n")

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
    self.logFile.write(f"\nOthers_PDG\n{self.Others_PDG}\n")

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

