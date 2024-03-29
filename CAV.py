# AUM SHREEGANESHAAYA NAMAH|| AUM NAMAH SHIVAAYA||

# Connected Autonomous Vehicle (CAV) model class file

import numpy as np
import config
from utils import dist, contiguous, objStr
from numpy.random import poisson
from threading import Thread

class CAV:
  iter = None # iteration number
  ID, timestamp = None, 0 # microseconds (will later set to a random positive number)
  logFile, trajFile, trajFileJson = None, None, None # log and trajectory
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
  phi, psi = None, None # heading and steering angle (radians)
  v, v_max, v_safe = None, None, None # m/s
  a_brake = None # m/s2
  a, a_max = None, None # m/s2
  lastMcTs = None # us

  Others_Info, Others_PDG = None, None # will be dictionary with CAV IDs as keys

  def __init__(self, car):
    """ Initialization aka `Booting` """
    self.nbWts = config.NBs
    self.iter = 0
    self.ID = car["id"]
    self.dest = car["dest"]
    self.x, self.y = (car["x"]/100), (car["y"]/100) # LHS is metres
    closest_dist, l_WPs = float('inf'), len(config.WPs)
    for i in range(l_WPs):
      d = dist({ "x" : (self.x * 100), "y" : (self.y * 100) }, config.WPs[i])
      if d < closest_dist:
        self.lookAhead = i
        closest_dist = d
    self.find_shortest_path() # computes `self.SP` from `self.lookAhead` and `self.dest`

    self.v, self.a, self.phi, self.psi = 0, 0, car["angle"], 0
    self.v_max, self.a_max, self.a_brake = car["speed"], car["acc"], car["accBrake"]
    self.timestamp = self.lastMcTs = poisson(config.poi_avg["boot_time"])
    self.thread = Thread(target = self.execute)
    self.logFile = open(f"./logFiles/CAV_{self.ID}.txt", "w")
    self.logFile.write(f"ID = {self.ID}, Boot Time = {self.timestamp}\n")
    self.logFile.write(f"{self.__str__()}\n")
    self.trajFile = open(f"./logFiles/CAV_{self.ID}_traj.csv", "w")
    self.trajFile.write(f"ts(ms),x(cm),y(cm),phi(degrees),v(m/s),lookAhead,lookAheadX(cm),lookAheadY(cm)\n")
    self.trajFileJson = open(f"./logFiles/CAV_{self.ID}_traj.json", "w")
    self.trajFileJson.write(f"[")
  
  def __del__(self):
    """ Destructor """
    if self.logFile and not self.logFile.closed:
      self.logFile.write("\nExiting...\n")
      self.logFile.close()

    if self.trajFile and not self.trajFile.closed:
      self.trajFile.close()
    
    if self.trajFileJson and not self.trajFileJson.closed:
      self.trajFileJson.write("\n]")
      self.trajFileJson.close()

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
    retStr += f"Shortest Path = {self.SP}\n"
    return retStr

  ######## GRAPH ALGORITHMS' STUFF ########
  #########################################

  def hasReachedDest(self):
    """ Return whether destination has been reached. Takes negligible time. """
    dt = self.timestamp - self.lastMcTs # us
    curr_x = (100 * self.x) + ((self.v * np.cos(self.phi) * dt) / (10**4)) # cm
    curr_y = (100 * self.y) + ((self.v * np.sin(self.phi) * dt) / (10**4)) # cm
    return dist({ "x" : curr_x, "y" : curr_y }, config.WPs[self.dest]) <= (config.DEST_REACH_THRESHOLD * 100)

  def find_shortest_path(self):
    """
    [Slow] Dijkstra Algorithm for Shortest Path between `self.lookAhead` and `self.dest`
    Output in `self.SP` (consists only of waypoints's indices in config.WPs). Used only once for now.
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
    
    # self.find_shortest_path() # self.SP gets updated
    # no need to recompute `self.SP`. Simply make `SP` = `self.SP`[`self.lookAhead` ...]
    SP = self.SP[ self.SP.index(self.lookAhead) : ] # takes poisson(config.poi_avg["sp_time"]) time
    self.timestamp += poisson(config.poi_avg["compute_future_path_1"])

    self.fpStartTs = self.timestamp # TS as which FP start position is recorded. used in computing TOA in CZ
    dt = self.timestamp - self.lastMcTs # us
    curr_x = (100 * self.x) + (self.v * np.cos(self.phi) * dt / (10**4)) # cm
    curr_y = (100 * self.y) + (self.v * np.sin(self.phi) * dt / (10**4)) # cm
    
    # must add self position if not close enough to SP[0] (aka self.lookAhead)
    mustAddSelf = dist({ "x" : curr_x, "y" : curr_y }, config.WPs[SP[0]]) >= config.FP_INCLUSION_THRESHOLD
    d_max = self.v_max * ((config.rho/1000) + (self.v_max/np.abs(self.a_brake)))
    l_sp = len(SP)

    fp, total_dist = [], 0.0 # future points, total distance (cm) covered by these future points

    for i in range(0 if mustAddSelf else 1 , l_sp):
      rem = (100.0 * d_max) - total_dist # remaining distance (cm)
      e_start = config.WPs[SP[i-1]] if (i > 0) else { "x" : curr_x, "y" : curr_y } # starting waypoint of edge
      e_end = config.WPs[SP[i]] # ending waypoint of edge
      d = dist(e_start, e_end) # edge length (cm)
      num_fp = np.ceil(np.min([rem, d]) / (config.b * 100))
      for j in range(int(num_fp)):
        fp.append({
          "x" : ( (d-100*j*config.b)*e_start["x"] + 100*j*config.b*e_end["x"] ) / d,
          "y" : ( (d-100*j*config.b)*e_start["y"] + 100*j*config.b*e_end["y"] ) / d,
          "e_start" : SP[i-1] if (i > 0) else None, "e_end" : SP[i] # indicates the edge these granulae come from
        })
      if (rem <= d): break
      if i == (l_sp-1):
        fp.append({
          "x" : e_end["x"], "y" : e_end["y"],
          "e_start" : SP[i-1] if (i > 0) else None, "e_end" : SP[i] # indicates the edge these granulae come from
        })
        break
      total_dist += d

    self.FP = fp # FP consists of granulae (xy coordinates)
    self.timestamp += poisson(config.poi_avg["compute_future_path_2"])
    self.logFile.write(f"\nAPPARENT SHORTEST PATH\n{SP}\n")
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

    self.timestamp += poisson(config.poi_avg["find_conflict_zones"]) # placed here because we require deterministic timing
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
      toa1 = (self.fpStartTs + (10000*d1_begin/(self.v if (self.v != 0) else self.v_max)))
      toa2 = (other["fpStartTs"] + (10000*d2_begin/(v_other if (v_other != 0) else (other["v_max"]))))
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
    
    if l_C > 0: # for now considering only C[0] for PDG
      rowIndex, colIndex = self.carIndices[self.ID], self.carIndices[other_cav_id] # self.ID yields to other_cav_id
      if C[0]["advantage"] == self.ID: rowIndex, colIndex = colIndex, rowIndex # other_cav_id yields to self.ID
      self.PDG[rowIndex][colIndex] = 1

  def construct_CDG(self):
    """ Construct CDG from `self.PDG` and `self.Others_PDG` and store it in `self.CDG` """
    l_carIndices = len(self.carIndices)
    self.CDG = np.zeros((l_carIndices, l_carIndices)) # lower index for lower ID
    self.CDG = np.logical_or(self.CDG, self.PDG)
    for PDG in self.Others_PDG:
      self.CDG = np.logical_or(self.CDG, self.Others_PDG[PDG])
    
    self.timestamp += poisson(config.poi_avg["construct_CDG"])
    self.logFile.write(f"\nCDG\n{self.CDG}\n")

  def DFS(self, CDG, visited, parent, start, n):
    """ Depth First Search (DFS) to detect only ONE cycle """

    visited[start] = -1
    cycle = []
    # flag = 0
    for i in range(n):
      if CDG[start][i] == True:
        if visited[i] == 0:
          parent[i] = start
          cycle = self.DFS(CDG, visited, parent, i, n)
          if cycle != []: return cycle
        elif visited[i] == -1: # cycle detected
          j = start
          while(parent[j]!=i):
            cycle.append(j)
            j = parent[j]
          cycle.append(j)
          cycle.append(i)
          return cycle

    visited[start] = 1
    return cycle

  def findCycles(self, CDG):
    """ Finding cycle: Function is expected to find exactly one cycle and return the nodes invovled in the cycle """

    n = np.array(CDG).shape[0]
    visited, parent = np.zeros(n), np.arange(n)

    for start in range(int(n/n-1)):
      if visited[start] == 0:
        cycle = self.DFS(CDG, visited, parent, start, n)
        print("Cyle: ", cycle)
        if(cycle != []):
          return cycle

    return []

  def resolveCycle(self, CDG, cycle, averagedTOA):
    min_time, leader = averagedTOA[cycle[0]], cycle[0]
    for vehicle in cycle:
      if averagedTOA[vehicle] < min_time: min_time, leader = averagedTOA[vehicle], vehicle
    
    n = CDG.shape[0]
    for i in range(n):
      if CDG[i][leader]: CDG[i][leader], CDG[leader][i] = False, True
    
    return CDG

  def ResolveDeadlock(self, averaged_TOA=[]):
    cycles = self.findCycles(self.CDG)

    while cycles != []:
      self.resolveCycle(self.CDG, cycles, averaged_TOA)
      cycles = self.findCycles(self.CDG)

    return self.CDG

  def deadlock_resolution(self):
    """ Detect any deadlocks found in `self.CDG` and resolve them usign DFS. Will complete this later. """

    self.ResolveDeadlock()
    self.timestamp += poisson(config.poi_avg["deadlock_resolution"])

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
      
      # self.logFile.write(f"\nother_cav_id = {other_cav_id}\nd_c = {d_c}\n")
      
      l_d_c = len(d_c)
      rho = config.rho / 1000.0 # s
      b = np.abs(self.a_brake) # m/s2
      for i in range(l_d_c):
        self.v_safe[i] = min(self.v_safe[i], self.v_max, ((( ((b*rho)**2) + (2*b*d_c[i]/100) )**0.5) - (b * rho)))

    self.timestamp += poisson(config.poi_avg["motion_planner"])
    self.logFile.write(f"\nv_safe\n{self.v_safe}\n")

  def PID(self, t=0):
    """ Simulate PID controller and vehicle (plant) for time `t` """

    if t == 0: return
    
    v_ref, phi_ref = self.v, self.phi
    dt = (t / config.PID_ITERS) / 1e6 # t is in microseconds (us)

    for _ in range(config.PID_ITERS):
      ev, ephi = (v_ref - self.v), (phi_ref - self.phi)
      ev_dot, ephi_dot = ((ev-self.v) / dt), ((ephi-self.phi) / dt)
      ev_sum, ephi_sum = (self.v + (ev * dt)), (self.phi + (ephi * dt))

      a, psi = self.a, self.psi

      self.a = (config.kP_a * ev) + (config.kI_a * ev_sum) + (config.kD_a * ev_dot)
      if self.a < (-self.a_max): self.a = -self.a_max
      elif self.a > self.a_max: self.a = self.a_max
      self.psi = (config.kP_psi * ev) + (config.kI_psi * ephi_sum) + (config.kD_psi * ephi_dot)
      if self.psi < (-np.pi/8): self.psi = -np.pi/8
      elif self.psi > (np.pi/8): self.psi = np.pi/8

      x = self.x + (self.v * np.cos(self.phi) * dt)
      y = self.y + (self.v * np.sin(self.phi) * dt)
      phi = self.phi + (self.v * np.tan(psi) * dt / config.L)
      v = self.v + (a * dt)
      if v < 0: v = 0
      # self.x, self.y, self.phi, self.v = x, y, phi, v

      x = self.x + (self.v * np.cos(self.phi) * dt)
      y = self.y + (self.v * np.sin(self.phi) * dt)
      phi = phi_ref
      v = v_ref
      if v < 0: v = 0
      self.x, self.y, self.phi, self.v = x, y, phi, v

  def motion_controller(self):
    """ Determine current `self.x` and `self.y`. Compute and save next `self.v` and `self.phi` """

    self.timestamp += poisson(config.poi_avg["motion_controller"])
    dt = self.timestamp - self.lastMcTs # us
    self.lastMcTs = self.timestamp

    self.PID(dt)
    
    l_FP =  len(self.FP)
    cfp_i, d = None, float('inf') # closest FP index and its distance
    for i in range(l_FP):
      tmp_d = dist({ "x" : (100*self.x), "y" : (100*self.y) }, self.FP[i])
      if tmp_d < d:
        d = tmp_d
        cfp_i = i
    self.logFile.write(f"\nclosest_fp = {cfp_i} : {self.FP[cfp_i]}\n")
    
    if cfp_i == 0 : self.v = self.v_safe[0]
    elif cfp_i == (l_FP - 1) : self.v = self.v_safe[-1]
    else: self.v = 0.5 * ( self.v_safe[cfp_i-1] + self.v_safe[cfp_i] )

    self.lookAhead = self.FP[cfp_i]["e_end"] # always defined (not None) and a part of self.SP
    self.phi = np.arctan2(
      config.WPs[self.lookAhead]["y"] - (self.y * 100), # cm
      config.WPs[self.lookAhead]["x"] - (self.x * 100)  # cm
    )

    self.logFile.write(f"\nTS = lastMcTs = {self.timestamp} us\n")
    self.logFile.write(f"\nx = {self.x} m, y = {self.y} m\n")
    self.logFile.write(f"\nv = {self.v} m/s, phi = {self.phi} radians\n")
    tmp = config.WPs[self.lookAhead]
    self.logFile.write(f"\nlookAhead = {self.lookAhead} : ({tmp['x']/100} m, {tmp['y']/100} m)\n")
    self.trajFile.write(f"{self.timestamp/1000},{self.x*100},{self.y*100},{self.phi*180/np.pi},{self.v},{self.lookAhead},{tmp['x']},{tmp['y']}\n")
    self.trajFileJson.write(f"{',' if (self.iter != 0) else ''}\n  " + '{')
    self.trajFileJson.write(f" \"ts\" : {self.timestamp/1000},")
    self.trajFileJson.write(f" \"x\" : {self.x*100}, \"y\" : {self.y*100},")
    self.trajFileJson.write(f" \"phi\" : {self.phi * 180.0 / np.pi}, \"v\" : {self.v} " + '}')

  ######## BROADCASTING STUFF ########
  ####################################

  def broadcast_info(self):
    config.S.broadcast({
      "ID" : self.ID, "timestamp" : self.timestamp, # this TS is broadcast start time
      "v" : self.v, "v_max" : self.v_max,
      "FP" : self.FP, "fpStartTs" : self.fpStartTs # this TS is fpStart start time
    })

  def receive_others_info(self):
    others_Info, self.timestamp = config.S.receive()
    del others_Info[self.ID]
    self.Others_Info = others_Info
    # self.logFile.write(f"\nOthers_Info\n{objStr(self.Others_Info)}\n")

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
    # self.logFile.write(f"\nOthers_PDG\n{self.Others_PDG}\n")

  def execute(self):

    while True: # main loop
    
      self.logFile.write(f"\n########################################\n")
      self.logFile.write(f"\n######## ITERATION {self.iter}: ########\n")
      self.logFile.write(f"\n########################################\n")

      if self.hasReachedDest():
        config.S.dontCare()
        self.logFile.write(f"TS-{self.timestamp}: Reached Destination.\n")
        self.logFile.write(f"Iterations Executed: {self.iter + 1}\n")
        exit(0)      

      self.compute_future_path()
      self.broadcast_info()
      self.receive_others_info()
      self.find_conflict_zones_all_CAVs()
      self.broadcast_PDG()
      self.receive_others_PDGs()
      self.construct_CDG()
      self.deadlock_resolution()
      self.motion_planner()
      self.motion_controller()

      # ############################################################################################
      # ######## near the point (7.03 m, 5.03 m) let the slow vehicle increase its velocity ########
      # ############################################################################################

      # if self.ID == 2:
      #   if dist({ "x" : self.x, "y" : self.y }, { "x" : 7.03, "y" : 5.03 }) <= 0.7:
      #     self.v_max = 8

      self.iter += 1

