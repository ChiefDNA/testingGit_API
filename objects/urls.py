from django.urls import path
from .views import ObjectsView

urlpatterns = [
    path('', ObjectsView.as_view()),
    path('<int:id>/', ObjectsView.as_view()),
]
