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
    cav.a_brake, cav.v_max = -5, 5
    cav.compute_future_path()
    print(f"ID = {cav.ID}")
    print(f"Shortest Path = {cav.SP}")
    print(f"Future Path = {cav.FP}")
    print()
  print()


def test_cav_find_conflict_zones():
  print("######## TEST CAV FIND CONFLICT ZONES ########")
  print("##############################################\n")

  CAVs, l_cars = [], len(config.cars)
  for car in config.cars:
    cav = CAV(car)
    cav.a_brake, cav.v_max = -5, 5
    cav.compute_future_path()
    CAVs.append(cav)
  
  for i in range(l_cars):
    CAVs[i].broadcast_info()
  
  for i in range(l_cars):
    CAVs[i].receive_others_info()
    CAVs[i].find_conflict_zones_all_CAVs()
    print(f"ID = {CAVs[i].ID}")
    print(CAVs[i].CZ)
    print()
  
  print()


def test_cav_upto_construct_CDG():
  print("######## TEST CAV UPTO CONSTRUCT CDG #########")
  print("##############################################\n")

  CAVs, l_cars = [], len(config.cars)
  for car in config.cars:
    cav = CAV(car)
    cav.a_brake, cav.v_max = -5, 10
    cav.compute_future_path()
    CAVs.append(cav)
  
  for i in range(l_cars):
    CAVs[i].broadcast_info()
  
  for i in range(l_cars):
    CAVs[i].receive_others_info()
    CAVs[i].find_conflict_zones_all_CAVs()

  for i in range(l_cars):
    CAVs[i].broadcast_PDG()

  for i in range(l_cars):
    CAVs[i].receive_others_PDGs()
    CAVs[i].construct_CDG()
    print(f"ID = {CAVs[i].ID}")
    print(f"PDG =", CAVs[i].PDG)
    print(f"Others_PDGs =", CAVs[i].Others_PDG)
    print(f"CDG =", CAVs[i].CDG)
    print()
  
  print()


def test_cav_upto_motion_controller():
  print("######## TEST CAV UPTO MOTION CONTROLLER #########")
  print("##############################################\n")

  CAVs, l_cars = [], len(config.cars)
  for car in config.cars:
    cav = CAV(car)
    cav.a_brake, cav.v_max = -5, 10
    CAVs.append(cav)
  
  for i in range(l_cars):
    CAVs[i].compute_future_path()
    CAVs[i].broadcast_info()
  
  for i in range(l_cars):
    CAVs[i].receive_others_info()
    CAVs[i].find_conflict_zones_all_CAVs()

  for i in range(l_cars):
    CAVs[i].broadcast_PDG()

  for i in range(l_cars):
    CAVs[i].receive_others_PDGs()
    CAVs[i].construct_CDG()
    CAVs[i].deadlock_resolution()
    CAVs[i].motion_planner()
    CAVs[i].motion_controller()
  
  print("TEST COMPLETE SEE LOG FILES.\n")


def test_cav_full_cycle():
  print("######## TEST CAV FULL CYCLE #########")
  print("######################################\n")

  CAVs, l_cars = [], len(config.cars)
  for car in config.cars:
    cav = CAV(car)
    cav.a_brake, cav.v_max = -5, 10
    CAVs.append(cav)

  for j in range(15):
    for i in range(l_cars):
      CAVs[i].compute_future_path()
      CAVs[i].broadcast_info()
    
    for i in range(l_cars):
      CAVs[i].receive_others_info()
      CAVs[i].find_conflict_zones_all_CAVs()

    for i in range(l_cars):
      CAVs[i].broadcast_PDG()

    for i in range(l_cars):
      CAVs[i].receive_others_PDGs()
      CAVs[i].construct_CDG()
      CAVs[i].deadlock_resolution()
      CAVs[i].motion_planner()
      CAVs[i].motion_controller()
  
  print("TEST COMPLETE SEE LOG FILES.\n")


def test_cav_execute():
  print("######## TEST CAV EXECUTE #########")
  print("######################################\n")

  CAVs, l_cars = [], len(config.cars)  
  for car in config.cars: # Initiialize
    cav = CAV(car)
    # cav.a_brake, cav.v_max = -10, 10
    # cav.a_brake, cav.v_max = -10, (15 if (car["id"] == 0) else 2) # straight_2_block: second is immovable (do not allow to reach dest)
    # cav.a_brake, cav.v_max = -10, (10 if (car["id"] == 0) else 5) # straight_2: second is slower
    cav.a_brake, cav.v_max = -10, (15 if (car["id"] == 0) else 2) # sharp_curve_2: second is slower
    CAVs.append(cav)
  
  for i in range(l_cars): # Start
    CAVs[i].thread.start()

  for i in range(l_cars): # Wait for End
    CAVs[i].thread.join()
  
  print("TEST COMPLETE SEE LOG FILES.\n")



if __name__ == "__main__":
  
  # straight_1,  curve_1, sharp_curve_1, straight_2, sharp_curve_2, straight_2_block
  config.importParentGraph(os.path.join(os.getcwd(), "samples/sharp_curve_2.json"))
  config.startServer() # config.S is now the functioning server

  # test_cav_init()
  # test_cav_sp_and_fp()
  # test_cav_find_conflict_zones()
  # test_cav_upto_construct_CDG()
  # test_cav_upto_motion_controller()
  # test_cav_full_cycle()
  test_cav_execute()



