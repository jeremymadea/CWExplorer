__ALL__ = [ 'ObjRegistry' ]

class ObjRegistry():
    registry = dict()

    @classmethod
    def add(cls, name, obj):
        if name in cls.registry:
            return False
        else:
            cls.registry[name] = obj
            return True

    @classmethod
    def update(cls, name, obj):
        cls.registry[name] = obj
        return True

    @classmethod
    def get(cls, name):
        return cls.registry.get(name)

