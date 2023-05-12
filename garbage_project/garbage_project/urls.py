from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers
from django.views.generic import RedirectView

from accounts.api.views import CustomUserDocumentView, GarbageCollectorDocumentView, LocationDocumentView

router = routers.SimpleRouter(trailing_slash=False)

router.register(r'customuser-search', CustomUserDocumentView, basename='customuser-search')
router.register(r'garbagecollector-search', GarbageCollectorDocumentView, basename='garbagecollector-search')
router.register(r'location-search', LocationDocumentView, basename='location-search')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include('accounts.urls', namespace='accounts')),
    path("garbage/", include('garbage_app.urls', namespace='garbage')),
    path("", include("admin_page.urls", namespace="adminpage")),
    path("api/", include('accounts.api.urls')),
    path('api/', include('garbage_app.api.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('', RedirectView.as_view(url='garbage/', permanent=True)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += router.urls