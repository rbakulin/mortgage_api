import logging
from typing import Dict

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from mortgage.messages import events, responses

logger = logging.getLogger('django')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs: Dict) -> Dict:
        if attrs['password'] != attrs['password2']:
            logger.warning(events.PASS_NOT_MATCH.format(username=attrs['username']))
            raise serializers.ValidationError({'password': responses.PASSWORDS_NOT_MATCH})

        return attrs

    def create(self, validated_data: Dict) -> User:
        del validated_data['password2']
        user = User.objects.create(**validated_data)

        user.set_password(validated_data['password'])
        user.save()
        logger.info(events.USER_CREATED.format(user_id=user.pk))

        return user


class TokenRefreshSuccessSerializer(serializers.Serializer):
    access = serializers.CharField()


class TokenObtainPairSuccessSerializer(TokenRefreshSuccessSerializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class UserCreateSuccessSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
