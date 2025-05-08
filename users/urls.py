from django.urls import path
from .views import ObjectsView

urlpatterns = [
    path('users/', ObjectsView.as_view()),
    path('users/<int:id>/', ObjectsView.as_view()),
]
