
from django.contrib import admin

from .models import (
    School,
    SchoolMembership,
    SchoolMemberPermission,
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone_number",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone_number",
        "slug",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = ("name",)


@admin.register(SchoolMembership)
class SchoolMembershipAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "school",
        "role",
        "status",
        "invited_at",
        "joined_at",
    )

    list_filter = (
        "role",
        "status",
        "school",
    )

    search_fields = (
        "user__email",
        "school__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(SchoolMemberPermission)
class SchoolMemberPermissionAdmin(admin.ModelAdmin):

    list_display = (
        "school_name",
        "member_email",
        "permission",
        "is_granted",
        "assigned_by",
        "created_at",
    )

    list_filter = (
        "permission",
        "is_granted",
        "membership__role",
        "membership__school",
    )

    search_fields = (
        "membership__user__email",
        "membership__school__name",
        "permission",
    )

    autocomplete_fields = (
        "membership",
    )

    readonly_fields = (
        "assigned_by",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "membership__school",
        "membership__user",
        "assigned_by",
    )

    ordering = ("membership__school__name", "permission")

    @admin.display(description="School", ordering="membership__school__name")
    def school_name(self, obj):
        return obj.membership.school.name

    @admin.display(description="Member", ordering="membership__user__email")
    def member_email(self, obj):
        return obj.membership.user.email

    def save_model(self, request, obj, form, change):
        if not change:
            obj.assigned_by = request.user

        super().save_model(request, obj, form, change)
