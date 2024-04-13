from enum import Enum

class EditorPanelComponent:
    class Type(Enum):
        INSPECTOR = 1
        VIEWPORT = 2
        HIERACHY = 3
        STATS = 4
        CONTENT_BROWSER = 5
        MENU_BAR = 6
        CONSOLE = 7
        SYSTEMS = 8

    class Style:
        def __init__(self, style_var, vector_value, float_value, use_float) -> None:
            self.style_var = style_var
            self.vector_value = vector_value
            self.float_value = float_value
            self.use_float = use_float

    def __init__(self, name: str, type : Type, flags, styles : list[Style] = None) -> None:
        self.name = name
        self.type = type
        self.flags = flags
        self.styles = styles
        self.enabled = True
        self.closable = False

class EditorVisibleComponent:
    SELECTED_ENTITY = None
    SELECTED = False
    def __init__(self, editor_visible = True) -> None:
            self.editor_visible = editor_visible