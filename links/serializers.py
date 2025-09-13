from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Link

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {'email': {'required': False, 'allow_blank': True}}
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

class LinkSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False, allow_blank=True)
    clicks_count = serializers.IntegerField(source='clicks.count', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Link
        fields = ("id", "title", "target_url", "slug", "is_active", "created_at", "owner_username", "clicks_count")
        read_only_fields = ("id", "is_active", "created_at", "owner_username", "clicks_count")
    def validate_slug(self, value):
        if value and Link.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Slug này đã được sử dụng. Hãy chọn slug khác.")
        return value
