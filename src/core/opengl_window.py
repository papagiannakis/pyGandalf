import glfw
import OpenGL.GL as gl

class OpenGLWindow:
    def __init__(self, title, width, height, vertical_sync):
        self.handle = None
        self.title = title
        self.width = width
        self.height = height
        self.vertical_sync = vertical_sync

    def create(self):
        # Initialize GLFW
        if not glfw.init():
            print("GLFW could not be initialized!")
            exit(-1)

        # Set GLFW window hints
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

        # Create a windowed mode window and its OpenGL context
        self.handle = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.handle:
            print("Window could not be created!")
            glfw.terminate()
            exit(-1)

        # Make the window's context current
        glfw.make_context_current(self.handle)

        # Set vsync mode
        glfw.swap_interval(1 if self.vertical_sync else 0)

        # Obtain the GL versioning system info
        gVersionLabel = f'OpenGL {gl.glGetString(gl.GL_VERSION).decode()} GLSL {gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode()} Renderer {gl.glGetString(gl.GL_RENDERER).decode()}'
        print(gVersionLabel)

    def destroy(self):
        glfw.destroy_window(self.handle)
        glfw.terminate()

    def dispatch_main_loop(self, main_loop):
        while not glfw.window_should_close(self.handle):
            main_loop()
            glfw.swap_buffers(self.handle)
            glfw.poll_events()

    def get_handle(self):
        return self.handle
    
    def close(self):
        glfw.set_window_should_close(self.handle, True)
    
    def set_title(self, title):
        glfw.set_window_title(self.handle, title)