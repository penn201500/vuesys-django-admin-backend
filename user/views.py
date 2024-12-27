# views.py

from datetime import datetime, timezone, timedelta

from django.db.models import Q
from django.utils import timezone
import os
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as SimpleJWTTokenRefreshView,
)

from role.models import SysRole, SysUserRole

# Import custom rate limit decorators
from user.utils import rate_limit_user
from user.utils import set_token_cookie
from .authentication import CookieJWTAuthentication
from .serializers import (
    CustomTokenObtainPairSerializer,
    ProfileUpdateSerializer,
    PasswordUpdateSerializer,
    UserProfileSerializer,
)
from rest_framework.pagination import PageNumberPagination

User = get_user_model()  # Django auth method


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle JWT authentication and return custom response structure.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_LOGIN, method="POST"))
    def post(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        serializer = self.get_serializer(data=request.data)
        remember_me = request.data.get("rememberMe", False)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            # Update the last_login field manually
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            # Adjust token lifetimes based on rememberMe value
            if remember_me:
                # Set longer lifetimes for 'remember me'
                access_token_lifetime = timedelta(minutes=30)  # Adjust as needed
                refresh_token_lifetime = timedelta(days=1)  # Adjust as needed
                refresh_cookie_max_age = 1 * 24 * 60 * 60  # 1 day in seconds
            else:
                # Use default lifetimes
                access_token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
                refresh_token_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
                refresh_cookie_max_age = None  # Session cookie

            tokens = self.get_tokens_for_user(
                user, access_token_lifetime, refresh_token_lifetime
            )

            serializer = UserProfileSerializer(user)
            user_data = serializer.data

            response = Response(
                {
                    "code": 200,
                    "message": "Login successful",
                    "user": user_data,
                    "access": tokens["access"],
                },
                status=status.HTTP_200_OK,
            )

            # Set access token cookie
            set_token_cookie(response, "access", tokens["access"])
            # Set refresh token cookie
            set_token_cookie(
                response, "refresh", tokens["refresh"], max_age=refresh_cookie_max_age
            )

            return response

        except serializers.ValidationError:
            # Customize the error response
            return Response(
                {"code": 401, "message": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def get_tokens_for_user(self, user, access_lifetime, refresh_lifetime):
        """
        Generates token pair for the authenticated user.
        """
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=refresh_lifetime)
        access = refresh.access_token
        access.set_exp(lifetime=access_lifetime)
        return {
            "refresh": str(refresh),
            "access": str(access),
        }


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Skip access token authentication

    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_LOGIN, method="POST"))
    def post(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["REFRESH_COOKIE"])
        if not refresh_token:
            res = {"code": 400, "message": "Refresh token is required"}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            res = {"code": 200, "message": "Logout successful"}
            response = Response(res, status=status.HTTP_200_OK)

            # Remove cookies
            response.delete_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )
            response.delete_cookie(
                settings.SIMPLE_JWT["REFRESH_COOKIE"],
                path=settings.SIMPLE_JWT["REFRESH_COOKIE_PATH"],
            )

            return response
        except TokenError as e:
            res = {"code": 400, "message": f"Invalid token, error is {e}"}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_LOGIN, method="GET"))
    def get(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        serializer = UserProfileSerializer(request.user)
        return Response({"code": 200, "data": serializer.data})


class TokenValidityView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_LOGIN, method="GET"))
    def get(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        access_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if access_token:
            try:
                payload = jwt.decode(access_token, options={"verify_signature": False})
                exp_ts = payload["exp"]
                issued_at_ts = payload["iat"]

                if not exp_ts or not issued_at_ts:
                    raise InvalidToken("Token does not contain exp or iat")

                exp_datetime = datetime.fromtimestamp(exp_ts, timezone.utc)
                iat_datetime = datetime.fromtimestamp(issued_at_ts, timezone.utc)
                now = datetime.now(timezone.utc)

                time_left = (exp_datetime - now).total_seconds()
                token_lifetime = (exp_datetime - iat_datetime).total_seconds()

                return Response(
                    {
                        "code": 200,
                        "valid": True,
                        "data": {
                            "time_left": time_left,
                            "token_lifetime": token_lifetime,
                        },
                    }
                )
            except (jwt.DecodeError, jwt.ExpiredSignatureError, InvalidToken):
                return Response(
                    {
                        "code": 400,
                        "valid": False,
                        "message": "Invalid or expired token",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "code": 400,
                    "valid": False,
                    "message": "Authorization header missing",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenRefreshView(SimpleJWTTokenRefreshView):
    permission_classes = [AllowAny]

    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_REFRESH, method="POST"))
    def post(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["REFRESH_COOKIE"])
        if not refresh_token:
            res = {"code": 401, "message": "No refresh token provided"}
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            remember_me = refresh.get("remember_me", False)
        except TokenError as e:
            return Response(
                {"code": 401, "message": f"Invalid refresh token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = {"refresh": refresh_token}
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response(
                {"code": 401, "message": f"Invalid or expired refresh token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access = serializer.validated_data.get("access")
        new_refresh = serializer.validated_data.get("refresh")
        res = {"code": 200, "message": "Token refreshed successfully", "access": access}
        response = Response(res, status=status.HTTP_200_OK)
        # Set new access token cookie
        if access:
            set_token_cookie(response, "access", access)
        # Set new refresh token cookie if rotation is enabled and a new refresh token is issued
        if new_refresh:
            if remember_me:
                refresh_cookie_max_age = 1 * 24 * 60 * 60  # 1 day in seconds
            else:
                refresh_cookie_max_age = None  # Session cookie

            set_token_cookie(
                response, "refresh", new_refresh, max_age=refresh_cookie_max_age
            )
        return response


class GetCSRFTokenView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_CSRF, method="GET"))
    def get(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return Response({"detail": "CSRF cookie set"}, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(rate_limit_user(rate=settings.RATE_LIMIT_LOGIN, method="POST"))
    def post(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"code": 429, "message": "Too many requests, please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        User = get_user_model()
        data = request.data

        # Validate required fields
        required_fields = ["username", "password", "email"]
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {"code": 400, "message": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check if username already exists
        if User.objects.filter(username=data["username"]).exists():
            return Response(
                {"code": 400, "message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if email already exists
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"code": 400, "message": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                create_time=timezone.now(),
                status=1,  # Active status
            )

            return Response(
                {
                    "code": 200,
                    "message": "User created successfully",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            )

        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def patch(self, request, user_id):
        # Check if the requesting user has admin privileges
        if not request.user.roles.filter(code="admin").exists():
            return Response(
                {
                    "code": 403,
                    "message": "You don't have permission to perform this action",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(update_time=timezone.now())
            return Response(
                {
                    "code": 200,
                    "message": "Profile updated successfully",
                    "data": serializer.data,
                }
            )

        return Response(
            {"code": 400, "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, user_id=None):
        # If user_id is provided, check admin privileges
        if user_id:
            if not request.user.roles.filter(code="admin").exists():
                return Response(
                    {
                        "code": 403,
                        "message": "You don't have permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"code": 404, "message": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            user = request.user

        serializer = PasswordUpdateSerializer(data=request.data, context={"user": user})

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response({"code": 200, "message": "Password updated successfully"})

        return Response(
            {"code": 400, "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AvatarUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, user_id=None):
        # If user_id is provided, check admin privileges
        if user_id:
            if not request.user.roles.filter(code="admin").exists():
                return Response(
                    {
                        "code": 403,
                        "message": "You don't have permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"code": 404, "message": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            user = request.user

        if "avatar" not in request.FILES:
            return Response(
                {"code": 400, "message": "No avatar file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        avatar_file = request.FILES["avatar"]

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if avatar_file.content_type not in allowed_types:
            return Response(
                {
                    "code": 400,
                    "message": "Invalid file type. Only JPEG, PNG and GIF are allowed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size (e.g., max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response(
                {"code": 400, "message": "File too large. Maximum size is 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate unique filename
        file_extension = os.path.splitext(avatar_file.name)[1]
        new_filename = f"avatar_{request.user.id}_{int(timezone.now().timestamp())}{file_extension}"

        # Save file path in media directory
        avatar_path = os.path.join("avatars", new_filename)
        full_path = os.path.join(settings.MEDIA_ROOT, "avatars", new_filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save file
        with open(full_path, "wb+") as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)

        # Update user avatar field
        user.avatar = f"/media/{avatar_path}"
        user.save()

        return Response(
            {
                "code": 200,
                "message": "Avatar updated successfully",
                "data": {"avatar_url": request.user.avatar},
            }
        )


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        user_id = request.query_params.get("user_id")
        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = request.user

            if not user.avatar:
                return Response(
                    {"code": 404, "message": "No avatar found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Return full URL for the avatar
            avatar_url = request.build_absolute_uri(user.avatar)
            return Response({"code": 200, "data": {"avatar_url": avatar_url}})
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": f"Error retrieving avatar: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        try:
            # Get query parameters
            search_query = request.query_params.get("search", "").strip()
            username = request.query_params.get("username", "").strip()
            email = request.query_params.get("email", "").strip()
            phone = request.query_params.get("phone", "").strip()
            comment = request.query_params.get("comment", "").strip()
            ordering = request.query_params.get("ordering", "-create_time")
            # Start with all users
            queryset = User.objects.all()

            # Build search filter
            search_filters = Q()

            # Add individual field filters
            if username:
                search_filters |= Q(username__icontains=username)
            if email:
                search_filters |= Q(email__icontains=email)
            if phone:
                search_filters |= Q(phone__icontains=phone)
            if comment:
                search_filters |= Q(comment__icontains=comment)

            # Add general search if provided
            if search_query:
                search_filters |= (
                    Q(username__icontains=search_query)
                    | Q(email__icontains=search_query)
                    | Q(phone__icontains=search_query)
                    | Q(comment__icontains=search_query)
                )

            # Apply search filters if any exist
            if search_filters:
                queryset = queryset.filter(search_filters)

            # Handle ordering
            if ordering:
                order_fields = ordering.split(",")
                queryset = queryset.order_by(*order_fields)

            # Apply pagination
            paginator = self.pagination_class()
            paginated_users = paginator.paginate_queryset(queryset, request)

            # Serialize the results
            serializer = UserProfileSerializer(paginated_users, many=True)
            # Return response with pagination data
            return Response(
                {
                    "code": 200,
                    "message": "Users retrieved successfully",
                    "data": serializer.data,
                    "count": queryset.count(),
                    "page": int(request.query_params.get("page", 1)),
                    "pageSize": int(
                        request.query_params.get("pageSize", paginator.page_size)
                    ),
                }
            )

        except Exception as e:
            return Response(
                {"code": 500, "message": f"An error occurred: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, user_id=None):
        if user_id:
            user, error_response = self.get_user_for_admin(user_id, request.user)
            if error_response:
                return error_response
        else:
            user = request.user

        role_ids = request.data.get("roles", [])
        if not role_ids:
            return self.bad_request_response("At least one role must be selected")

        if not self.can_assign_roles(user, role_ids, request.user):
            return self.forbidden_response(
                "Cannot assign admin role without admin privileges"
            )

        try:
            self.update_user_roles(user, role_ids)
            return Response(
                {
                    "code": 200,
                    "message": "Roles updated successfully",
                    "data": {"roles": role_ids},
                }
            )
        except Exception as e:
            return self.internal_error_response(str(e))

    def get_user_for_admin(self, user_id, current_user):
        if not current_user.roles.filter(code="admin").exists():
            return None, self.forbidden_response(
                "You don't have permission to perform this action"
            )
        try:
            user = User.objects.get(id=user_id)
            return user, None
        except User.DoesNotExist:
            return None, self.not_found_response("User not found")

    def can_assign_roles(self, user, role_ids, current_user):
        if current_user.roles.filter(code="admin").exists():
            return True
        admin_role = SysRole.objects.filter(code="admin").first()
        return not (admin_role and admin_role.id in role_ids)

    def update_user_roles(self, user, role_ids):
        SysUserRole.objects.filter(user=user).delete()
        for role_id in role_ids:
            try:
                role = SysRole.objects.get(id=role_id)
                SysUserRole.objects.create(user=user, role=role)
            except SysRole.DoesNotExist:
                continue

    @staticmethod
    def bad_request_response(message):
        return Response(
            {"code": 400, "message": message}, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def forbidden_response(message):
        return Response(
            {"code": 403, "message": message}, status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def not_found_response(message):
        return Response(
            {"code": 404, "message": message}, status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def internal_error_response(message):
        return Response(
            {"code": 500, "message": message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, user_id):
        if not request.user.roles.filter(code="admin").exists():
            return Response(
                {
                    "code": 403,
                    "message": "You don't have permission to perform this action",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)
            serializer = UserProfileSerializer(user)
            return Response({"code": 200, "data": serializer.data})
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, user_id):
        # Check if the requesting user has admin privileges
        if not request.user.roles.filter(code="admin").exists():
            return Response(
                {
                    "code": 403,
                    "message": "You don't have permission to perform this action",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)

            # Check if user has admin role
            if user.roles.filter(code="admin").exists():
                return Response(
                    {"code": 400, "message": "Cannot delete user with admin role"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Delete the user
            user.delete()

            return Response({"code": 200, "message": "User deleted successfully"})

        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
