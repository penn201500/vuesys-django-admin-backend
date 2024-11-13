# user/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


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
