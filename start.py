import json
import time
from scripts.car import *

with open("config.json", "r") as cnfgjs:
    CONFIG = json.load(cnfgjs)

gTime = 0
CARS = {}

# Spawn car(s)
for crs in range(CONFIG["N_CARS"]):
    CARS[str(crs)] = car(str(crs))

def iterate():

    for crs in range(CONFIG["N_CARS"]):
        CARS[str(crs)].compute_future_path()
        CARS[str(crs)].get_cav_info()
        CARS[str(crs)].broadcast_INFO()

    for crs in range(CONFIG["N_CARS"]):
        CARS[str(crs)].local_ti = gTime
        CARS[str(crs)].receive_other_CAV_info()
        # Code for Finding Conflict Zones #
        #
        #
        # End #
        CARS[str(crs)].broadcast_PDG()

    for crs in range(CONFIG["N_CARS"]):
        CARS[str(crs)].local_ti = gTime
        CARS[str(crs)].receive_other_PDGs()

    # Construct CDG #
    #
    # End #

    for crs in range(CONFIG["N_CARS"]):
        # Motion Planner #
        # Motion Controller #
        pass