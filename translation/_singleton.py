# https://stackoverflow.com/q/6760685
# CC BY-SA 4.0
# (C) https://stackoverflow.com/users/655372/theheadofabroom


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
