from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.schools.models import School, SchoolMembership
from apps.schools.permission_registry import SchoolPermissions
from apps.schools.role_permissions import ROLE_PERMISSIONS


class HasStaffPermission(BasePermission):
    """
    Controls access to staff management features within a school.

    View:
        Requires STAFF_VIEW.

    Create and update:
        Requires STAFF_MANAGE.

    DELETE:
        Not allowed.

    Custom membership permissions override default role permissions.
    """

    message = "You do not have permission to access staff records."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id or request.method == "DELETE":
            return False

        if request.method in SAFE_METHODS:
            required_permission = SchoolPermissions.STAFF_VIEW

        elif request.method in ("POST", "PUT", "PATCH"):
            required_permission = SchoolPermissions.STAFF_MANAGE

        else:
            return False

        membership = SchoolMembership.objects.filter(
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status=School.Status.ACTIVE,
        ).first()

        if membership is None:
            return False

        # School Owners retain their existing owner-level access.
        if membership.role == SchoolMembership.Role.SCHOOL_OWNER:
            return True

        # Check explicit custom permission overrides first.
        custom_permission = membership.custom_permissions.filter(
            permission=required_permission,
        ).only("is_granted").first()

        if custom_permission is not None:
            return custom_permission.is_granted

        # Fall back to the role's default permissions.
        role_permissions = ROLE_PERMISSIONS.get(
            membership.role,
            set(),
        )

        return required_permission in role_permissions