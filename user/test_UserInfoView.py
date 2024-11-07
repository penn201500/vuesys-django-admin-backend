# test_UserInfoView.py

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta

# Use get_user_model to support custom user models
User = get_user_model()


@pytest.mark.django_db
class TestUserInfoView:

    # Returns user information for authenticated requests
    def test_returns_user_info_for_authenticated_requests(self):
        client = APIClient()

        # Create a test user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

        # Authenticate the client with the user
        client.force_authenticate(user=user)

        # Use reverse to get the URL
        url = reverse('user_info')

        # Print the URL to debug
        print(f"URL resolved by reverse('user_info'): {url}")

        # Set the 'Accept-Language' header
        client.credentials(HTTP_ACCEPT_LANGUAGE='en')

        # Make a GET request to the UserInfoView
        response = client.get(url)

        # Assert the response status code and data
        assert response.status_code == 200
        assert response.data['data']['username'] == 'testuser'
        assert response.data['data']['email'] == 'test@example.com'

    # Handles requests with invalid JWT tokens
    def test_handle_invalid_jwt_token(self):
        client = APIClient()

        # Provide an invalid token
        client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')

        # Set the 'Accept-Language' header
        client.credentials(HTTP_ACCEPT_LANGUAGE='en')

        url = reverse('user_info')
        response = client.get(url)

        # Assert the response status code for unauthorized access
        assert response.status_code == 401

    # Handles requests with expired JWT tokens
    def test_handles_expired_jwt_token(self):
        client = APIClient()

        # Set the 'Accept-Language' header
        client.credentials(HTTP_ACCEPT_LANGUAGE='en')

        # Create a test user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

        # Create an expired token
        token = AccessToken.for_user(user)
        token.set_exp(lifetime=timedelta(seconds=-1))  # Set token to be expired

        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('user_info')
        response = client.get(url)

        assert response.status_code == 401
