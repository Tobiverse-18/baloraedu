
from django.db.models import Q
from rest_framework.permissions import BasePermission

from .models import School, SchoolMembership
from .role_permissions import ROLE_PERMISSIONS


class IsActiveSchoolMember(BasePermission):
    """
    Allows access only to authenticated users who have
    an active membership in an active school.

    Used for normal school operations.
    """

    message = "You do not have active access to this school."

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id:
            return False

        return SchoolMembership.objects.filter(
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status=School.Status.ACTIVE,
        ).exists()


class IsSchoolManagementMember(BasePermission):
    """
    Allows authenticated, active school members to access
    school management features.

    Active schools:
        Eligible active members can proceed to role checks.

    Pending schools:
        Only the school owner can proceed.

    Suspended and archived schools:
        Access is denied.
    """

    message = "You do not have permission to manage this school."

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id:
            return False

        return SchoolMembership.objects.filter(
            Q(
                school__status=School.Status.ACTIVE,
            )
            | Q(
                school__status=School.Status.PENDING,
                role=SchoolMembership.Role.SCHOOL_OWNER,
            ),
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
        ).exists()


class HasSchoolRole(IsSchoolManagementMember):
    """
    Allows authorised school management members to access
    endpoints based on their assigned school roles.

    Pending schools are restricted to school owners.
    """

    message = "Your school role does not have permission to perform this action."

    def has_permission(self, request, view):

        if not super().has_permission(request, view):
            return False

        required_roles = getattr(
            view,
            "required_school_roles",
            (),
        )

        if not required_roles:
            return False

        school_id = view.kwargs.get("school_id")

        return SchoolMembership.objects.filter(
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            role__in=required_roles,
        ).filter(
            Q(school__status=School.Status.ACTIVE)
            | Q(
                school__status=School.Status.PENDING,
                role=SchoolMembership.Role.SCHOOL_OWNER,
            )
        ).exists()


class HasSchoolPermission(IsActiveSchoolMember):
    """
    Checks whether an active school member has permission
    to access a specific school feature.

    Custom permissions override default role permissions.
    School Owners retain full access.

    This permission is strictly restricted to active schools.
    """

    message = "You do not have permission to access this feature."

    def has_permission(self, request, view):

        if not super().has_permission(request, view):
            return False

        required_permission = getattr(
            view,
            "required_school_permission",
            None,
        )

        if not required_permission:
            return False

        membership = SchoolMembership.objects.filter(
            school_id=view.kwargs.get("school_id"),
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status=School.Status.ACTIVE,
        ).first()

        if not membership:
            return False

        # School Owners retain full access.
        if membership.role == SchoolMembership.Role.SCHOOL_OWNER:
            return True

        # Explicit custom permission takes priority.
        custom_permission = membership.custom_permissions.filter(
            permission=required_permission,
        ).only("is_granted").first()

        if custom_permission is not None:
            return custom_permission.is_granted

        # Fall back to the member's default role permissions.
        user_permissions = ROLE_PERMISSIONS.get(
            membership.role,
            set(),
        )

        return required_permission in user_permissions
