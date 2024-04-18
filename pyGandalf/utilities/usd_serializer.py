import jsonpickle
import pickle

class USDSerializer(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(USDSerializer, cls).__new__(cls)
            cls.instance.serialization_rules = {}
            cls.instance.deserialization_rules = {}
        return cls.instance
    
    def add_serialization_rule(cls, component_type, serialization_func):
        cls.instance.serialization_rules[component_type] = serialization_func

    def add_deserialization_rule(cls, component_type, deserialization_func):
        cls.instance.deserialization_rules[component_type] = deserialization_func

    def serialize(cls, prim, component):
        return cls.instance.serialization_rules[type(component)](prim, component)

    def deserialize(cls, prim, component_type):
        return cls.instance.deserialization_rules[component_type](prim)

    def to_json(cls, obj):
        try:
            return jsonpickle.dumps(obj)
        except TypeError:  # If jsonpickle fails, try pickle
            return pickle.dumps(obj).decode('latin1')

    def from_json(cls, json_string):
        try:
            return jsonpickle.loads(json_string)
        except ValueError:  # If jsonpickle fails, try pickle
            return pickle.loads(json_string.encode('latin1'))


"""
Example Usage:

- The custom component should have an attribute by the name: 'custom_serialization' set to True.
- Define and add the serialization rule for the component
- Define and add the deserialization rule for the component

Check here for USD to Python types table: https://docs.omniverse.nvidia.com/usd/latest/technical_reference/usd-types.html

class MyComponent(Component):
    def __init__(self, name: str):
        self.name = name
        self.custom_serialization = True

def serialize_my_component(prim, component):
    component_prim_name = prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
    component_prim_name.Set(component.name)
    return prim

USDSerializer().add_serialization_rule(MyComponent, serialize_my_component)

def deserialize_my_component(prim):
    name = prim.GetAttribute("name").Get()
    return MyComponent(str(name))

USDSerializer().add_deserialization_rule(MyComponent, deserialize_my_component)

"""