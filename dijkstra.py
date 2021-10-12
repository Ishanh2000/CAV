# AUM SHREEGANESHAAYA NAMAH||
import json
from os import close, read
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
    print(num_fp)
    for j in range(int(num_fp)):
      fp.append({
        "x" : ( (d-100*j*b)*e_start["x"] + 100*j*b*e_end["x"] ) / d,
        "y" : ( (d-100*j*b)*e_start["y"] + 100*j*b*e_end["y"] ) / d,
      })
    if (rem <= d):
      break
    if i == (l_sp-1):
      fp.append(e_end)
      break
    total_dist += d

  return fp, sp


graph_json_file = "./samples/hex.json"

if __name__ == "__main__":
  G = []
  with open(graph_json_file) as gjfile:
    G = json.load(gjfile)

  cars = G["cars"]; l_cars = len(cars)

  for ci in range(l_cars-1):
    cars[ci]["fp"], cars[ci]["sp"] = compute_future_path(graph = G, car = cars[ci], d_max = 10)
    print(f"ID = {cars[ci]['id']}, SP = {cars[ci]['sp']}")
    print(f"FP = {cars[ci]['fp']}")
    print()


