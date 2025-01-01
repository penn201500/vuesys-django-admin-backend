from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogFilterSerializer
from user.views import CustomPageNumberPagination
from .permissions import AuditAccessPermission


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [
        IsAuthenticated,
        AuditAccessPermission,
    ]  # Easier way to check permissions
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = AuditLog.objects.all()

        filters = AuditLogFilterSerializer(data=self.request.query_params)
        filters.is_valid()

        data = filters.validated_data

        if start_date := data.get("start_date"):
            queryset = queryset.filter(timestamp__gte=start_date)

        if end_date := data.get("end_date"):
            queryset = queryset.filter(timestamp__lte=end_date)

        if user := data.get("user"):
            queryset = queryset.filter(
                Q(username__icontains=user) | Q(user_email__icontains=user)
            )

        if action := data.get("action"):
            queryset = queryset.filter(action=action)

        if module := data.get("module"):
            queryset = queryset.filter(module=module)

        if search := data.get("search"):
            queryset = queryset.filter(
                Q(message__icontains=search)
                | Q(resource_type__icontains=search)
                | Q(resource_id__icontains=search)
            )

        return queryset.select_related("user")
