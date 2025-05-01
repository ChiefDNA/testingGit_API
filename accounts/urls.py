from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AccountsViewSet, RegisterView, LoginView, AccountsView

router = DefaultRouter()
router.register(r'', AccountsViewSet)

urlpatterns = [
     path('register/', RegisterView.as_view(),name="accounts-register"),
     path('users/',include(router.urls)),
     path('users/<int:id>/',include(router.urls)),
     path('user/',AccountsView.as_view(),name="accounts-ganeral"),
     path('user/<int:id>/',AccountsView.as_view(),name="accounts-general"),
     path('login/', LoginView.as_view(),name="accounts-login"),
     # path('login2/', LoginViews.as_view(),name="accounts-login2"),

]
