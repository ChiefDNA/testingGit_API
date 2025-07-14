from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('materials/', include('materials.urls')),
    path('companies/', include('companies.urls')),
] + static('media/', document_root='media/')  # Serve media files in development
