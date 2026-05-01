from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import MimasaModel, TranslationNotification

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class MimasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MimasaModel
        fields = [
            "id",
            "video",
            "input_language",
            "output_language",
            "task_status",
            "task_id",
            "output_video_filename",
            "output_video",
            "translated_at",
            "created_at",
        ]


class TranslationNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationNotification
        fields = ["id", "translation", "message", "is_read", "download_token", "created_at"]
