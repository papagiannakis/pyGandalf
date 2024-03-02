import glfw

class BaseWindow:
    def __init__(self, title, width, height, vertical_sync):
        self.handle = None
        self.title = title
        self.width = width
        self.height = height
        self.vertical_sync = vertical_sync

    def create(self):        
        return NotImplementedError()

    def dispatch_main_loop(self, main_loop):
        return NotImplementedError()

    def destroy(self):
        glfw.destroy_window(self.handle)
        glfw.terminate()

    def get_handle(self):
        return self.handle
    
    def close(self):
        glfw.set_window_should_close(self.handle, True)
    
    def set_title(self, title):
        glfw.set_window_title(self.handle, title)