from pyGandalf.core.base_window import BaseWindow
from pyGandalf.utilities.logger import logger

import sys
import glfw
from wgpu.gui.base import WgpuCanvasBase, WgpuAutoGui

# Do checks to prevent pitfalls on hybrid Xorg/Wayland systems
is_wayland = False
if sys.platform.startswith("linux"):
    is_wayland = "wayland" in os.getenv("XDG_SESSION_TYPE", "").lower()
    if is_wayland and not hasattr(glfw, "get_wayland_window"):
        raise RuntimeError(
            "We're on Wayland but Wayland functions not available. "
            + "Did you apt install libglfw3-wayland?"
        )

class WebGPUWindow(WgpuAutoGui, WgpuCanvasBase, BaseWindow):
    def create(self):
        # Initialize GLFW
        if not glfw.init():
            logger.critical("GLFW could not be initialized!")
            exit(-1)
        
        # Set window hints
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        glfw.window_hint(glfw.RESIZABLE, True)
        # see https://github.com/FlorianRhiem/pyGLFW/issues/42
        # Alternatively, from pyGLFW 1.10 one can set glfw.ERROR_REPORTING='warn'
        if sys.platform.startswith("linux"):
            if is_wayland:
                glfw.window_hint(glfw.FOCUSED, False)  # prevent Wayland focus error

        self.handle = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.handle:
            logger.critical("WebGPU Window could not be created!")
            glfw.terminate()
            exit(-1)
        
        # Attach the callbacks.
        self.set_callbacks()

        # Other internal variables
        self._need_draw = False
        self._request_draw_timer_running = False
        self._changing_pixel_ratio = False
        self._is_minimized = False
        
        # Initialize the size
        self._pixel_ratio = -1
        self._screen_size_is_logical = False
        self.set_logical_size(self.width, self.height)
        self._request_draw()

    def dispatch_main_loop(self, main_loop):
        while not glfw.window_should_close(self.handle):
            glfw.poll_events()
            main_loop()
            if self._need_draw:
                # logger.debug(f'_need_draw: {self._need_draw}')
                self._need_draw = False;
                self._draw_frame_and_present()

    def get_context(self):
        return super().get_context(kind="webgpu")

    def _mark_ready_for_draw(self):
        self._request_draw_timer_running = False
        self._need_draw = True  # The event loop looks at this flag
        glfw.post_empty_event()  # Awake the event loop, if it's in wait-mode

    def set_logical_size(self, width, height):
        if width < 0 or height < 0:
            raise ValueError("Window width and height must not be negative")
        self._set_logical_size((float(width), float(height)))

    def _determine_size(self):
        width, height = glfw.get_framebuffer_size(self.handle)  
        pixel_ratio = glfw.get_window_content_scale(self.handle)[0]
        psize = width, height
        psize = int(psize[0]), int(psize[1])

        self._pixel_ratio = pixel_ratio
        self._physical_size = psize
        self._logical_size = psize[0] / pixel_ratio, psize[1] / pixel_ratio     
        
        self._windowWidth = width 
        self._windowHeight = height
                
    def _set_logical_size(self, new_logical_size):
        if self.handle is None:
            return
        # There is unclarity about the window size in "screen pixels".
        # It appears that on Windows and X11 its the same as the
        # framebuffer size, and on macOS it's logical pixels.
        # See https://github.com/glfw/glfw/issues/845
        # Here, we simply do a quick test so we can compensate.

        # The current screen size and physical size, and its ratio
        pixel_ratio = glfw.get_window_content_scale(self.handle)[0]
        ssize = glfw.get_window_size(self.handle)
        psize = glfw.get_framebuffer_size(self.handle)

        # Apply
        if is_wayland:
            # Not sure why, but on Wayland things work differently
            screen_ratio = ssize[0] / new_logical_size[0]
            glfw.set_window_size(
                self.handle,
                int(new_logical_size[0] / screen_ratio),
                int(new_logical_size[1] / screen_ratio),
            )
        else:
            screen_ratio = ssize[0] / psize[0]
            glfw.set_window_size(
                self.handle,
                int(new_logical_size[0] * pixel_ratio * screen_ratio),
                int(new_logical_size[1] * pixel_ratio * screen_ratio),
            )
        self._screen_size_is_logical = screen_ratio != 1
        # If this causes the widget size to change, then _on_size_change will
        # be called, but we may want force redetermining the size.
        if pixel_ratio != self._pixel_ratio:
            self._determine_size()
    
    # API

    def get_window_id(self):
        if sys.platform.startswith("win"):
            return int(glfw.get_win32_window(self.handle))
        elif sys.platform.startswith("darwin"):
            return int(glfw.get_cocoa_window(self.handle))
        elif sys.platform.startswith("linux"):
            if is_wayland:
                return int(glfw.get_wayland_window(self.handle))
            else:
                return int(glfw.get_x11_window(self.handle))
        else:
            raise RuntimeError(f"Cannot get GLFW window id on {sys.platform}.")

    def get_display_id(self):
        if sys.platform.startswith("linux"):
            if is_wayland:
                return glfw.get_wayland_display()
            else:
                return glfw.get_x11_display()
        else:
            raise RuntimeError(f"Cannot get GLFW display id on {sys.platform}.")

    def get_pixel_ratio(self):
        return self._pixel_ratio

    def get_logical_size(self):
        return self._logical_size

    def get_physical_size(self):
        return self._physical_size

    def set_logical_size(self, width, height):
        if width < 0 or height < 0:
            raise ValueError("Window width and height must not be negative")
        self._set_logical_size((float(width), float(height)))

    def _request_draw(self):
        if not self._request_draw_timer_running:
            self._request_draw_timer_running = True
            self._mark_ready_for_draw()