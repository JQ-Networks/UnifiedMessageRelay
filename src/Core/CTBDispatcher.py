from typing import Dict, List
from enum import Enum
from .UnifiedMessage import UnifiedMessage
from dataclasses import dataclass
from .CTBDriver import sender


class ActionType(Enum):
    All = 1
    Reply = 2


@dataclass
class Action:
    to_platform: str
    to_chat: int
    action_type: ActionType  # All, Reply


graph: Dict[str, Dict[int, List[Action]]] = dict()
graph_ready = False

def set_graph_ready():
    global graph_ready
    graph_ready = True

async def dispatch(message: UnifiedMessage):
    if not graph_ready:  # wait for initialization
        return

    for action in graph[message.from_platform][message.from_chat]:
        # TODO plugin logic
        if action.action_type == ActionType.Reply:
            continue
        await sender[action.to_platform](action.to_chat, message)
