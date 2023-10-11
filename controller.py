import threading
import time
from typing import *
from typing import Union
from aster import *
from copy import copy

from aster import Union

def processBoard(board):
    result_board = list()
    result_masons = {
        'ally': [],
        'opponent': []
    }
    for i in range(board['height']):
        result_board.append(list())
        for j in range(board['width']):
            structure = board['structures'][i][j]
            wall = board['walls'][i][j]
            territory = board['territories'][i][j]
            mason = board['masons'][i][j]
            result_board[i].append({
                'structure': structure,
                'wall': wall,
                'territory': territory,
                'mason': mason
            })
            if mason > 0:
                result_masons["ally"].append({
                    'id': mason,
                    'location': Vec2D(j, i)
                })
            elif mason < 0:
                result_masons["opponent"].append({
                    'id': mason,
                    'location': Vec2D(j, i)
                })
    f = lambda l : abs(l['id'])
    result_masons['ally'] = sorted(result_masons['ally'], key=f)
    result_masons['opponent'] = sorted(result_masons['opponent'], key=f)
    
    return result_board, result_masons

Mason_Alias: TypeAlias = 'Mason'

class Action:
    def __init__(self, type: str, direction: int) -> None:
        self.type: str = type
        self.direction: int = direction
    
    def get(self) -> Tuple[str, int]:
        return self.type, self.direction
    
    def toPostData(self) -> dict:
        return {
            'type': self.toAction(self.type),
            'dir' : self.direction
        }
    
    def toDict(self) -> dict:
        return {
            'type': self.type,
            'dir': self.direction
        }
    
    def __str__(self) -> str:
        return f'{{type:{self.type}, dir: {str(direction_to_vector(self.direction))}}}'

    @staticmethod
    def toAction(type: str):
        try:
            return ['wait', 'move', 'build', 'destroy'].index(type)
        except ValueError:
            return 0

class ActionBase:
    def __init__(self, mason: Mason_Alias) -> None:
        self.mason: Mason = mason
        self.__done: bool = False
        self.initialized: bool = False
    
    def actionInit(self) -> bool:
        self.initialized = True
        return True
    
    def next(self) -> Union[Action, None]:
        self.finish()
        return None
    
    def finish(self) -> None:
        self.__done = True
    
    def availableNext(self) -> bool:
        return self.__done
    
    def isDone(self) -> bool:
        return self.__done
    
    def updateInfo(self, board) -> None:
        self.board = board
    
    def toDict(self) -> dict:
        return {
            'type': self.__class__.__name__,
            'mason': self.mason.id,
            'initialied': self.initialized,
            'done': self.__done
        }


class WaitAction(ActionBase):
    def __init__(self, mason, turns: int) -> None:
        super().__init__(mason)
        self.turns: int = turns
        self.progress: int = 0
    
    def next(self) -> Union[Action, None]:
        self.progress += 1
        if self.progress == self.turns:
            super().next()
        
        if self.progress > self.turns:
            return None
        return Action('wait', 0)
    
    def toDict(self) -> dict:
        result = super().toDict()
        result['turns'] = self.turns
        result['progress'] = self.progress
        return result


class MoveAction(ActionBase):
    def __init__(self, mason: Mason_Alias, dist_x: int, dist_y: int) -> None:
        super().__init__(mason)
        self.dist: Vec2D = Vec2D(dist_x, dist_y)
        self.actions: List[Action] = []
        self.index = -1
    
    def actionInit(self) -> bool:
        goal_node = aster(self.board, self.mason.location, self.dist)
        if goal_node == None:
            return False
        current_node = goal_node
        trace: List[Action] = []

        while current_node.location != self.mason.location:
            v: Vec2D = current_node.move_vector
            trace.append(Action('move', vector_to_direction(v)))
            current_node = current_node.parent
        trace.reverse()
        print(list(map(str, trace)))
        self.actions = trace
        self.index = 0
        super().actionInit()
        return True

    def __getNextPos(self) -> Vec2D:
        next_vec: Vec2D = direction_to_vector(self.actions[self.index].direction)
        new_pos: Vec2D = copy(self.mason.location)
        new_pos.x += next_vec.x
        new_pos.y += next_vec.y
        return new_pos
        
    
    def availableNext(self) -> bool:
        if super().isDone():
            return False
        new_pos = self.__getNextPos()
        cell = self.board['fixed_board'][new_pos.y][new_pos.x]
        if cell["structure"] == 1:
            return False
        if cell["mason"] != 0:
            return False
        
        if cell["wall"] == 2:
            return False
        return True

    def next(self) -> Union[Action, None]:
        if not self.availableNext():
            new_pos = self.__getNextPos()
            if self.board['fixed_board'][new_pos.y][new_pos.x]['wall'] == 2:
                return Action('destroy', self.actions[self.index].direction)
            
            if self.actionInit():
                return self.next()
            else:
                super().finish()
                return None
        action = self.actions[self.index]
        self.index += 1
        if self.index >= len(self.actions):
            super().finish()
        return action
    
    def toDict(self) -> dict:
        result = super().toDict()
        result['dist'] = self.dist
        result['actions'] = [a.toDict() for a in self.actions]
        result['index'] = self.index
        return result

