# AUM SHREEGANESHAAY NAMAH|| AUM NAMAH SHIVAAYA||

# Connected Autonomous Vehicle (CAV) model class file

import os
import globals

class CAV:
  ID, timestamp = None, None # microseconds

  # Graph Related Members
  wp, dest = None, None
  nbWts = None # similar to graph["neighbours"], but weights get updated in each iteration
  SP = None # waypoints indices
  FP = None # granula (FP) indices
  CZ = [] # Conflict Zones

  # Dynamics Related Members
  x, y = None, None # m
  phi = None # radians
  v, v_max = None, None # m/s  (check if v_max is parameter)
  a, a_max = None, None # m/s2 (check if a_max is parameter)

  def __str__(self):
    ts = "%.3f" % (self.timestamp / 1000)
    dest = globals.WPs[self.dest]
    wp = globals.WPs[self.wp]
    retStr = f"CAV : ID = {self.ID}, Timestamp = {ts} ms\n"
    retStr += f"\tCurrent WP = {self.wp} ({round(wp['x']/100, 3)} m, {round(wp['y']/100, 3)} m), "
    retStr += f"Destination WP = {self.dest} ({round(dest['x']/100, 3)} m, {round(dest['y']/100, 3)} m)\n"
    retStr += f"\tPosition = ({self.x} m, {self.y} m), Angle (phi) = {self.phi} rad, "
    retStr += f"Velocity = {self.v} m/s, Acc. = {self.a} m/s2"
    return retStr


def testCAVDefinition():
  c = CAV()
  c.ID, c.timestamp = 0, 90990
  c.wp, c.dest = 0, 3
  c.x, c.y = 90, 906
  c.phi = 0.785
  c.v, c.a = 10, -1
  print(c)


if __name__ == "__main__":
  globals.importParentGraph(os.path.join(os.getcwd(), "samples/eye.json"))
  testCAVDefinition()


