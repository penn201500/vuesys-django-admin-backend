# user/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to include additional user information in the response.
    """

    remember_me = serializers.BooleanField(default=False, required=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        # Add more custom claims if needed

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Customize the response data
        data.update(
            {
                "code": 200,
                "message": "Login successful",
            }
        )

        # Include additional user information
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            # Add more user fields if necessary
        }

        data["remember_me"] = attrs.get("remember_me", False)

        refresh = self.get_token(self.user)
        # Add refresh_me in the refresh token
        refresh["remember_me"] = data["remember_me"]
        data["refresh"] = str(refresh)

        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone", "comment"]
        extra_kwargs = {
            "email": {"required": False},
            "phone": {"required": False},
            "comment": {"required": False},
        }

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        return value


class PasswordUpdateSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": ["Passwords do not match"]}
            )
        return data

    def validate_new_password(self, value):
        try:
            validate_password(value, self.context["user"])
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_current_password(self, value):
        user = self.context["user"]
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
