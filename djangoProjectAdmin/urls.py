"""
URL configuration for djangoProjectAdmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    # JWT token endpoints
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    # Optional: For token verification and blacklisting
    path('api/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/blacklist/', jwt_views.TokenBlacklistView.as_view(), name='token_blacklist'),
    path("user/", include('user.urls')),
    path("role/", include('role.urls')),
    path("menu/", include('menu.urls')),
)
