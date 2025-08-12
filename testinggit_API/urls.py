from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from accounts.views import DashboardView, custom_login, CrudDashBoardView


urlpatterns = [
    path('', custom_login, name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    re_path(r'^crud/(?P<path>.+)/?$', CrudDashBoardView.as_view(), name='dashboard CRUD'), 
    path('accounts/', include('accounts.urls')),
    path('materials/', include('materials.urls')),
    path('companies/', include('companies.urls')),
] + static('media/', document_root='media/')  # Serve media files in development
