# AUM SHREEGANESHAAYA NAMAH||
import json
import numpy as np


def dist(p, q):
  """ Euclidean Distance between point `p` and `q` """
  return np.sqrt((p["x"] - q["x"])**2 + (p["y"] - q["y"])**2)


def Dijkstra(graph, src, dst):
  """ Dijkstra Algorithm for Shortest Path between WP[`src`] and WP[`dst`] """

  l_WPs = len(graph["waypoints"])
  NBs = graph["neighbours"]

  cost = [float('inf') for i in range(l_WPs)] # costs are in time (milliseconds)
  parent = [None for i in range(l_WPs)] # parents
  cost[src] = 0 # cost from source = 0
  Q = [i for i in range(l_WPs)] # all vertices in Min-Priority Queue

  while len(Q) > 0:
    min_q_idx = np.array([cost[u] for u in Q]).argmin() # get vertex with smallest distance
    u = Q[min_q_idx]
    del Q[min_q_idx]
    for nb in NBs[u]:
      v, wt = nb["idx"], nb["wt"]
      if v in Q:
        alt = cost[u] + wt
        if alt < cost[v]:
          cost[v] = alt
          parent[v] = u
  
  sp = [dst] # list of vertices
  while parent[sp[-1]] != None:
    sp.append(parent[sp[-1]])
  sp.reverse()
  return sp

b = 0.5 # granularity in metres

def compute_future_path(graph, car, d_max):
  """ Computing Future Path of a Car """
  # d_max is passed in metres

  WPs = graph["waypoints"]
  sp = Dijkstra(graph = graph, src = car["closest_wp"], dst = car["dest"])
  l_sp = len(sp)

  fp, total_dist = [], 0.0 # future points, total distance (cm) covered by these future points
  for i in range(1 , l_sp):
    rem = (100.0 * d_max) - total_dist # remaining distance (cm)
    e_start, e_end = WPs[sp[i-1]], WPs[sp[i]] # points of edge
    d = dist(e_start, e_end) # edge length (cm)
    num_fp = np.ceil(np.min([rem, d]) / (b * 100))
    for j in range(int(num_fp)):
      fp.append({
        "x" : ( (d-100*j*b)*e_start["x"] + 100*j*b*e_end["x"] ) / d,
        "y" : ( (d-100*j*b)*e_start["y"] + 100*j*b*e_end["y"] ) / d,
        "e_start" : sp[i-1], "e_end" : sp[i], # indicates which edge these gaypoints were a part of
      })
    if (rem <= d):
      break
    if i == (l_sp-1):
      fp.append({ "x" : e_end["x"], "y" : e_end["y"], "e_start" : sp[i-1], "e_end" : sp[i] })
      break
    total_dist += d

  return fp, sp # FP consists of gaypoints, SP consists of waypoints


def contiguous(zone, pair):
  zv1, zv2 = zone["v1"], zone["v2"]
  pv1, pv2 = pair["v1"][0], pair["v2"][0]

  if (pv1 < zv1[0]) or (zv1[-1] < pv1):
    if pv1 == (zv1[0] - 1):
      zv1 = [pv1] + zv1
    elif pv1 == (zv1[-1] + 1):
      zv1.append(pv1)
    else:
      return None
  
  if (pv2 < zv2[0]) or (zv2[-1] < pv2):
    if pv2 == (zv2[0] - 1):
      zv2 = [pv2] + zv2
    elif pv2 == (zv2[-1] + 1):
      zv2.append(pv2)
    else:
      return None
  
  return { "v1" : zv1, "v2" : zv2 }

CLOCK_ACCURACY = 50 # microseconds


