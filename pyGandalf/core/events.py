from typing import Any
from enum import Enum 

EventBuss = []  

class EventType(Enum):
    KEY_PRESS = 1
    KEY_RELEASE = 2
    KEY_REPEAT = 3
    MOUSE_BUTTON_PRESS = 4
    MOUSE_BUTTON_RELEASE = 5
    MOUSE_MOTION = 6
    CURSOR_POS = 7
    SCROLL = 8
    WINDOW_SIZE = 9
    WINDOW_CLOSE = 10
    WINDOW_REFRESH = 11
    WINDOW_FOCUS = 12
    FRAMEBUFFER_SIZE = 13
    CURSOR_ENTER = 14
    SCENE_CHANGE = 15
    SYSTEM_STATE = 16

class Event:
    """
    Simple event wrapper for the window events provided from the window API.
    """ 

    type: EventType
    data: Any    

def PushEvent(event: Event):  
    """
    Push an Event into the event buss.
    """ 
    
    EventBuss.append(event)
    
def PollEventAndFlush():   
    """ 
    Pull all the events from the event buss and clear.
    """ 
    
    events = [] 
    for event in EventBuss:
        events.append(event)

    EventBuss.clear() 
    return events