class ConstructionActionBase(ActionBase):
    def __init__(self, mason: Mason_Alias, dist_x: int, dist_y: int) -> None:
        super().__init__(mason)
        self.dist: Vec2D = Vec2D(dist_x, dist_y)
        self.actions: List[Action] = []
        self.index = -1

    def actionInit(self) -> bool:
        goal_node = surrounding_aster(self.board, self.mason.location, self.dist)
        if goal_node == None:
            return False
        current_node = goal_node
        trace: List[Action] = []
        dist_dir = Vec2D(self.dist.x - goal_node.location.x, self.dist.y - goal_node.location.y)
        trace.append(Action('dummy', vector_to_direction(dist_dir)))

        while current_node.location != self.mason.location:
            v: Vec2D = current_node.move_vector
            trace.append(Action('move', vector_to_direction(v)))
            current_node = current_node.parent
        trace.reverse()
        print(list(map(str, trace)))
        self.actions = trace
        self.index = 0
        super().actionInit()
        return True
    
    def __getNextPos(self) -> Vec2D:
        next_vec: Vec2D = direction_to_vector(self.actions[self.index].direction)
        new_pos: Vec2D = copy(self.mason.location)
        new_pos.x += next_vec.x
        new_pos.y += next_vec.y
        return new_pos
    
    def availableNext(self) -> bool:
        if super().isDone():
            return False
        new_pos = self.__getNextPos()
        cell = self.board['fixed_board'][new_pos.y][new_pos.x]
        next_action = self.actions[self.index]
        if next_action.type == 'move':
            if cell["structure"] == 1:
                return False #池
            if cell["mason"] != 0:
                return False #職人がいる
            if cell["wall"] == 2:
                return False #相手の城壁
            
        elif next_action.type == 'build':
            if cell["structure"] == 2:
                return False #城
            if cell["mason"] < 0:
                return False #相手の職人がいる
            if cell["wall"] == 2:
                return False #相手の城壁

        return True
    
    def next(self) -> Union[Action, None]:
        action = self.actions[self.index]
        if not self.availableNext():
            new_pos = self.__getNextPos()
            if self.board['fixed_board'][new_pos.y][new_pos.x]['wall'] == 2:
                return Action('destroy', self.actions[self.index].direction)
            if  action.type == 'move':
                if self.actionInit():
                    return self.next()
                else:
                    super().finish()
                    return None

        action = self.actions[self.index]
        self.index += 1
        if self.index >= len(self.actions):
            super().finish()
        return action
    
    def toDict(self) -> dict:
        result = super().toDict()
        result['dist'] = self.dist
        result['actions'] = [a.toDict() for a in self.actions]
        result['index'] = self.index
        return result

class BuildAction(ConstructionActionBase):
    def __init__(self, mason: Mason_Alias, dist_x: int, dist_y: int) -> None:
        super().__init__(mason, dist_x, dist_y)

    def actionInit(self) -> bool:
        res = super().actionInit()
        self.actions[-1].type = 'build'
        return res
    
    def availableNext(self) -> bool:
        return super().availableNext()
    
    def next(self) -> Action | None:
        return super().next()
    
class DestroyAction(ConstructionActionBase):
    def __init__(self, mason: Mason_Alias, dist_x: int, dist_y: int) -> None:
        super().__init__(mason, dist_x, dist_y)

    def actionInit(self) -> bool:
        res = super().actionInit()
        self.actions[-1].type = 'destroy'
        return res
    
    def availableNext(self) -> bool:
        return super().availableNext()
    
    def next(self) -> Action | None:
        return super().next()
    


class Mason:
    def __init__(self, id) -> None:
        self.id = id
        self.actions: List[ActionBase] = []
        self.action_index: int = 0
        self.board = None

    def updateInfo(self, board) -> None:
        self.board = board
        for m in board['masons']['ally']:
            if m['id'] == self.id:
                self.location: Vec2D = m['location']
        for action in self.actions:
            action.updateInfo(board)
    
    def nextAction(self) -> Union[Action, None]:
        if self.action_index >= len(self.actions):
            return None
        
        current_action_type = self.actions[self.action_index]
        if current_action_type.isDone():
            self.action_index += 1
            return self.nextAction()
        if not current_action_type.initialized:
            res = current_action_type.actionInit()
            if not res:
                self.action_index += 1
                return self.nextAction()
        return current_action_type.next()
    
    def allocateAction(self, type: str, data: dict) -> bool:
        new_action: Union[None, MoveAction, BuildAction, DestroyAction, WaitAction] = None
        if type == 'move':
            new_action = MoveAction(self, data['x'], data['y'])
            self.actions.append(new_action)
            return True
        
        elif type == 'build':
            new_action = BuildAction(self, data['x'], data['y'])
            self.actions.append(new_action)
            return True
        
        elif type == 'destroy':
            new_action = DestroyAction(self, data['x'], data['y'])
            self.actions.append(new_action)
            return True
        
        return False
    
    def toDict(self) -> dict:
        return {
            'id': self.id,
            'actions': [action.toDict() for action in self.actions],
            'action_index': self.action_index,
            'location': self.location
        }


