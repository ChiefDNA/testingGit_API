from .views import MaterialDetailView, MaterialView, MaterialUsageView, MaterialTypeView, SupplierView
from django.urls import path

urlpatterns = [
    path('general/',MaterialView.as_view(), name='materials'),
    path('general/<int:id>/',MaterialDetailView.as_view(), name='material-detail'),
    path('usage/', MaterialUsageView.as_view(), name='material-usage'),
    path('type/', MaterialTypeView.as_view(), name='material-type'),
    path('supplier/', SupplierView.as_view(), name='supplier'),
]
