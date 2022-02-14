from .stat import Stat

class Player:
    def __init__(self,data:bytearray):
        self.data = data
        self.name = self.data[:32].decode('utf-16-le')
        self.face_type = Stat(self.data, 108, 2, 3, "Face type")
        self.skin_colour = Stat(self.data, 91, 0, 3, "Skin Colour")
        self.face_id = Stat(self.data, 101, 0, 511, "Face ID")
        self.hair_id = Stat(self.data, 93, 0, 2047, "Hair ID")