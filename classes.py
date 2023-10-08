
import heapq
from typing import List
from utils import *

class FNode:
    def __init__(self, location: Vec2D, parent, cost: float, heuristic: float, move_vector: Vec2D) -> None:
        self.location: Vec2D = location
        self.parent: FNode = parent
        self.cost = cost
        self.heuristic = heuristic
        self.move_vector = move_vector
    
    def __lt__(self, other) -> bool:
        v1 = self.cost + self.heuristic
        v2 = other.cost + other.heuristic
        return v1 < v2

class PriorityQueue:
    def __init__(self) -> None:
        self._container: List[FNode] = []
    
    @property
    def empty(self) -> bool:
        return not self._container
    
    def push(self, node: FNode) -> None:
        heapq.heappush(self._container, node)

    def pop(self) -> FNode:
        return heapq.heappop(self._container)
