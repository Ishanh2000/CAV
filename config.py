# AUM SHREEGANESHAAY NAMAH|| AUM NAMAH SHIVAAYA||

# Global Variables and Constant Parameters like graphs are imported using this file

import json
from server2 import Server2 as Server

b = 0.5 # granularity, metres (required for computing FP)
CLOCK_ACCURACY = 50 # microseconds (required for CZ detection)
T = 50 # milliseconds (periodic broadcast time period)
rho = 100 # milliseconds (worst end to end delay)
d_th = 0.63 # metres
S : Server = None # will initialize later

# Average computing times (Poisson distribution) in microseconds (us)
poi_avg = {
  "boot_time" : 1000, # 1 ms
  "compute_future_path" : 1000, # 1 ms
  "find_conflict_zones" : 1000, # 1 ms
  "construct_CDG" : 1000, # 1 ms
  "motion_planner" : 1000, # 1 ms
  "motion_controller" : 1000, # 1 ms
  "server" : 1000, # 1 ms
}

# modifications by Utkarsh Gupta
N_CARS = 6
WAIT_T = 1e6 # In Microseconds
CHANNEL_INFO, CHANNEL_PDG = 0, 1


# radius within which CAV's position is considered same as the closest waypoint's position
# affects whether or not CAV's position is used in FP computation)
FP_INCLUSION_THRESHOLD = 0 # metres

def importParentGraph(fname):
  with open(fname) as f:
    G = json.load(f)
    global WPs, NBs, cars, sectors, carsSectors
    WPs = G["waypoints"]
    NBs = G["neighbours"]
    cars = G["cars"]
    sectors = G["sectors"]
    carsSectors = G["carsSectors"]

def startServer():
  global S, cars
  S = Server(carNum = len(cars))









#### DESCRIPTION OF GRAPH ####

# WPs = array[{ "x": float(cm), "y": float(cm) }]
# NBs = array[ array[{ "idx" : int, "wt" : float (ms) }]]
# cars = array[{
#   "id": int, "color": "#XYZ",
#   "x": float(cm), "y": float(cm), "angle": float(rad), "speed" : float(m/s), "acc" : float(m/s2),
#   "dest": int, "closest_wp": int
# }]
# sectors = array (20 x 20) [[ array[ int ] ]]
# carsSectors = array (20 x 20) [[ array[ int ] ]]