class GameController(threading.Thread):

    def __init__(self, match_list: dict, token: str, get_method: Callable, post_method: Callable) -> None:
        super(GameController, self).__init__()
        self.match_list: dict = match_list
        self.token: str = token
        self.get: Callable = get_method
        self.post: Callable = post_method
        self.initialized: bool = False
        self.__match_info: Union[dict, None] = None
        self.__locking_info: bool = False
        self.posted_turn: int = -1
        self.accepted_actions: list = []
        self.__break_flag: bool = False

    def selectMatch(self, match_id: int) -> None:
        self.match_id: int = match_id
        for m in self.match_list['matches']:
            print(m)
            if m['id'] == match_id:
                self.turns: int = m['turns']
                self.turnSeconds: int = m['turnSeconds']
                self.opponent: str = m['opponent']
                self.first: bool = m['first']
                if not self.first:
                    self.posted_turn = 0
                self.bonus: dict = m['bonus']
                self.board_info: dict = {
                    'height': m['board']['height'],
                    'width': m['board']['width'],
                    'mason' : m['board']['mason'],
                }
                self.mason_list: List[Mason] = []
                for i in range(self.board_info['mason']):
                    self.mason_list.append(Mason(i + 1))
                self.updateInfo()
                self.initialized = True
                return


    def run(self) -> None:
        while self.initialized and not self.__break_flag:
            self.updateInfo()
            if not self.__match_info:
                continue
            current_turn = self.__match_info['turn'] + 1
            if (current_turn %2 == 1) == self.first and self.posted_turn < current_turn:
                turn_actions = []
                for mason in self.mason_list:
                    action = mason.nextAction()
                    if action:
                        turn_actions.append(action.toPostData())
                    else:
                        turn_actions.append(Action('wait', 0).toPostData())
                post_data = {
                    'turn': self.posted_turn + 2,
                    'actions': turn_actions
                }
                print(post_data)
                res = self.post(f'matches/{self.match_id}', self.token, {'Content-Type': 'application/json'}, json.dumps(post_data))
                if res.status_code == 200:
                    self.posted_turn += 2
                    self.accepted_actions.append({
                        'data': post_data,
                        'accepted_at': res.json()['accepted_at']
                    })
            elif current_turn - self.posted_turn >= 2:
                self.posted_turn = current_turn - 1
            time.sleep(0.5)
    
    def updateInfo(self) -> None:
        res = self.get(f'matches/{self.match_id}', self.token)
        if res.status_code != 200:
            return
        res = res.json()
        b, m = processBoard(res['board'])
        info = res
        info['fixed_board'] = b
        info['masons'] = m
        while self.__locking_info:
            pass
        self.__locking_info = True
        self.__match_info = info
        self.__locking_info = False
        for mason in self.mason_list:
            mason.updateInfo(self.getInfo())
            

    def getInfo(self) -> Union[dict, None]:
        return self.__match_info

    
    def allocate(self, data: dict) -> bool:
        try:
            mason_id = data['mason_id']
            action_type = data['action_type']
            action_data = data['action_data']
            return self.mason_list[mason_id - 1].allocateAction(action_type, action_data)
        except KeyError:
            print('[allocate] Invalid data')
            return False
        except IndexError:
            print('[allocate] Invalid mason id')
            return False
        
    def exit(self) -> None:
        self.__break_flag = True

    def toDict(self) -> dict:
        result = {
            'match_list': self.match_list,
            'token': self.token,
            'initialized': self.initialized,
            'match_info': self.__match_info,
            'loking_info': self.__locking_info,
            'posted_turn': self.posted_turn,
            'accepted_actions': self.accepted_actions,
            'break_flag': self.__break_flag
        }
        try:
            result['match_id'] = self.match_id
            result['turns'] = self.turns
            result['turnSeconds'] = self.turnSeconds
            result['opponent'] = self.opponent
            result['first'] = self.first
            result['bonus'] = self.bonus
            result['board_info'] = self.board_info
            result['mason_list'] = [m.toDict() for m in self.mason_list]
            result['loking_info'] = self.__locking_info
            result['match_info'] = self.__match_info

        except AttributeError:
            pass
        return result
