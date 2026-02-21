from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'telegram_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'full_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class TelegramAuthSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    full_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        telegram_id = data['telegram_id']

        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'full_name': data.get('full_name', ""),
            },
        )

        data['user'] = user
        data['created'] = created
        return data

