from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CompanyView

urlpatterns = [
    path('company/', CompanyView.as_view(), name="company-general"),
    path('company/<int:id>/', CompanyView.as_view(), name="company-detail"),
]
