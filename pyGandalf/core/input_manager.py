from pyGandalf.utilities.logger import logger

import glfw
import glm

class InputManager:
    """Provides input management without the event system and on demand.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(InputManager, cls).__new__(cls)
            cls.instance.window = None
            cls.instance.last_pressed_state = []
            cls.instance.last_released_state = []
        return cls.instance
    
    def initialize(cls, window):
        """Initializes the input manager and the button states.

        Args:
            window (GLFWWindow*): The application window.
        """
        cls.instance.window = window

        for i in range(0, 349):
            cls.instance.last_pressed_state.append(glfw.PRESS)

        for i in range(0, 349):
            cls.instance.last_released_state.append(glfw.RELEASE)

    def get_key_down(cls, key_code) -> bool:
        """Returns True as long as the specified key is pressed.

        Args:
            key_code (int): The glfw key code to check.

        Returns:
            bool: True as long as the specified key is pressed, otherwise False.
        """
        result = False
        if cls.instance.window != None:
            if key_code >= 0 and key_code <= 7:
                result = glfw.get_mouse_button(cls.instance.window, key_code) == glfw.PRESS
            else:
                result = glfw.get_key(cls.instance.window, key_code) == glfw.PRESS
        else:
            logger.error('The window is null!')

        return result

    def get_key_press(cls, key_code) -> bool:
        """Return True only the first frame that the specified key is pressed.

        Args:
            key_code (int): The glfw key code to check.

        Returns:
            bool: True only the first frame that the specified key is pressed, otherwise False.
        """
        result = False
        if cls.instance._check_state(key_code) == glfw.PRESS and cls.instance.last_pressed_state[key_code] == glfw.RELEASE:
            result = cls.instance.get_key_down(key_code)

        cls.instance.last_pressed_state[key_code] = cls.instance._check_state(key_code)

        return result

    def get_key_up(cls, key_code) -> bool:
        """Returns True as long as the specified key is released.

        Args:
            key_code (int): The glfw key code to check.

        Returns:
            bool: True as long as the specified key is released, otherwise False.
        """
        result = False
        if cls.instance.window != None:
            if key_code >= 0 and key_code <= 7:
                result = glfw.get_mouse_button(cls.instance.window, key_code) == glfw.RELEASE
            else:
                result = glfw.get_key(cls.instance.window, key_code) == glfw.RELEASE
        else:
            logger.error('The window is null!')

        return result
    
    def get_key_release(cls, key_code) -> bool:
        """Return True only the first frame that the specified key is released.

        Args:
            key_code (int): The glfw key code to check.

        Returns:
            bool: True only the first frame that the specified key is released, otherwise False.
        """
        result = False
        if cls.instance._check_state(key_code) == glfw.RELEASE and cls.instance.last_released_state[key_code] == glfw.PRESS:
            result = cls.instance.get_key_up(key_code)

        cls.instance.last_released_state[key_code] = cls.instance._check_state(key_code)

        return result

    def get_mouse_cursor_pos(cls) -> glm.vec2:
        """Returns the current position of the mouse cursor.

        Returns:
            glm.vec2: The current position of the mouse cursor.
        """
        current_cursor_pos = glm.vec2(0.0)
        if cls.instance.window != None:
            pos = glfw.get_cursor_pos(cls.instance.window)
            current_cursor_pos.x = pos[0]
            current_cursor_pos.y = pos[1]
            return current_cursor_pos
        else:
            logger.error('The window is null!')
        return current_cursor_pos

    def _check_state(cls, key_code):
        if cls.instance.window != None:
            if key_code >= 0 and key_code <= 7:
                return glfw.get_mouse_button(cls.instance.window, key_code)
            else:
                return glfw.get_key(cls.instance.window, key_code)
        else:
            logger.error('The window is null!')

        return 0
