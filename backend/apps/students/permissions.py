from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.schools.models import School, SchoolMembership
from apps.schools.permission_registry import SchoolPermissions
from apps.schools.role_permissions import ROLE_PERMISSIONS


class HasStudentPermission(BasePermission):
    """
    Controls access to student records within a specific school.
    """

    message = "You do not have permission to access student records."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id or request.method == "DELETE":
            return False

        if request.method in SAFE_METHODS:
            required_permission = SchoolPermissions.STUDENTS_VIEW
        elif request.method in ("POST", "PUT", "PATCH"):
            required_permission = SchoolPermissions.STUDENTS_MANAGE
        else:
            return False

        membership = SchoolMembership.objects.select_related(
            "school",
        ).filter(
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status=School.Status.ACTIVE,
        ).first()

        if membership is None:
            return False

        if membership.role == SchoolMembership.Role.TEACHER:
            return False

        if membership.role == SchoolMembership.Role.SCHOOL_OWNER:
            return True

        custom_permission = membership.custom_permissions.filter(
            permission=required_permission,
        ).only("is_granted").first()

        if custom_permission is not None:
            return custom_permission.is_granted

        role_permissions = ROLE_PERMISSIONS.get(
            membership.role,
            set(),
        )

        return required_permission in role_permissions


class HasGuardianPermission(BasePermission):
    """
    Controls access to guardian records within a specific school.
    """

    message = "You do not have permission to access guardian records."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id or request.method == "DELETE":
            return False

        if request.method in SAFE_METHODS:
            required_permission = SchoolPermissions.GUARDIANS_VIEW
        elif request.method in ("POST", "PUT", "PATCH"):
            required_permission = SchoolPermissions.GUARDIANS_MANAGE
        else:
            return False

        membership = SchoolMembership.objects.select_related(
            "school",
        ).filter(
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status=School.Status.ACTIVE,
        ).first()

        if membership is None:
            return False

        if membership.role == SchoolMembership.Role.PARENT:
            return request.method in SAFE_METHODS

        if membership.role in (
            SchoolMembership.Role.STUDENT,
            SchoolMembership.Role.TEACHER,
        ):
            return False

        if membership.role == SchoolMembership.Role.SCHOOL_OWNER:
            return True

        custom_permission = membership.custom_permissions.filter(
            permission=required_permission,
        ).only("is_granted").first()

        if custom_permission is not None:
            return custom_permission.is_granted

        role_permissions = ROLE_PERMISSIONS.get(
            membership.role,
            set(),
        )

        return required_permission in role_permissions


class HasStudentGuardianPermission(BasePermission):
    """
    Controls access to student-guardian relationships.

    School Owner, School Admin, Principal:
        View and manage according to their permissions.

    Accountant:
        Read-only access.

    Parent:
        Read-only access. Views must restrict results to their
        own Guardian profile.

    Teacher and Student:
        No access.

    DELETE:
        Not allowed.
    """

    message = (
        "You do not have permission to access student-guardian relationships."
    )

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id or request.method == "DELETE":
            return False

        if request.method in SAFE_METHODS:
            required_permission = SchoolPermissions.GUARDIANS_VIEW
        elif request.method in ("POST", "PUT", "PATCH"):
            required_permission = SchoolPermissions.GUARDIANS_MANAGE
        else:
            return False

        membership = SchoolMembership.objects.select_related(
            "school",
        ).filter(
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status=School.Status.ACTIVE,
        ).first()

        if membership is None:
            return False

        if membership.role in (
            SchoolMembership.Role.TEACHER,
            SchoolMembership.Role.STUDENT,
        ):
            return False

        if membership.role == SchoolMembership.Role.PARENT:
            return request.method in SAFE_METHODS

        if membership.role == SchoolMembership.Role.SCHOOL_OWNER:
            return True

        custom_permission = membership.custom_permissions.filter(
            permission=required_permission,
        ).only("is_granted").first()

        if custom_permission is not None:
            return custom_permission.is_granted

        role_permissions = ROLE_PERMISSIONS.get(
            membership.role,
            set(),
        )

        return required_permission in role_permissions