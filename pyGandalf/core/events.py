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
    SCROLL = 7
    WINDOW_SIZE = 8
    WINDOW_CLOSE = 9
    WINDOW_REFRESH = 10
    WINDOW_FOCUS = 11
    FRAMEBUFFER_SIZE = 12
    CURSOR_ENTER = 13
    SCENE_CHANGE = 14
    SYSTEM_STATE = 15

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