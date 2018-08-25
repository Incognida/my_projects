from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Event
from .serializers import (EventSerializer, CreateEventSerializer,
                          UpdateEventSerializer)


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class ActionBasedPermission(AllowAny):
    """
    Grant or deny access to a view, based on a mapping in view.action_permissions
    """
    def has_permission(self, request, view):
        for klass, actions in getattr(view, 'action_permissions', {}).items():
            if view.action in actions:
                return klass().has_permission(request, view)
        return False


class EventModelViewSet(ModelViewSet):
    """
    Event creation
    ---
        {
            "category_id": 1,
            "subcategories_ids": [1, 2, 3, 4],
            "description": "flexing out",
            "latitude": 56.2151,
            "longitude": 34.1212,
            "max_members": 10
        }
    ---
    Event patching
    ---
        {
            "category_id": 2,
            "subcategories_ids": [5, 6, 7, 8],
            "members_ids": [2, 3],
            "black_members_ids": [4],
            "max_members": 4
        }
    ---
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination

    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['create', 'partial_update', 'destroy'],
        AllowAny: ['list', 'retrieve']
    }

    def list(self, request, *args, **kwargs):
        """
        Return list of events with pagination. (default page_size=10)
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Get detail event instance by id.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = CreateEventSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, partial=True, **kwargs):
        instance = self.get_object()
        if instance.owner == request.user:
            serializer = UpdateEventSerializer(
                instance=instance, data=request.data
            )
            serializer.is_valid(raise_exception=True)
            updated_instance = serializer.update(
                instance, serializer.validated_data
            )
            return Response(
                self.serializer_class(updated_instance).data,
                status=status.HTTP_202_ACCEPTED
            )
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """
        Delete post. Allowed only by event's owner.
        """
        instance = self.get_object()
        if instance.owner == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
