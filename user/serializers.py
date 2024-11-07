# serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # Add more custom claims if needed

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Customize the response data
        data.update({
            'code': 200,
            'message': 'Login successful',
        })

        # Optionally, include additional user information
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            # Add more user fields if necessary
        }

        return data
