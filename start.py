import time
from car import *
from config import N_CARS
from server import get_global_cdg

gTime = 0 # In Microseconds
CARS = {}

def incGTime(v):
    global gTime
    gTime += v
    return gTime

# Spawn car(s)
for crs in range(N_CARS):
    CARS[str(crs)] = car(str(crs))

def thread_func(cav_id):
    cav = CARS[cav_id]
    while not cav.hasReached:
        cav.compute_future_path()
        cav.get_cav_info()
        cav.broadcast_INFO()
        cav.timestamp = gTime
        cav.receive_other_CAV_info()
        cav.find_conflict_zones_all_CAVs()
        cav.broadcast_PDG()
        cav.timestamp = gTime
        cav.receive_other_PDGs()
        cav.set_CDG(get_global_cdg())
        cav.motion_planner()
        cav.motion_controller()

def iterate():

    for crs in range(N_CARS):
        CARS[str(crs)].compute_future_path()
        CARS[str(crs)].get_cav_info()
        CARS[str(crs)].broadcast_INFO()

    for crs in range(N_CARS):
        CARS[str(crs)].timestamp = gTime
        CARS[str(crs)].receive_other_CAV_info()
        CARS[str(crs)].find_conflict_zones_all_CAVs()
        CARS[str(crs)].broadcast_PDG()

    for crs in range(N_CARS):
        CARS[str(crs)].timestamp = gTime
        CARS[str(crs)].receive_other_PDGs()
        CARS[str(crs)].set_CDG(get_global_cdg())

    for crs in range(N_CARS):
        CARS[str(crs)].motion_planner()
        CARS[str(crs)].motion_controller()
        CARS[str(crs)].cont_end = CARS[str(crs)].timestamp