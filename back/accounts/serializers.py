# backend/accounts/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import DEFAULT_AVATAR_CHOICES
from api.serializers import BookSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    default_avatar = serializers.CharField(read_only=True)
    occupation = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)
    interests = serializers.CharField(read_only=True)
    favorites  = BookSerializer(many=True, read_only=True)
    read_books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name',
            'nickname', 'phone', 'birthdate', 'address',
            'status_message', 'avatar_url', 'default_avatar',
            'favorites', 'read_books', 'occupation', 'gender', 'interests'
        ]
        read_only_fields = ['username', 'email']

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        # obj.avatar 는 ImageField, 실제 저장된 파일이 있는 경우
        if obj.avatar:
            url = obj.avatar.url  # 보통 "/media/avatars/xxx.png"
            # request 가 있다면 절대 URI 로 바꿔주고, 없으면 상대경로 그대로 리턴
            return request.build_absolute_uri(url) if request else url
        # 이미지가 없으면 빈 문자열 반환
        return ""

class UserUpdateSerializer(serializers.ModelSerializer):
    # emotion_tags removed
    occupation = serializers.ChoiceField(
        choices=[c[0] for c in User.OCCUPATION_CHOICES], required=False, allow_blank=True
    )
    gender = serializers.ChoiceField(
        choices=[c[0] for c in User.GENDER_CHOICES], required=False, allow_blank=True
    )
    interests = serializers.CharField(required=False, allow_blank=True)
    default_avatar = serializers.ChoiceField(
        choices=[c[0] for c in DEFAULT_AVATAR_CHOICES],
        required=False, allow_blank=True
    )
    avatar         = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'name', 'nickname', 'phone', 'birthdate', 'address',
            'status_message', 'avatar', 'default_avatar', 
            'occupation', 'gender', 'interests'
        ]

    def validate_birthdate(self, value):
        if value is None:
            raise serializers.ValidationError('birthdate is required')
        return value

    def update(self, instance, validated_data):
        occupation = validated_data.pop('occupation', None)
        gender = validated_data.pop('gender', None)
        interests = validated_data.pop('interests', None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        if occupation is not None:
            instance.occupation = occupation
        if gender is not None:
            instance.gender = gender
        if interests is not None:
            instance.interests = interests

        instance.save()
        return instance
