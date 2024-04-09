from . import Globals
import pygame

class LogItem:
    def __init__(self) -> None:
        self.ticks = pygame.time.get_ticks()
    
    def __repr__(self) -> str:
        return str(self.dict())
    
    def dict(self) -> dict[str, any]:
        dict = {}
        dict["ticks"] = self.ticks
        dict["class"] = str(self.__class__).split('.')[-1][:-2]
        for key, value in self.__dict__.items():
            dict[key] = value
            
        return dict

class Logger:
    def __init__(self) -> None:
        self.logs: list[LogItem] = []
        
    def log(self, log_item: LogItem):
        if not isinstance(log_item, LogItem):
            raise ValueError("Logged item must inherit LogItem")
        self.logs.append(log_item)
        
    def __repr__(self) -> str:
        return str(self.logs)
    
class ChangeSimState(LogItem):
    def __init__(self, new_state) -> None:
        super().__init__()
        self.new_state = new_state

class ChangeDrawState(LogItem):
    def __init__(self, new_state) -> None:
        super().__init__()
        self.new_state = new_state

class EntityDeath(LogItem):
    def __init__(self, entity_type: str, agent_id: int, pos: pygame.Vector2) -> None:
        super().__init__()
        self.entity_type = entity_type
        self.agent_id = agent_id
        self.pos = [pos.x, pos.y]

class EntitySpawn(LogItem):
    def __init__(self, entity_type: str, agent_id: int, pos: pygame.Vector2) -> None:
        super().__init__()
        self.entity_type = entity_type
        self.agent_id = agent_id
        self.pos = [pos.x, pos.y]

class AgentDetection(LogItem):
    def __init__(self, detection_type: str, agent_id: int, detected_id: int) -> None:
        super().__init__()
        self.detection_type = detection_type
        self.agent_id = agent_id
        self.detected_id = detected_id

class EnemyDetection(LogItem):
    def __init__(self, detection_type: str, enemy_id: int, detected_id: int) -> None:
        super().__init__()
        self.detection_type = detection_type
        self.enemy_id = enemy_id
        self.detected_id = detected_id

class ChangeCam(LogItem):
    def __init__(self, current_cam: str, new_cam: str) -> None:
        super().__init__()
        self.current_cam = current_cam
        self.new_cam = new_cam

class EnemyChangeState(LogItem):
    def __init__(self, enemy_id: int, cur_state: str, new_state: str) -> None:
        super().__init__()
        self.enemy_id = enemy_id
        self.cur_state = cur_state
        self.new_state = new_state
        
class ManualSpawn(LogItem):
    def __init__(self, type: str, pos: pygame.Vector2) -> None:
        super().__init__()
        self.type = type
        self.pos = [pos.x, pos.y]
    
class EntityPositionUpdate(LogItem):
    def __init__(self, entities: list) -> None:
        super().__init__()
        self.entities = [{
            "entity_type": str(entity.__class__).split('.')[-1][:-2], 
            "entity_id": entity.__hash__(), 
            "pos": [entity.pos.x, entity.pos.y]
            } for entity in entities]
