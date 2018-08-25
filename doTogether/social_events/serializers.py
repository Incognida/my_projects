from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Event, Category
from .utils import UpdateValidator


class EventSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class UpdateEventSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(
        min_value=1, max_value=1024, required=False
    )
    subcategories_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=1024 ** 2),
        required=False
    )
    members_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=10000),
        required=False
    )
    black_members_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=10000),
        required=False
    )

    class Meta:
        model = Event
        fields = ('category_id','subcategories_ids', 'members_ids',
                  'description', 'latitude', 'longitude',
                  'max_members', 'ends_at', 'black_members_ids')
        extra_kwargs = dict.fromkeys(fields, {'required': False})

    def update(self, instance, validated_data):
        return UpdateValidator(instance, validated_data).validate()


class CreateEventSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(
        min_value=1, max_value=1024, required=True
    )
    subcategories_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=1024**2)
    )

    class Meta:
        model = Event
        fields = ('description', 'latitude', 'longitude',
                  'max_members', 'ends_at', 'category_id','subcategories_ids')

    def create(self, validated_data):
        request = self.context.get('request', None)
        if not request:
            raise Exception("No 'request' in context")
        if not hasattr(request, 'user'):
            raise Exception("No 'user' in request")
        if not self.validate_subcategories():
            raise Exception("One of the subcategories doesn't match category")
        user = request.user
        if self.validated_data.get('subcategories_ids', None):
            del self.validated_data['subcategories_ids']
        event = Event.objects.create(
            owner=user, **self.validated_data
        )
        return event

    def validate_subcategories(self):
        subcategories_ids = self.validated_data.get("subcategories_ids", None)
        if not subcategories_ids:
            return True
        category = Category.objects.get(pk=self.validated_data['category_id'])
        sub_ids = category.subcategories.values_list('id', flat=True)
        for subcategory_id in subcategories_ids:
            if subcategory_id not in sub_ids:
                return False
        return True

