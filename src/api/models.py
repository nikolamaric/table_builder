from django.db import models

from api.enums import TypeEnum


class Table(models.Model):
    external_name = models.CharField(max_length=255, null=True)
    internal_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.__class__.__name__}({self.external_name}, {self.internal_name})"

    def get_raw_fields(self) -> dict:
        return dict(self.fields.values_list("name", "type"))


class Field(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=32, choices=TypeEnum.tuple_choices(), default=TypeEnum.STR)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="fields")

    class Meta:
        unique_together = ("name", "table")

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, {self.type})"
