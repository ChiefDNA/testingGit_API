from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AccountsView


urlpatterns = [
     path('user/',AccountsView.as_view(),name="accounts-ganeral"),
     path('user/<int:id>/',AccountsView.as_view(),name="accounts-general"),

]
