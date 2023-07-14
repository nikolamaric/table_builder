from rest_framework import serializers

from api.models import Table, Field
from api.utils import DynamicModel


def get_dynamic_serializer_class(dynamic_model):
    """
    Get a dynamic serializer class for a dynamic model
    """

    class DynamicTableSerializer(serializers.ModelSerializer):
        class Meta:
            model = dynamic_model
            fields = "__all__"

    return DynamicTableSerializer


class CreateDynamicTableSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=True)
    fields = serializers.DictField(child=serializers.CharField(), required=True)

    def validate(self, data):
        fields = data.get("fields")

        for field_name, field_type in fields.items():
            if field_type not in DynamicModel.MAPPING_FIELD_TYPES:
                raise serializers.ValidationError(
                    f"Field type: {field_type} for field: {field_name} is not supported. "
                    f"Only the following types are supported: "
                    f'[{", ".join(DynamicModel.MAPPING_FIELD_TYPES.keys())}]'
                )
        return data


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        exclude = ("table", "id")


class DynamicTableInfoSerializer(serializers.Serializer):
    table = TableSerializer()
    fields = FieldSerializer(many=True)
