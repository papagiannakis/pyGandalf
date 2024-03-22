import uuid

class Entity:
    def __init__(self):
        self.id = uuid.uuid4()
        self.enabled = True