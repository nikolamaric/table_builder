from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Table
from api.serializers import (
    get_dynamic_serializer_class,
    CreateDynamicTableSerializer,
    DynamicTableInfoSerializer,
)
from api.utils import (
    DynamicModel,
    create_dynamic_model_by_table_id,
    update_fields_in_dynamic_model_by_table_id,
)


class TableView(APIView):
    def post(self, request):
        """
        Create a new dynamic table
        """
        serializer = CreateDynamicTableSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(data={"msg": serializer.errors}, status=400)

        table_name = serializer.validated_data.get("name")
        fields = serializer.validated_data.get("fields")

        try:
            dynamic_table = DynamicModel(raw_fields=fields).create_table(external_name=table_name)
        except Exception as e:
            return Response(data={"msg": str(e)}, status=400)

        table = Table.objects.get(id=dynamic_table.id)
        fields = table.fields

        res = DynamicTableInfoSerializer(dict(table=table, fields=fields)).data
        return Response(data=res, status=201)

    def put(self, request, table_id):
        """
        Update a dynamic table - add new fields
        """

        table = Table.objects.filter(id=table_id).first()

        if not table:
            return Response(data={"msg": f"Table with id: {table_id} does not exist."}, status=404)

        serializer = CreateDynamicTableSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(data={"msg": serializer.errors}, status=400)

        fields = serializer.validated_data.get("fields")

        try:
            # Update the fields in the dynamic model
            update_fields_in_dynamic_model_by_table_id(table_id=table_id, field_mappings=fields)
        except Exception as e:
            return Response(data={"msg": str(e)}, status=400)

        table = Table.objects.get(id=table_id)
        fields = table.fields

        res = DynamicTableInfoSerializer(dict(table=table, fields=fields)).data
        return Response(data=res, status=201)


class DynamicTableRowCreateView(APIView):
    def post(self, request, table_id):
        """
        Create a new row in a dynamic table
        """

        table = Table.objects.filter(id=table_id).first()

        if not table:
            return Response(data={"msg": f"Table with id: {table_id} does not exist."}, status=404)

        # Get the dynamic model type from the table_id
        dynamic_model_type = create_dynamic_model_by_table_id(table_id=table_id)

        # Get the dynamic serializer class from the dynamic model type
        serializer = get_dynamic_serializer_class(dynamic_model=dynamic_model_type)(data=request.data)

        if not serializer.is_valid():
            return Response(data={"msg": serializer.errors}, status=400)

        dynamic_model_type.objects.create(**serializer.validated_data)
        return Response(status=201)


class DynamicTableRowListView(APIView):
    def get(self, request, table_id):
        """
        Get all rows in a dynamic table
        """

        table = Table.objects.filter(id=table_id).first()

        if not table:
            return Response(data={"msg": f"Table with id: {table_id} does not exist."}, status=404)

        # Get the dynamic model type from the table_id
        dynamic_model_type = create_dynamic_model_by_table_id(table_id=table_id)

        # Get the table rows from the table model
        table_rows = dynamic_model_type.objects.all()

        # Serialize the table rows
        serialized_table_rows = get_dynamic_serializer_class(dynamic_model=dynamic_model_type)(
            table_rows, many=True
        ).data

        return Response(data=serialized_table_rows, status=200)
