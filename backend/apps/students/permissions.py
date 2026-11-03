
from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.schools.models import School, SchoolMembership
from apps.schools.permission_registry import SchoolPermissions
from apps.schools.role_permissions import ROLE_PERMISSIONS


class HasStudentPermission(BasePermission):
    """
    Controls access to student records within a specific school.

    GET, HEAD, OPTIONS:
        Requires students.view.

    POST, PUT, PATCH:
        Requires students.manage.

    DELETE:
        Not allowed. Student records must preserve their history.

    Teachers:
        Denied until class-teacher assignments are implemented.

    Parents and students:
        May pass the feature permission check, but their querysets
        and object access must be restricted in the views.
    """

    message = "You do not have permission to access student records."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id:
            return False

        if request.method == "DELETE":
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

    School Owner, School Admin, Principal:
        Can view and manage guardians according to role permissions.

    Accountant:
        Can view guardian records only.

    Parent:
        Can make read-only requests with an active school membership.
        Their queryset must restrict them to their own linked profile.

    Teacher and Student:
        Cannot access guardian management endpoints.

    DELETE:
        Not allowed. Guardian records must preserve their history.
    """

    message = "You do not have permission to access guardian records."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        school_id = view.kwargs.get("school_id")

        if not school_id:
            return False

        if request.method == "DELETE":
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

        # Parents can make read-only requests.
        # Their queryset restricts them to their own Guardian profile.
        if membership.role == SchoolMembership.Role.PARENT:
            return request.method in SAFE_METHODS

        # Students and teachers cannot access guardian records.
        if membership.role in (
            SchoolMembership.Role.STUDENT,
            SchoolMembership.Role.TEACHER,
        ):
            return False

        # School Owners retain full access.
        if membership.role == SchoolMembership.Role.SCHOOL_OWNER:
            return True

        # An explicit custom permission overrides the default role.
        custom_permission = membership.custom_permissions.filter(
            permission=required_permission,
        ).only("is_granted").first()

        if custom_permission is not None:
            return custom_permission.is_granted

        # Fall back to the school's default role permissions.
        role_permissions = ROLE_PERMISSIONS.get(
            membership.role,
            set(),
        )

        return required_permission in role_permissions
