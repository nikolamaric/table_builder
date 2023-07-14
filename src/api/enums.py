class Enumeration:
    CHOICES = None  # this is populated in the subclasses

    @classmethod
    def tuple_choices(cls):
        return [(choice, choice) for choice in cls.CHOICES]


class TypeEnum(Enumeration):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "bool"

    CHOICES = (STR, INT, FLOAT, BOOLEAN)
