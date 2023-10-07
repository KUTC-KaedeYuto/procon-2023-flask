import threading
import time
from typing import Tuple, List

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
                    'location':{
                        'x': j,
                        'y': i
                    }
                })
            elif mason < 0:
                result_masons["opponent"].append({
                    'id': mason,
                    'location':{
                        'x': j,
                        'y': i
                    }
                })
    f = lambda l : abs(l['id'])
    result_masons['ally'] = sorted(result_masons['ally'], key=f)
    result_masons['opponent'] = sorted(result_masons['opponent'], key=f)
    
    return result_board, result_masons

#経路計算アルゴリズムとつなげる何かが必要
#importして使ってもいいしここにコピペするか新しくクラス作るのもあり

class Action:
    def __init__(self, type: str, direction: int) -> None:
        self.type: str = type
        self.direction: int = direction
    
    def get(self) -> Tuple[str, int]:
        return self.type, self.direction

class ActionType:
    def __init__(self, mason) -> None:
        self.mason = mason
        self.board = None
        self.__done = False
    
    def next(self) -> Action:
        self.__done = True
        return None
    
    def availableNext(self) -> bool:
        return self.__done
    
    def isDone(self) -> bool:
        return self.__done
    
    def updateBoard(self, board) -> None:
        self.board = board


class WaitAction(ActionType):
    def __init__(self, turns: int) -> None:
        super().__init__()
        self.turns: int = turns
        self.progress: int = 0
    
    def next(self) -> Action:
        self.progress += 1
        if self.progress == self.turns:
            super(WaitAction, self).next()
        
        if self.progress > self.turns:
            return None
        return Action('wait', 0)
    
class MoveAction(ActionType):
    def __init__(self, dist_x: int, dist_y: int) -> None:
        super().__init__()
        self.dist = {
            'x': dist_x,
            'y': dist_y
        }
        self.actions: List[Action] = []
        #職人のインスタンス受け取り
    
    def isDone(self) -> bool:
        #行動が完了したか検知(職人の現在地 == 目的地)
        pass
    
    def availableNext(self) -> bool:
        #self.boardを参照して次の行動が有効かどうか判定
        pass

    def next(self) -> Action:
        #次の移動が有効かどうかを検証して有効なら移動アクションを返す
        #無効なら再計算
        pass

#設置と破壊クラスも作る

class Mason:
    def __init__(self, id) -> None:
        self.id = id
        self.actions = []
        self.board = None

    def updateBoard(self, board):
        self.board = board
        for m in board['masons']['ally']:
            if m['id'] == self.id:
                self.location = m['location']
    
    def nextAction(self):
        #self.actionsからActionTypeを取り出してnextを呼び出す
        #ActionTypeのisDoneがTrueなら次のActionTypeに切り替える
        pass
    
    def allocateAction(self, type, data):
        #typeとdataからアクション生成してself.actionsにappendする
        pass


class GameController(threading.Thread):

    def __init__(self, match_list, token, get_method) -> None:
        super(GameController, self).__init__()
        self.match_list = match_list
        self.token = token
        self.get = get_method
        self.initialized = False
        self.__locking_board = False

    def selectMatch(self, match_id):
        self.match_id = match_id
        for m in self.match_list['matches']:
            print(m)
            if m['id'] == match_id:
                self.turns = m['turns']
                self.turnSeconds = m['turnSeconds']
                self.opponent = m['opponent']
                self.first = m['first']
                self.bonus = m['bonus']
                self.board_info = {
                    'height': m['board']['height'],
                    'width': m['board']['width'],
                    'mason' : m['board']['mason'],
                }
                self.mason_list: List[Mason] = []
                for i in range(self.board_info['mason']):
                    self.mason_list.append(Mason(i + 1))
                self.updateBoard()
                self.initialized = True


    def run(self):
        while self.initialized:
            if not self.__board:
                continue
            if False:#ターン更新の検知
                turn_actions = []
                for mason in self.mason_list:
                    turn_actions.append(mason.nextAction())
                #行動計画更新のPOST
            time.sleep(1)
    
    def updateBoard(self):
        res = self.get(f'matches/{self.match_id}', self.token).json()
        b, m = processBoard(res['board'])
        board = res
        board['fixed_board'] = b
        board['masons'] = m
        while self.__locking_board:
            pass
        self.__locking_board = True
        self.__board = board
        self.__locking_board = False
        for mason in self.mason_list:
            mason.updateBoard(self.getBoard())

    def getBoard(self):
        return self.__board