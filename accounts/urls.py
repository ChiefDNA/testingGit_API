from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AccountsViewSet, RegisterView

router = DefaultRouter()
router.register(r'', AccountsViewSet)

urlpatterns = [
     path('register/', RegisterView.as_view(),name="api-register"),
     path('',include(router.urls)),
]
