# AUM SHREEGANESHAAAYA NAMAH|| AUM NAMAH SHIVAAYA||
import os, config
from CAV import CAV

parent_graph_file = os.path.join(os.getcwd(), "samples/eye.json")

try:
  config.importParentGraph(parent_graph_file)
except:
  print("ERROR: Could not load parent graph. Exiting...")
  exit(-1)

# graph should be accessible to all other files now

CAVs = []

for car in config.cars:
  CAVs.append(CAV(car)) # can even start execution here itself

for cav in CAVs:
  print(cav)
  print()

