# AUM SHREEGANESHAAYA NAMAH|| AUM NAMAH SHIVAAYA||
import os
import config
from CAV import CAV

def test_cav_init():
  print("######## TEST CAV INIT ########")
  print("###############################\n")
  c = CAV({
    "id" : 0,
    "closest_wp" : 0, "dest" : 3,
    "x" : 90, "y" : 906, "angle" : 0.785, "speed" : 10, "acc" : -1  
  })  
  print(c)
  print()


def test_cav_sp_and_fp():
  print("######## TEST CAV SHORTEST PATH AND FUTURE PATH ########")
  print("########################################################\n")
  for car in config.cars:
    cav = CAV(car)
    cav.a_brake = -5
    cav.v_max = 5 # TODO: How and where to compute this correctly?
    cav.compute_future_path()
    print(f"ID = {cav.ID}")
    print(f"Shortest Path = {cav.SP}")
    print(f"Future Path = {cav.FP}")
    print()
  print()


def test_cav_find_conflict_zones():
  print("######## TEST CAV FIND CONFLICT ZONES ########")
  print("##############################################\n")

  CAVs = []
  for car in config.cars:
    cav = CAV(car)
    cav.a_brake = -5
    cav.v_max = 5 # TODO: How and where to compute this correctly?
    cav.compute_future_path()
    CAVs.append(cav)
  
  for i in range(3):
    CAVs[i].broadcast_info()
  
  for i in range(3):
    CAVs[i].receive_others_info()
    CAVs[i].find_conflict_zones_all_CAVs()
    print(f"ID = {CAVs[i].ID}")
    print(CAVs[i].CZ)
    print()
  
  print()


if __name__ == "__main__":
  
  config.importParentGraph(os.path.join(os.getcwd(), "samples/hex2.json"))
  config.startServer() # config.S is now the functioning server

  test_cav_init()
  test_cav_sp_and_fp()
  test_cav_find_conflict_zones()



