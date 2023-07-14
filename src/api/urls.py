from django.urls import path

from api.views import (
    DynamicTableCreateView,
    DynamicTableRowCreateView,
    DynamicTableRowListView,
    DynamicTableUpdateView,
)

urlpatterns = [
    path("table", DynamicTableCreateView.as_view(), name="create_dynamic_table"),
    path("table/<int:table_id>", DynamicTableUpdateView.as_view(), name="update_dynamic_table"),
    path("table/<int:table_id>/row", DynamicTableRowCreateView.as_view(), name="create_dynamic_table_row"),
    path("table/<int:table_id>/rows", DynamicTableRowListView.as_view(), name="list_dynamic_table_rows"),
]
