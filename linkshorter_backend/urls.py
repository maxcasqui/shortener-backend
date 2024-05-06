from django.contrib import admin
from django.urls import path, include,re_path
from api import urls
from rest_framework.documentation import include_docs_urls
from api.views import RedirectView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-docs/', include_docs_urls(title='Documentation Shortener API')),
    path('<str:slug>', RedirectView.as_view(), name='redirect')
]
