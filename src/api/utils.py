from django.db import connection, models, transaction

from api.enums import TypeEnum
from api.models import Field, Table


class DynamicModel:
    APP_LABEL = "api"
    DYNAMIC_TABLE_PREFIX = "dynamic_table"

    __MODULE__ = "api.models"

    MAPPING_FIELD_TYPES = {
        TypeEnum.STR: models.CharField,
        TypeEnum.INT: models.IntegerField,
        TypeEnum.FLOAT: models.FloatField,
        TypeEnum.BOOLEAN: models.BooleanField,
    }

    def __init__(self, raw_fields: dict):
        self.raw_fields = raw_fields
        self.mapped_fields = self._map_field_types(raw_fields)

    def _map_field_types(self, raw_fields_dict: dict) -> dict:
        """
        Map the raw fields to Django model fields based on the field type
        """
        mapped_fields = {}

        for field_name, field_type in raw_fields_dict.items():
            field = self.MAPPING_FIELD_TYPES.get(field_type)
            mapped_fields[field_name] = field(max_length=255) if field == models.CharField else field()

        return mapped_fields

    def create_dynamic_model(self, internal_name: str) -> type:
        """
        Create a new dynamic model
        """
        attrs = {}

        class Meta:
            app_label = self.APP_LABEL

        # Create attributes for the new model
        attrs["Meta"] = Meta
        attrs["__module__"] = self.__MODULE__
        attrs.update(self.mapped_fields)

        new_model_type = type(internal_name, (models.Model,), attrs)

        return new_model_type

    def save_model(self, external_name: str) -> Table:
        """
        Save the model to the database
        """
        internal_name = self.DYNAMIC_TABLE_PREFIX + "_" + f"{Table.objects.count() + 1}"
        new_table = Table.objects.create(external_name=external_name, internal_name=internal_name)

        return new_table

    @staticmethod
    def save_field(table: Table, field_name: str, field_type: str, save_now: bool = True) -> Field:
        """
        Save a field to the database
        """
        field = Field(name=field_name, type=field_type, table=table)

        # Save it imeediately if save_now is True
        if save_now:
            field.save()

        return field

    def save_fields(self, table: Table):
        """
        Save the fields to the database
        """
        fields = [
            self.save_field(
                table=table,
                field_name=field_name,
                field_type=field_type,
                save_now=False,
            )
            for field_name, field_type in self.raw_fields.items()
        ]

        # Bulk create the fields
        Field.objects.bulk_create(fields)

    @transaction.atomic
    def save_model_and_fields(self, external_name: str) -> Table:
        # Save the model
        new_table = self.save_model(external_name=external_name)

        # Save the fields
        self.save_fields(table=new_table)

        return new_table

    def create_table(self, external_name: str):
        """
        Create a new dynamic table
        """
        new_table = self.save_model_and_fields(external_name=external_name)
        new_model_type = self.create_dynamic_model(internal_name=new_table.internal_name)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(new_model_type)

        return new_table

    def add_field(self, table, field_name, field_type):
        """
        Add a new field to the table
        """
        # Create a field
        field = self.MAPPING_FIELD_TYPES.get(field_type)

        # We do not know if other fields contain data, so we set the field to allow null values,
        # otherwise we cannot add the field
        field = field(max_length=255, null=True) if field == models.CharField else field(null=True)

        model = self.create_dynamic_model(table.internal_name)
        field.contribute_to_class(model, field_name)

        field = model._meta.get_field(field_name)

        # Add field to model
        with connection.schema_editor() as schema_editor:
            schema_editor.add_field(model, field)

        # All is good! Now add the field
        self.save_field(table=table, field_name=field_name, field_type=field_type, save_now=True)


def create_dynamic_model_by_table_id(table_id: int) -> type:
    """
    Create a dynamic model by table id
    """
    table = Table.objects.get(id=table_id)

    # Get the table name from the table model
    table_name = table.internal_name

    # Get the table fields from the table model
    table_fields = table.get_raw_fields()

    dynamic_model = DynamicModel(raw_fields=table_fields)

    # Create the dynamic model type
    dynamic_model_type = dynamic_model.create_dynamic_model(internal_name=table_name)

    return dynamic_model_type


def update_fields_in_dynamic_model_by_table_id(table_id: int, field_mappings: dict):
    """
    Update the fields in the dynamic model by table id
    """
    table = Table.objects.get(id=table_id)

    # Get the table fields from the table model
    table_fields = table.get_raw_fields()

    dynamic_model = DynamicModel(raw_fields=table_fields)

    try:
        for field_name, field_type in field_mappings.items():
            if field_name not in table_fields:
                dynamic_model.add_field(table, field_name, field_type)
    except Exception as e:
        raise Exception(f"Error updating fields in dynamic model. Error: {e}")
