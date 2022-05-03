from typing import Iterable, List, TYPE_CHECKING
from point import Point

class Centroid: 
    penalty_tower: List 
    group: int 
    x: int
    y: int 
    valid: bool
    gs: int 
    # group means which cover it belongs to 
    # x,y represents the x,y coordinates

    def __init__(self,group,x,y):
        self.penalty_tower = []
        self.group = group
        self.x = x 
        self.y = y 
        self.valid = True 
        self.gs = 0 
    
    def distance(self, x1,y1,x2,y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5
    
    def add_penalty(self,cent,R_p):
        if self.distance(self.x,self.y,cent.x,cent.y) <= R_p:
            self.penalty_tower.append(cent)
    
    def remove_penalty(self, cent):
        if cent in self.penalty_tower:
            self.penalty_tower.remove(cent)

    
    def size(self):
        s = []
        for p in self.penalty_tower:
            if not p.group in s: 
                s.append(p.group)
        return len(s)

    def devalid(self,group):
        if self.group == group:
            self.valid = False
            return True 
        return False 
