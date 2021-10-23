# AUM SHREEGANESHAAY NAMAH|| AUM NAMAH SHIVAAYA||

# Common Utility Functions reside here.

import numpy as np
import json

def dist(p, q):
  """ Euclidean Distance between point `p` and `q` (usually accepts/returns in cm) """
  return np.sqrt((p["x"] - q["x"])**2 + (p["y"] - q["y"])**2)


def contiguous(zone, pair):
  """
  Tries to merge `zone` and `pair` if the
  vehicles in them lie on conitguous indices
  """
  zv1, zv2 = zone["self"], zone["other"]
  pv1, pv2 = pair["self"][0], pair["other"][0]

  if (pv1 < zv1[0]) or (zv1[-1] < pv1):
    if pv1 == (zv1[0] - 1):
      zv1 = [pv1] + zv1
    elif pv1 == (zv1[-1] + 1):
      zv1.append(pv1)
    else:
      return None
  
  if (pv2 < zv2[0]) or (zv2[-1] < pv2):
    if pv2 == (zv2[0] - 1):
      zv2 = [pv2] + zv2
    elif pv2 == (zv2[-1] + 1):
      zv2.append(pv2)
    else:
      return None
  
  return { "self" : zv1, "other" : zv2 }

def objStr(obj):
  return json.dumps(obj, indent=2)

def test_contiguous():
  """ Test for computing Contiguous Zones """
  print("######## TEST FUNCTION \"CONTIGUOUS\" ########")
  print("##############################################\n")  

  combinedZone = contiguous(
    zone = { "self" : [0, 1, 2, 3], "other" : [8, 9] },
    pair = { "self" : [4], "other" : [7] },
  )
  print(f"TEST 1: {combinedZone}\n")

  combinedZone = contiguous(
    zone = { "self" : [0, 1, 2, 3], "other" : [8, 9] },
    pair = { "self" : [3], "other" : [6] },
  )
  print(f"TEST 2: {combinedZone}\n")

  combinedZone = contiguous(
    zone = { "self" : [0, 1, 2, 3], "other" : [8, 9] },
    pair = { "self" : [2], "other" : [10] },
  )
  print(f"TEST 3: {combinedZone}\n")

  print()


if __name__ == "__main__":
  test_contiguous()
