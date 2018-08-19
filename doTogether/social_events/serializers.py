from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Event, Category


class EventSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class CreateEventSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(
        min_value=1, max_value=1024, required=True
    )
    subcategories_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=1024**2)
    )
    members_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=10000)
    )

    class Meta:
        model = Event
        fields = ('category_id','subcategories_ids', 'members_ids',
                  'description', 'latitude', 'longitude',
                  'max_members', 'ends_at')

    def create(self, validated_data):
        request = self.context.get('request', None)
        if not request:
            raise Exception("No 'request' in context")
        if not hasattr(request, 'user'):
            raise Exception("No 'user' in request")
        if not self.validate_subcategories():
            raise Exception("One of the subcategories doesn't match category")
        user = request.user
        del self.validated_data['subcategories_ids']
        del self.validated_data['members_ids']
        event = Event.objects.create(
            owner=user, **self.validated_data
        )
        return event

    def update(self, instance, validated_data):
        max_members = validated_data.get('max_members', None)
        members = validated_data.get('members_ids', None)
        if max_members and max_members > len(members):
            raise Exception("Members overflow, up the limit of max_members")
        if not self.validate_subcategories():
            raise Exception("One of the subcategories doesn't match category")

        ends_at = validated_data.get("ends_at", None)
        if ends_at and ends_at < instance.starts_at:
            raise Exception(
                "Event can't be finished earlier than it's started"
            )

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
