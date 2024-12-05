from SplikamiApp.admin import admin_site
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('SplikamiApp.urls')),
]

# Only for development - this will serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)