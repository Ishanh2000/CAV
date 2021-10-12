# AUM SHREEGANESHAAYA NAMAH||
import json
from os import close, read
import numpy as np

def Dijkstra(G, src, dst):
  """ Dijkstra Algorithm for Shortest Path between WP[`src`] and WP[`dst`] """

  l_WPs = len(G["waypoints"])
  NBs = G["neighbours"]

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
  
  path = [dst] # list of vertices
  while parent[path[-1]] != None:
    path.append(parent[path[-1]])
  path.reverse()
  return path, d[dst] # second is total weight

graph_json_file = "./samples/graph.json"

if __name__ == "__main__":
  G = []
  with open(graph_json_file) as gjfile:
    G = json.load(gjfile)

  cars = G["cars"]; l_cars = len(cars)

  for ci in range(l_cars):
    cars[ci]["sp"], cars[ci]["sp_wt"] = Dijkstra(G, cars[ci]["closest_wp"], cars[ci]["dest"])
    # FP = ??
    print(f"ID = {cars[ci]['id']}, Path = {cars[ci]['sp']}, Path Length = {cars[ci]['sp_wt']}")
  


