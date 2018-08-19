from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventModelViewSet

router = DefaultRouter()
router.register(r'', EventModelViewSet)

urlpatterns = [
    path('', include(router.urls), name='events'),
]