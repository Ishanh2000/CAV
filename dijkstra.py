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

  d = [float('inf') for i in range(l_WPs)] # distances
  parent = [None for i in range(l_WPs)] # parents
  d[src] = 0 # distance from source = 0
  Q = [i for i in range(l_WPs)] # all vertices in Min-Priority Queue

  while len(Q) > 0:
    min_q_idx = np.array([d[u] for u in Q]).argmin() # get vertex with smallest distance
    u = Q[min_q_idx]
    del Q[min_q_idx]
    for nb in NBs[u]:
      v, wt = nb["idx"], nb["wt"]
      if v in Q:
        alt = d[u] + wt
        if alt < d[v]:
          d[v] = alt
          parent[v] = u
  
  sp = [dst] # list of vertices
  while parent[sp[-1]] != None:
    sp.append(parent[sp[-1]])
  sp.reverse()
  return sp


def compute_future_path(graph, car, d_max):
  """ Computing Future Path of a Car """
  # d_max is passed in metres

  WPs = graph["waypoints"]
  sp = Dijkstra(graph = graph, src = car["closest_wp"], dst = car["dest"])

  # fp, tot_dist = [sp[0]], 0

  # for u in sp[1:]:
  #   edge_len = dist(WPs[fp[-1]], WPs[u])
  #   if (tot_dist + edge_len) >= (100 * d_max): # LHS is in cm
  #     break
  #   fp.append(u)
  #   tot_dist += edge_len

  return sp



graph_json_file = "./samples/eye.json"

if __name__ == "__main__":
  G = []
  with open(graph_json_file) as gjfile:
    G = json.load(gjfile)

  cars = G["cars"]; l_cars = len(cars)

  for ci in range(l_cars):
    cars[ci]["sp"] = Dijkstra(G, cars[ci]["closest_wp"], cars[ci]["dest"])
    # cars[ci]["fp"] = compute_future_path(graph = G, car = cars[ci], d_max = 10)
    print(f"ID = {cars[ci]['id']}, FP = {cars[ci]['sp']}")
  


