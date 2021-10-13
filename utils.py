# AUM SHREEGANESHAAY NAMAH|| AUM NAMAH SHIVAAYA||

# Common Utility Functions reside here.

import numpy as np

def dist(p, q): # Utility Function
  """ Euclidean Distance between point `p` and `q` """
  return np.sqrt((p["x"] - q["x"])**2 + (p["y"] - q["y"])**2)
