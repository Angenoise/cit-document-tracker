"""
URL routing for documents API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet,
    DocumentActivityViewSet,
    AuthLoginView,
    AuthLogoutView,
    AuthStatusView,
    AuthRegisterView,
    UserViewSet,
    GroupViewSet,
    TokenViewSet,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'activities', DocumentActivityViewSet, basename='activity')
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'tokens', TokenViewSet, basename='token')

urlpatterns = [
    path('auth/login/', AuthLoginView.as_view(), name='auth-login'),
    path('auth/logout/', AuthLogoutView.as_view(), name='auth-logout'),
    path('auth/status/', AuthStatusView.as_view(), name='auth-status'),
    path('auth/register/', AuthRegisterView.as_view(), name='auth-register'),
    path('', include(router.urls)),
]
