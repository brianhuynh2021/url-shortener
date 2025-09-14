from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.views.generic import RedirectView

from links.views import (
    RegisterAPIView,
    LinksListCreateAPIView,
    LinkDetailAPIView,
    LinkStatsAPIView,
    TopLinksAPIView,
    LinkQRAPIView,
    RedirectAPIView,
)

urlpatterns = [
    path('', RedirectView.as_view(url='/ui/', permanent=False)),
    path('admin/', admin.site.urls),

    # UI
    path('ui/', include('ui.urls')),

    # Auth
    path('api/auth/register/', RegisterAPIView.as_view(), name='auth_register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Links
    path('api/links/', LinksListCreateAPIView.as_view(), name='links_list_create'),
    path('api/links/<int:pk>/', LinkDetailAPIView.as_view(), name='link_detail'),
    path('api/links/<int:pk>/stats/', LinkStatsAPIView.as_view(), name='link_stats'),
    path('api/links/<int:pk>/qr/', LinkQRAPIView.as_view(), name='link_qr'),

    # Stats
    path('api/stats/top/', TopLinksAPIView.as_view(), name='top_links'),

    # Redirect (public)
    path('r/<slug:slug>/', RedirectAPIView.as_view(), name='redirect'),

    # OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # DRF browsable API login/logout (session auth for dev/testing)
    path('api-auth/', include('rest_framework.urls')),
]
