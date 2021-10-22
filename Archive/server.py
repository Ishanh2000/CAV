import redis
import json
import time
import random
from config import N_CARS, WAIT_T
from start import incGTime

rINFO = redis.Redis(host='localhost', port=6379, db=0)
rPDG  = redis.Redis(host='localhost', port=6379, db=1)
GLOBAL_CDG = {}

def broadcast(info, car_sign, tp):
    global GLOBAL_CDG 
    GLOBAL_CDG = {}
    rCache = rINFO if tp == 0 else rPDG
    rCache.set(car_sign, json.dumps(info))

def receive(tp, car_sign = "OPTIONAL"):
    rCache = rINFO if tp == 0 else rPDG
    indices = rCache.scan()[1]
    arrTime = time.time()
    while N_CARS != len(indices): 
        indices = rCache.scan()[1]
        if time.time() - arrTime > WAIT_T * 1e-6:
            print("Failed Access, requesting to terminate car: ", car_sign)
            return { "STATUS": -1 }
    
    ret_js = {}
    for ind in indices:
        ret_js[ind.decode('utf-8')] = json.loads(rCache.get(ind))
    
    return ret_js

def get_global_cdg():
    global GLOBAL_CDG 
    if GLOBAL_CDG.get('active', 0):
        return GLOBAL_CDG
    GLOBAL_CDG = generate_cdg(receive(1))
    GLOBAL_CDG["active"] = 1
    return GLOBAL_CDG