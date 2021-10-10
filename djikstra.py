# AUM SHREEGANESHAAYA NAMAH||



class WayPoint: # also called "node"
  gid = 0 # graph id
  x = 0
  y = 0
  t = float('inf') # weight, milliseconds
  nb = [] # neighbors
  
  def __init__(self, gid=0, x=0, y=0, t=float('inf'), nb=[]):
    self.gid = gid
    self.x = x
    self.y = y
    self.t = t
    self.nb = nb

if __name__ == "__main__":
  # test Djikstra
  # first add a sample graph
  # G = [
    
  # ]
