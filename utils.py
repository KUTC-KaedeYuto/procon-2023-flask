
import json
from flask.json.provider import JSONProvider
from typing import *

class Vec2D:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if type(other) != Vec2D:
            return False
        return self.x == other.x and self.y == other.y
    
    def __str__(self) -> str:
        return str(self.x) + "," + str(self.y)

class OriginalJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Vec2D):
            return {"x":o.x,"y":o.y}
        return super().default(o)

class OriginalJSONProvider(JSONProvider):
    def loads(self, s: str | bytes, **kwargs: Any) -> Any:
        return super().loads(s, **kwargs)

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        return json.dumps(obj, cls=OriginalJSONEncoder, **kwargs)


move_vectors = [
    Vec2D(0, 0), Vec2D(-1, -1), Vec2D(0, -1), Vec2D(1, -1), Vec2D(1, 0), Vec2D(1, 1), Vec2D(0, 1), Vec2D(-1, 1), Vec2D(-1, 0)
]

def vector_to_direction(v: Vec2D) -> int:
    for i in range(len(move_vectors)):
        if v == move_vectors[i]:
            return i
            
    return -1

def direction_to_vector(n: int)-> Vec2D:
    return move_vectors[n]
def distance(p1: Vec2D, p2: Vec2D) -> float:
    return ((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2) ** 0.5

def min_distance(start: Vec2D, goals: list) -> float:
    result = 2e9
    for g in goals:
        result = min(result, distance(start, g))
    return result
