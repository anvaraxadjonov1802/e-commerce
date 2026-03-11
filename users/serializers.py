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


class TelegramCheckSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    def validate(self, data):
        telegram_id = data["telegram_id"]

        user = User.objects.filter(telegram_id=telegram_id).first()

        data["user"] = user
        data["registered"] = bool(user and user.phone)
        data["needs_phone"] = not bool(user and user.phone)

        return data


class TelegramBindSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
    full_name = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        phone = value.replace(" ", "").replace("+", "")
        return phone

    def validate(self, data):
        telegram_id = data["telegram_id"]
        phone = data["phone"]
        full_name = data.get("full_name", "")

        # 1) telegram_id bilan user bormi?
        user_by_tg = User.objects.filter(telegram_id=telegram_id).first()

        # 2) phone bilan user bormi?
        user_by_phone = User.objects.filter(phone=phone).first()

        # conflict: tg boshqa userda, phone boshqa userda
        if user_by_tg and user_by_phone and user_by_tg.id != user_by_phone.id:
            raise serializers.ValidationError("Phone belongs to another account.")

        # Case A: tg user bor
        if user_by_tg:
            if not user_by_tg.phone:
                user_by_tg.phone = phone
            if not user_by_tg.full_name and full_name:
                user_by_tg.full_name = full_name
            user_by_tg.save(update_fields=["phone", "full_name"])
            data["user"] = user_by_tg
            return data

        # Case B: phone user bor, tg yo‘q
        if user_by_phone:
            if not user_by_phone.telegram_id:
                user_by_phone.telegram_id = telegram_id
            if not user_by_phone.full_name and full_name:
                user_by_phone.full_name = full_name
            user_by_phone.save(update_fields=["telegram_id", "full_name"])
            data["user"] = user_by_phone
            return data

        # Case C: ikkalasi ham yo‘q — yangi user
        user = User.objects.create_user(
            phone=phone,
            password=None,
            telegram_id=telegram_id,
            full_name=full_name,
        )
        data["user"] = user
        return data


class TelegramLoginSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    def validate(self, data):
        telegram_id = data["telegram_id"]

        user = User.objects.filter(telegram_id=telegram_id).first()
        if not user:
            raise serializers.ValidationError("User not found")

        if not user.phone:
            raise serializers.ValidationError("Phone is required")

        data["user"] = user
        return data
