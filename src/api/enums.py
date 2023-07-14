class Enumeration:
    CHOICES = None  # this is populated in the subclasses

    @classmethod
    def tuple_choices(cls):
        return [(choice, choice) for choice in cls.CHOICES]

    @classmethod
    def from_string(cls, text: str):
        if cls.CHOICES is not None:
            for choice in cls.CHOICES:
                if str(choice) == text:
                    return choice
        return None


class TypeEnum(Enumeration):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "bool"

    CHOICES = (STR, INT, FLOAT, BOOLEAN)
