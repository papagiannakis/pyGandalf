from pyGandalf.utilities.logger import logger
from pyGandalf.core.events import Event, PushEvent, EventType

import glfw

import weakref

def weakbind(method):
    """Replace a bound method with a callable object that stores the `self` using a weakref."""
    ref = weakref.ref(method.__self__)
    class_func = method.__func__
    del method

    def proxy(*args, **kwargs):
        self = ref()
        if self is not None:
            return class_func(self, *args, **kwargs)

    proxy.__name__ = class_func.__name__
    return proxy

class BaseWindow:
    def __init__(self, title = 'Untitled', width = 1280, height = 720, vertical_sync = True):
        self.handle = None
        self.title = title
        self.width = width
        self.height = height
        self.vertical_sync = vertical_sync
        self.key_modifiers = [] 
        self.pointer_buttons = [] 
        self.pointer_pos = 0, 0 
        self.double_click_state = {"clicks": 0}

    def create(self):
        raise NotImplementedError()

    def dispatch_main_loop(self, main_loop):
        raise NotImplementedError()
    
    def get_context(self):
        raise NotImplementedError()

    def destroy(self):
        glfw.destroy_window(self.handle)
        glfw.terminate()

    def get_handle(self):
        return self.handle
    
    def close(self):
        glfw.set_window_should_close(self.handle, True)
    
    def set_title(self, title):
        self.title = title
        glfw.set_window_title(self.handle, title)

    def get_title(self):
        return self.title
    
    def set_callbacks(self):
        glfw.set_window_close_callback(self.handle, weakbind(self._on_window_close)) 
        glfw.set_framebuffer_size_callback(self.handle, weakbind(self._on_framebuffer_resize)) 
        glfw.set_window_size_callback(self.handle, weakbind(self._on_window_resize)) 
        glfw.set_window_refresh_callback(self.handle, weakbind(self._on_window_refresh))
        glfw.set_window_focus_callback(self.handle, weakbind(self._on_window_focus))

        glfw.set_mouse_button_callback(self.handle, weakbind(self._on_mouse_button))
        glfw.set_scroll_callback(self.handle, weakbind(self._on_scroll))
        glfw.set_cursor_pos_callback(self.handle, weakbind(self._on_cursor_pos))
        glfw.set_cursor_enter_callback(self.handle, weakbind(self._on_cursor_enter)) 

        glfw.set_key_callback(self.handle, weakbind(self._on_key))
    
    def _on_window_close(self, window):    
        event = Event() 
        event.type = EventType.WINDOW_CLOSE
        event.data = None 
        PushEvent(event)

    def _on_window_resize(self, window, width, height):
        ev = {
            "width": width, 
            "height": height
        } 
    
        event = Event() 
        event.type = EventType.WINDOW_SIZE
        event.data = ev 
        PushEvent(event)
    
    def _on_framebuffer_resize(self, window, width, height):
        ev = {
            "width": width, 
            "height": height
        }

        event = Event() 
        event.type = EventType.FRAMEBUFFER_SIZE
        event.data = ev 
        PushEvent(event)

    def _on_window_refresh(self, window):
        event = Event() 
        event.type = EventType.WINDOW_REFRESH
        event.data = None 
        PushEvent(event)

    def _on_window_focus(self, window, focus):
        ev = {
            "focus": focus
        }

        event = Event() 
        event.type = EventType.WINDOW_FOCUS
        event.data = ev 
        PushEvent(event)

    def _on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            event_type = EventType.KEY_PRESS
            if key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_LEFT_CONTROL or key == glfw.KEY_LEFT_ALT:
                modifiers = set(self.key_modifiers) 
                modifiers.add(key) 
                self.key_modifiers = list(sorted(modifiers))
        elif action == glfw.RELEASE: 
            event_type = EventType.KEY_RELEASE
            if key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_LEFT_CONTROL or key == glfw.KEY_LEFT_ALT:
                modifiers = set(self.key_modifiers) 
                modifiers.discard(key) 
                self.key_modifiers = list(sorted(modifiers))
        else: 
            return 
        
        ev = {  
            "key": key, 
            "modifiers": list(self.key_modifiers)
        }

        event = Event()  
        event.type = event_type
        event.data = ev 
        PushEvent(event)

    def _on_scroll(self, window, dx, dy):
        ev = {  
            "dx": 100.0 * dx, 
            "dy": -100.0 * dy, 
            "x": glfw.get_cursor_pos(self.handle)[0], 
            "y": glfw.get_cursor_pos(self.handle)[0],
            "buttons": list(self.pointer_buttons),
            "modifiers": list(self.key_modifiers)
        }   
        
        event = Event() 
        event.type = EventType.SCROLL
        event.data = ev
        PushEvent(event)

    def _on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:  
            event_type = EventType.MOUSE_BUTTON_PRESS
            buttons = set(self.pointer_buttons)
            buttons.add(button) 
            self.pointer_buttons = list(sorted(buttons)) 
        elif action == glfw.RELEASE: 
            event_type = EventType.MOUSE_BUTTON_RELEASE
            buttons = set(self.pointer_buttons) 
            buttons.discard(button) 
            self.pointer_buttons = list(sorted(buttons)) 
        else:
            return
            
        ev = {  
            "x": glfw.get_cursor_pos(self.handle)[0], 
            "y": glfw.get_cursor_pos(self.handle)[1], 
            "button": button,
            "modifiers": list(self.key_modifiers)  
        } 
        
        event = Event()  
        event.type = event_type 
        event.data = ev
        PushEvent(event)

    def _on_cursor_pos(self, window, x, y):
        ev = {  
            "x": x, 
            "y": y,
            "width": self.width, 
            "height": self.height,
            "buttons": list(self.pointer_buttons),
            "modifiers": list(self.key_modifiers)
        } 
      
        event = Event() 
        event.type = EventType.MOUSE_MOTION
        event.data = ev  
        PushEvent(event)

    def _on_cursor_enter(self, window, entered):
        ev = {  
            "enter": entered
        } 

        event = Event() 
        event.type = EventType.CURSOR_ENTER
        event.data = ev  
        PushEvent(event)