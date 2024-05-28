from pyGandalf.utilities.logger import logger
from pyGandalf.renderer.base_renderer import BaseRenderer
from pyGandalf.core.events import Event, PollEventAndFlush, EventType

import glfw

class EventManager:
    """Provides an inteface to process the recorded events and calls the user attached callbacks for each type.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EventManager, cls).__new__(cls)
            cls.instance.window = None
            cls.instance.renderer = None
            cls.instance.event_callbacks = {}
            cls.instance.renderer: BaseRenderer = None # type: ignore
        return cls.instance
    
    def initialize(cls, window, renderer: BaseRenderer):
        """Initializes the event manager.

        Args:
            window (GLFWWindow*): The application window.
            window (BaseRenderer): The application window.
        """
        cls.instance.window = window
        cls.instance.renderer = renderer
        for event_type in EventType:
            cls.instance.event_callbacks[event_type] = []

    def process(cls):
        """Polls and flushes the pushed events and excecutes the callbacks attached to them.
        """
        events: list[Event] = PollEventAndFlush()

        for event in events:
            match event.type:
                case EventType.WINDOW_CLOSE:
                    for callback, _ in cls.instance.event_callbacks[EventType.WINDOW_CLOSE]:
                        callback()
                    cls.instance._handle_callback_flush(event.type)
                    glfw.set_window_should_close(cls.instance.window, True)
                case EventType.WINDOW_REFRESH:
                    for callback, _ in cls.instance.event_callbacks[EventType.WINDOW_REFRESH]:
                        callback()
                    cls.instance._handle_callback_flush(event.type)
                case EventType.WINDOW_FOCUS:
                    for callback, _ in cls.instance.event_callbacks[EventType.WINDOW_FOCUS]:
                        callback(event.data["focus"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.WINDOW_SIZE:
                    for callback, _ in cls.instance.event_callbacks[EventType.WINDOW_SIZE]:
                        callback(event.data["width"], event.data["height"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.FRAMEBUFFER_SIZE:
                    for callback, _ in cls.instance.event_callbacks[EventType.FRAMEBUFFER_SIZE]:
                        callback(event.data["width"], event.data["height"])
                    cls.instance._handle_callback_flush(event.type)
                    display_w, display_h = glfw.get_framebuffer_size(cls.instance.window)
                    cls.instance.renderer().resize(display_w, display_h)
                case EventType.CURSOR_ENTER:
                    for callback, _ in cls.instance.event_callbacks[EventType.CURSOR_ENTER]:
                        callback(event.data["enter"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.MOUSE_MOTION:
                    for callback, _ in cls.instance.event_callbacks[EventType.MOUSE_MOTION]:
                        callback(event.data["x"], event.data["y"], event.data["width"], event.data["height"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.SCROLL:
                    for callback, _ in cls.instance.event_callbacks[EventType.SCROLL]:
                        callback(event.data["dx"], event.data["dy"], event.data["buttons"], event.data["modifiers"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.MOUSE_BUTTON_PRESS:
                    for callback, _ in cls.instance.event_callbacks[EventType.MOUSE_BUTTON_PRESS]:
                        callback(event.data["button"], event.data["modifiers"], event.data["x"], event.data["y"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.MOUSE_BUTTON_RELEASE:
                    for callback, _ in cls.instance.event_callbacks[EventType.MOUSE_BUTTON_RELEASE]:
                        callback(event.data["button"], event.data["modifiers"], event.data["x"], event.data["y"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.KEY_PRESS:
                    for callback, _ in cls.instance.event_callbacks[EventType.KEY_PRESS]:
                        callback(event.data["key"], event.data["modifiers"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.KEY_RELEASE:
                    for callback, _ in cls.instance.event_callbacks[EventType.KEY_RELEASE]:
                        callback(event.data["key"], event.data["modifiers"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.SCENE_CHANGE:
                    for callback, _ in cls.instance.event_callbacks[EventType.SCENE_CHANGE]:
                        callback(event.data["previous"], event.data["next"])
                    cls.instance._handle_callback_flush(event.type)
                case EventType.SYSTEM_STATE:
                    for callback, _ in cls.instance.event_callbacks[EventType.SYSTEM_STATE]:
                        callback(event.data["type"], event.data["state"])
                    cls.instance._handle_callback_flush(event.type)

    def attach_callback(cls, event_type: EventType, callback, persistent = False):
        """Attaches a callback to the specified event type callback array.

        Args:
            event_type (EventType): The type of event to attach the callback to.
            callback (function): The callback to be attached.
            persistent (bool): Whether or not the callback will be removed after its first invokation.
            
        \n The callback depending on the type should have the following signature:
            \n- EventType.WINDOW_CLOSE: Callable[[None], None]
            \n- EventType.WINDOW_REFRESH: Callable[[None], None]
            \n- EventType.WINDOW_FOCUS: Callable[[int], None]
            \n- EventType.WINDOW_SIZE: Callable[[int, int], None]
            \n- EventType.FRAMEBUFFER_SIZE: Callable[[int, int], None]
            \n- EventType.CURSOR_ENTER: Callable[[int], None]
            \n- EventType.SCROLL: Callable[[float, float, list[int], list[int]], None]
            \n- EventType.MOUSE_BUTTON_PRESS: Callable[[int, list[int], float, float], None]
            \n- EventType.MOUSE_BUTTON_RELEASE: Callable[[int, list[int], float, float], None]
            \n- EventType.MOUSE_MOTION: Callable[[int, int, int, int], None]
            \n- EventType.KEY_PRESS: Callable[[int, list[int]], None]
            \n- EventType.KEY_RELEASE: Callable[[int, list[int]], None]
            \n- EventType.SCENE_CHANGE: Callable[[Scene, Scene], None]
            \n- EventType.SYSTEM_STATE: Callable[[type, SystemState], None]
        """
        cls.instance.event_callbacks[event_type].append((callback, persistent))

    def _handle_callback_flush(cls, event_type):
        index = 0
        while index < len(cls.instance.event_callbacks[event_type]):
            if not cls.instance.event_callbacks[event_type][index][1]:
                del cls.instance.event_callbacks[event_type][index]
            else:
                index += 1