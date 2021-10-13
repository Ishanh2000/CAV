from msg_pub_sub import *

class car:

    def __init__(self, car_sign):
        self.car_sign = car_sign
        self.has_reached = False
        self.local_ti = 0
        self.cont_end = 0
        self.v_max = 0
        self.d_max = 0
        self.fp = False # Future Path Struct/List
        self.CAV_info = False # CAV Values from Sensor
        self.Others_info = {} # Other CAV info
        self.Others_PDG = {} # Other CAV info

    def broadcast_INFO(self):
        broadcast(self.info, 0)

    def broadcast_PDG(self):
        broadcast(self.pdg, 1)
    
    def compute_future_path(self):
        pass
        # self.fp = 
    
    def get_cav_info(self):
        pass
        # self.CAV_info = 

    def receive_other_CAV_info(self):
        self.Others_info = receive(0, self.car_sign)

    def receive_other_PDGs(self):
        self.Others_PDG = receive(1, self.car_sign)