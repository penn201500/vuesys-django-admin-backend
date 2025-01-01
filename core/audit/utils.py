from functools import wraps
from .models import AuditLog
from django.utils import timezone


def audit_log(module, resource_type):
    """
    Decorator to automatically log audit events for views
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            method_to_action = {
                "POST": "CREATE",
                "PUT": "UPDATE",
                "PATCH": "UPDATE",
                "DELETE": "DELETE",
            }

            try:
                response = func(self, request, *args, **kwargs)

                if request.method in method_to_action:
                    # Check if response indicates success (2xx status codes)
                    is_success = 200 <= response.status_code < 300

                    resource_id = kwargs.get("pk") or getattr(response, "data", {}).get(
                        "id"
                    )
                    # For signup, use the created user's info from response
                    if (
                        module == "USER"
                        and resource_type == "USER"
                        and request.method == "POST"
                        and is_success
                    ):
                        user_data = response.data.get("data", {})
                        username = user_data.get("username", "system")
                        user_email = user_data.get("email")
                    else:
                        # For authenticated users
                        username = (
                            request.user.username
                            if hasattr(request.user, "username")
                            else "system"
                        )
                        user_email = (
                            request.user.email
                            if hasattr(request.user, "email")
                            else None
                        )

                    # Determine message based on response status
                    if is_success:
                        message = f"Successfully {method_to_action[request.method].lower()}d {resource_type}"
                    else:
                        message = f"Failed to {method_to_action[request.method].lower()} {resource_type}: {response.data.get('message', '')}"

                    AuditLog.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        username=username,
                        user_email=user_email,
                        action=method_to_action[request.method],
                        module=module,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        detail={
                            "request_data": request.data,
                            "response_data": getattr(response, "data", None),
                            "params": request.query_params.dict(),
                            "status_code": response.status_code,
                        },
                        ip_address=request.META.get("REMOTE_ADDR"),
                        status=True,
                        message=message,
                    )

                return response

            except Exception as e:
                # For error cases, use system as username if not authenticated
                username = (
                    request.user.username
                    if hasattr(request.user, "username")
                    else "system"
                )
                user_email = (
                    request.user.email if hasattr(request.user, "email") else None
                )

                AuditLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    username=username,
                    user_email=user_email,
                    action=method_to_action.get(request.method, "ERROR"),
                    module=module,
                    resource_type=resource_type,
                    resource_id=kwargs.get("pk", "N/A"),
                    detail={
                        "request_data": request.data,
                        "error": str(e),
                        "params": request.query_params.dict(),
                    },
                    ip_address=request.META.get("REMOTE_ADDR"),
                    status=False,
                    message=f"Failed to {method_to_action.get(request.method, '').lower()} {resource_type}: {str(e)}",
                )
                raise

        return wrapper

    return decorator
