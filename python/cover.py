from typing import Iterable, List, TYPE_CHECKING
from point import Point

class Cover:
    horizontal_min: int
    horizontal_max: int
    vertical_min: int 
    vertical_max: int 
    points: List[Point]
    size: int
    # keep track of possible tower region so far 
    center : List[int]
    towers: List[Point]

    def __init__(self):
        self.horizontal_max = - float('inf')
        self.vertical_max = - float('inf')
        self.horizontal_min = float('inf')
        self.vertical_min = float('inf')
        self.points = []
        self.size = 0 
        self.center = []
        self.towers = []


    def put(self, p):
        self.points.append(p)
        if p.x < self.horizontal_min: 
            self.horizontal_min = p.x
        if p.x > self.horizontal_max: 
            self.horizontal_max = p.x
        if p.y < self.vertical_min:
            self.vertical_min = p.y
        if p.y > self.vertical_max: 
            self.vertical_max = p.y
        self.size = self.size + 1

    def set_tower(self): 
        return Point(x=self.center[0],y = self.center[1])
    
    def add_tower(self, t):
        self.towers.append(t)

    def same_cover(c1, c2):
 #       if c1.size != c2.size:
 #           return False
        for x in c1.points:
            if x not in c2.points:
                return False
        return True
