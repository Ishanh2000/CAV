# AUM SHREEGANESHAYA NAMAH||

################ IMPORTS ################
import os, globals
from CAV import CAV

parent_graph_file = os.path.join(os.getcwd(), "samples/eye.json")

try:
  globals.importParentGraph(parent_graph_file)
except:
  print("ERROR: Could not load parent graph. Exiting...")
  exit(-1)

# graph should be accessible to all other files now
CAVs = []
for c in globals.cars:
  cav = CAV()
  cav.ID, cav.timestamp = c["id"], 0 # timestamp may be later changed to a random positive number
  cav.wp, cav.dest = c["closest_wp"], c["dest"]
  cav.nbWts = globals.NBs
  cav.x, cav.y = (c["x"]/100), (c["y"]/100) # LHS is metres
  cav.phi, cav.v, cav.a = c["angle"], c["speed"], c["acc"]
  CAVs.append(cav)

for cav in CAVs:
  print(cav)
  print()

# print(globals.WPs); print(globals.NBs); print(globals.cars); print(globals.sectors); print(globals.carsSectors)

