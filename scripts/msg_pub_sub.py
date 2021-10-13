import redis
import json
import time

with open("../config.json", "r") as cnfgjs:
    CONFIG = json.load(cnfgjs)

rINFO = redis.Redis(host='localhost', port=6379, db=0)
rPDG  = redis.Redis(host='localhost', port=6379, db=1)

def broadcast(info, car_sign, tp):

    rCache = rINFO if tp == 0 else rPDG
    rCache.set(car_sign, json.dumps(info))
    
def receive(tp, car_sign = "OPTIONAL"):

    rCache = rINFO if tp == 0 else rPDG
    indices = rCache.scan()[1]
    arrTime = time.time()
    while CONFIG["N_CARS"] != len(indices): 
        indices = rCache.scan()[1]
        if time.time() - arrTime > CONFIG["WAIT_T"]:
            print("Failed Access, requesting to terminate car: ", car_sign)
            return {"STATUS": -1}
    
    ret_js = {}
    for ind in indices:
        ret_js[ind.decode('utf-8')] = json.loads(rCache.get(ind))
    
    return ret_js