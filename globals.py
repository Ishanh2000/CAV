# AUM SHREEGANESHAAY NAMAH|| AUM NAMAH SHIVAAYA||

# Global Variables like graphs are imported using this file

import json

# array[{ "x": float(cm), "y": float(cm) }]
WPs = None

# array[ array[{ "idx" : int, "wt" : float (ms) }]]
NBs = None

# array[{ "x": float(cm), "y": float(cm), "id": int, "color": "#XYZ", "angle": float(rad), "dest": int, "closest_wp": int }]
cars = None

# array (20 x 20) [[ array[ int ] ]]
sectors = None # may be unnecessary

# array (20 x 20) [[ array[ int ] ]]
carsSectors = None # may be unnecesary

def importParentGraph(fname):
  with open(fname) as f:
    G = json.load(f)
    global WPs, NBs, cars, sectors, carsSectors
    WPs = G["waypoints"]
    NBs = G["neighbours"]
    cars = G["cars"]
    sectors = G["sectors"]
    carsSectors = G["carsSectors"]
