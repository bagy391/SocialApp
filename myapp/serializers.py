from drf_dynamic_read.serializers import DynamicReadSerializerMixin
from rest_framework import serializers

from myapp.models import User, FriendRequest


class BaseSerializer(DynamicReadSerializerMixin, serializers.ModelSerializer):
    pass


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        # can change later to make random password
        user = User.objects.create_user(**validated_data, password="Test@123", username=validated_data["email"])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)


class FriendRequestSerializer(BaseSerializer):
    from_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="from_user", write_only=True)
    from_user = UserSerializer(read_only=True, filter_fields=["id", "first_name", "last_name", "email"])
    to_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="to_user", write_only=True)
    to_user = UserSerializer(read_only=True, filter_fields=["id", "first_name", "last_name", "email"])

    class Meta:
        model = FriendRequest
        fields = "__all__"

    def create(self, validated_data):
        print(validated_data)
        return FriendRequest.objects.create(**validated_data)

    def validate(self, attrs):
        print(attrs)
        if attrs["from_user"] == attrs["to_user"]:
            raise serializers.ValidationError("You can't send friend request to yourself")
        return attrs