def find_conflict_zones(id1, vel_1, ts1, fp1, id2, vel_2, ts2, fp2, d_th):
  """
  Find conflict zones between future paths (consists of gaypoints and associated
  edges) `fp1` and `fp2`. Als make Partial Dependncy Graph (PDG) in parallel.
  """
  # UNITS: [vel_1] = [vel_2] = m/s, [ts1] = [ts2] = microseconds, [d_th] = metres
  
  l_fp1, l_fp2 = len(fp1), len(fp2)
  mp1, mp2 = [], [] # edge midpoints (mp[i] is midpoint of fp[i] and fp[i+1])
  for i in range(1, l_fp1):
    tstart, tend = fp1[i-1], fp1[i]
    mp1.append({ "x" : (tstart["x"] + tend["x"]) / 2, "y" : (tstart["y"] + tend["y"]) / 2 })
  for i in range(1, l_fp2):
    tstart, tend = fp2[i-1], fp2[i]
    mp2.append({ "x" : (tstart["x"] + tend["x"]) / 2, "y" : (tstart["y"] + tend["y"]) / 2 })
  
  # calculate conflicting pairs first
  C = []
  for i in range(l_fp1-1):
    for j in range(l_fp2-1):
      if dist(mp1[i], mp2[j]) < (d_th * 100): # LHS is in cm
        C.append({ "v1" : [i], "v2" : [j] })

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
    v1, d1_begin, d1_end = C[i]["v1"], 0, 0 # d1_begin, d1_end in cm
    p, q, special = v1[0], v1[-1], (len(v1) <= 1)
    for k in range(p):
      d1_begin += dist(fp1[k], fp1[k+1])  
    d1_end = d1_begin
    for k in range(p, q):
      d1_end += dist(fp1[k], fp1[k+1])
    d1_begin += 0 if special else (0.5 * dist(fp1[p], fp1[p+1]))
    d1_end += (1 if special else 0.5) * dist(fp1[q], fp1[q+1])
    v1 = [p, p+1] if special else v1[1:]

    v2, d2_begin, d2_end = C[i]["v2"], 0, 0 # d2_begin, d2_end in cm
    p, q, special = v2[0], v2[-1], (len(v2) <= 1)
    for k in range(p):
      d2_begin += dist(fp2[k], fp2[k+1])
    d2_end = d2_begin
    for k in range(p, q):
      d2_end += dist(fp2[k], fp2[k+1])
    d2_begin += 0 if special else (0.5 * dist(fp2[p], fp2[p+1]))
    d2_end += (1 if special else 0.5) * dist(fp2[q], fp2[q+1])
    v2 = [p, p+1] if special else v2[1:]

    toa1, toa2 = (ts1 + (10000*d1_begin/vel_1)), (ts2 + (10000*d2_begin/vel_2)) # Times of Arrival (microseconds)
    diff, adv = (toa2-toa1), None
    if np.abs(diff) <= CLOCK_ACCURACY:
      adv = id1 if (id1 < id2) else id2
    else:
      adv = id1 if (diff > 0) else id2
    
    C[i] = {
      id1 : { "begin" : (d1_begin/100), "end" : (d1_end/100), "toa" : toa1, "cz" : v1 },
      id2 : { "begin" : (d2_begin/100), "end" : (d2_end/100), "toa" : toa2, "cz" : v2 },
      "advantage" : adv
    }

  # Calculate PDG

  return C

graph_json_file = "./samples/hex.json"

def testContiguous():
  print(contiguous(
    zone = { "v1" : [0, 1, 2, 3], "v2" : [8, 9] },
    pair = { "v1" : [4], "v2" : [7] },
  ))
  print(contiguous(
    zone = { "v1" : [0, 1, 2, 3], "v2" : [8, 9] },
    pair = { "v1" : [3], "v2" : [6] },
  ))
  print(contiguous(
    zone = { "v1" : [0, 1, 2, 3], "v2" : [8, 9] },
    pair = { "v1" : [2], "v2" : [10] },
  ))

if __name__ == "__main__":
  # G = []
  # with open(graph_json_file) as gjfile:
  #   G = json.load(gjfile)

  # cars = G["cars"]; l_cars = len(cars)

  # for ci in range(l_cars):
  #   cars[ci]["fp"], cars[ci]["sp"] = compute_future_path(graph = G, car = cars[ci], d_max = 5)
  #   print(f"ID = {cars[ci]['id']}, SP = {cars[ci]['sp']}")
  #   print(f"FP = {cars[ci]['fp']}")
  #   print()
  
  # find_conflict_zones(cars[0]["fp"], cars[1]["fp"], d_th = 2)
  # testContiguous()
  fp1 = [
    { "x": 140, "y": 135 },
    { "x": 210, "y": 203 },
    { "x": 297, "y": 209 },
    { "x": 404, "y": 220 },
    { "x": 498, "y": 216 },
    { "x": 573, "y": 201 },
    { "x": 603, "y": 188 },
    { "x": 713, "y": 175 },
    { "x": 838, "y": 193 },
    { "x": 895, "y": 203 },
    { "x": 1031, "y": 216 },
    { "x": 1119, "y": 213 },
    { "x": 962, "y": 213 }
  ]
  fp2 = [
    { "x": 143, "y": 321 },
    { "x": 211, "y": 274 },
    { "x": 307, "y": 263 },
    { "x": 401, "y": 264 },
    { "x": 486, "y": 265 },
    { "x": 550, "y": 280 },
    { "x": 616, "y": 314 },
    { "x": 711, "y": 372 },
    { "x": 788, "y": 397 },
    { "x": 863, "y": 368 }, 
    { "x": 897, "y": 325 }, 
    { "x": 944, "y": 267 }, 
    { "x": 996, "y": 232 },
    { "x": 1040, "y": 174 },
    { "x": 1105, "y": 124 }
  ]
  # print(fp1)
  # print(fp2)
  C = find_conflict_zones(
    id1 = 0, vel_1 = 2, ts1 = 0, fp1 = fp1,
    id2 = 1, vel_2 = 2, ts2 = 0, fp2 = fp2,
    d_th = 0.63
  )
  print(len(C))
  print()

  for c in C:
    print(c)
    print()

