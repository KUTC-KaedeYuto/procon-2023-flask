from classes import *
from utils import *

def calc_additional_cost(cell, move_vector: Vec2D):
    if cell["structure"] == 1:
        return False
    
    if cell["mason"] != 0:
        return False
    
    if cell["wall"] == 2:
        if move_vector.x * move_vector.y == 0:
            return 2
        else:
            return False
    return 1


def aster(field, start: Vec2D, goal: Vec2D):
    open_queue: PriorityQueue = PriorityQueue()
    open_queue.push(FNode(start,None, 0, distance(start, goal), Vec2D(0, 0)))
    closed_cost = {str(start): 0}
    

    while not open_queue.empty:
        current_node = open_queue.pop()
        current_pos = current_node.location

        if current_pos == goal:
            return current_node
        
        for v in move_vectors:
            new_pos = Vec2D(current_pos.x + v.x, current_pos.y + v.y)
            if new_pos.x < 0 or new_pos.x >= field["board"]["width"] or new_pos.y < 0 or new_pos.y >= field["board"]["height"]:
                continue
            
            new_cell = field['fixed_board'][new_pos.y][new_pos.x]
            new_cost = calc_additional_cost(new_cell, v)

            if new_cost == False:
                continue

            new_cost += current_node.cost
            if str(new_pos) in closed_cost.keys() and closed_cost[str(new_pos)] <= new_cost:
                continue

            closed_cost[str(new_pos)] = new_cost
            open_queue.push(FNode(new_pos, current_node, new_cost, distance(new_pos, goal), v))
    return None

def surrounding_aster(field, start: Vec2D, goal: Vec2D):
    goals = [
        Vec2D(goal.x - 1, goal.y),
        Vec2D(goal.x + 1, goal.y),
        Vec2D(goal.x, goal.y - 1),
        Vec2D(goal.x, goal.y + 1)
    ]
    open_queue: PriorityQueue = PriorityQueue()
    open_queue.push(FNode(start,None, 0, min_distance(start, goals), Vec2D(0, 0)))
    closed_cost = {str(start): 0}
    while not open_queue.empty:
        current_node = open_queue.pop()
        current_pos = current_node.location

        if current_pos in goals:
            return current_node
        
        for v in move_vectors:
            new_pos = Vec2D(current_pos.x + v.x, current_pos.y + v.y)
            if new_pos.x < 0 or new_pos.x >= field["board"]["width"] or new_pos.y < 0 or new_pos.y >= field["board"]["height"]:
                continue
            
            new_cell = field['fixed_board'][new_pos.y][new_pos.x]
            new_cost = calc_additional_cost(new_cell, v)

            if new_cost == False:
                continue

            new_cost += current_node.cost
            if str(new_pos) in closed_cost.keys() and closed_cost[str(new_pos)] <= new_cost:
                continue

            closed_cost[str(new_pos)] = new_cost
            open_queue.push(FNode(new_pos, current_node, new_cost, min_distance(new_pos, goals), v))
    return None