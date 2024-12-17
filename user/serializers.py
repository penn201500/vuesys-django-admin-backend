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
            "phone": self.user.phone,
            "comment": self.user.comment,
            "status": self.user.status,
            "create_time": (
                self.user.create_time.isoformat() if self.user.create_time else None
            ),
            "login_date": (
                self.user.last_login.isoformat() if self.user.last_login else None
            ),
            "update_time": (
                self.user.update_time.isoformat() if self.user.update_time else None
            ),
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
        fields = ["email", "phone", "comment", "status"]
        extra_kwargs = {
            "email": {"required": False},
            "phone": {"required": False},
            "comment": {"required": False},
            "status": {"required": False},
        }

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if value and len(value) > 11:  # Assuming max length is 11
            raise serializers.ValidationError("Phone number is too long")
        return value

    def validate_email(self, value):
        if (
            value
            and User.objects.exclude(pk=self.instance.pk).filter(email=value).exists()
        ):
            raise serializers.ValidationError("This email is already in use")
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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "comment",
            "status",
            "create_time",
            "last_login",
            "update_time",
        ]
        read_only_fields = [
            "id",
            "username",
            "create_time",
            "update_time",
        ]
