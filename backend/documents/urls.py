"""
URL routing for documents API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet,
    DocumentActivityViewSet,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'activities', DocumentActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
]
