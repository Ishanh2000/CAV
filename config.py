# AUM SHREEGANESHAAY NAMAH|| AUM NAMAH SHIVAAYA||

# Global Variables and Constant Parameters like graphs are imported using this file

import json

b = 0.5 # granularity, metres (required for computing FP)

CLOCK_ACCURACY = 50 # microseconds (required for CZ detection)

T = None

rho = None

t_b = None

N_CARS = 6

WAIT_T = 100

CHANNEL_INFO, CHANNEL_PDG = 0, 1

d_th = 0.63 # metres


def importParentGraph(fname):
  with open(fname) as f:
    G = json.load(f)
    global WPs, NBs, cars, sectors, carsSectors
    WPs = G["waypoints"]
    NBs = G["neighbours"]
    cars = G["cars"]
    sectors = G["sectors"]
    carsSectors = G["carsSectors"]

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
