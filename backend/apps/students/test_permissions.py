from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.schools.models import (
    School,
    SchoolMembership,
    SchoolMemberPermission,
)
from apps.schools.permission_registry import SchoolPermissions
from apps.students.permissions import HasStudentPermission


User = get_user_model()


class HasStudentPermissionTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Permission Test School",
            status=School.Status.ACTIVE,
        )

        self.other_school = School.objects.create(
            name="Another Permission Test School",
            status=School.Status.ACTIVE,
        )

        self.permission = HasStudentPermission()

    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
        )

    def create_membership(
        self,
        email,
        role,
        school=None,
        status=SchoolMembership.Status.ACTIVE,
    ):
        user = self.create_user(email)

        membership = SchoolMembership.objects.create(
            school=school or self.school,
            user=user,
            role=role,
            status=status,
        )

        return user, membership

    def check_permission(
        self,
        user,
        method="GET",
        school_id="USE_DEFAULT",
    ):
        if school_id == "USE_DEFAULT":
            school_id = self.school.id

        request = SimpleNamespace(
            user=user,
            method=method,
        )

        view = SimpleNamespace(
            kwargs={
                "school_id": school_id,
            },
        )

        return self.permission.has_permission(request, view)

    def grant_custom_permission(
        self,
        membership,
        permission,
        is_granted=True,
    ):
        return SchoolMemberPermission.objects.create(
            membership=membership,
            permission=permission,
            is_granted=is_granted,
        )

    # Authentication and membership checks

    def test_anonymous_user_is_denied(self):
        self.assertFalse(
            self.check_permission(AnonymousUser())
        )

    def test_user_without_school_membership_is_denied(self):
        user = self.create_user("outsider@example.com")

        self.assertFalse(
            self.check_permission(user)
        )

    def test_missing_school_id_is_denied(self):
        user, membership = self.create_membership(
            "owner@example.com",
            SchoolMembership.Role.SCHOOL_OWNER,
        )

        self.assertFalse(
            self.check_permission(
                user,
                school_id=None,
            )
        )

    def test_inactive_membership_is_denied(self):
        user, membership = self.create_membership(
            "inactive@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
            status=SchoolMembership.Status.SUSPENDED,
        )

        self.assertFalse(
            self.check_permission(user)
        )

    def test_suspended_school_is_denied(self):
        user, membership = self.create_membership(
            "suspended-school@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.school.status = School.Status.SUSPENDED
        self.school.save(update_fields=["status"])

        self.assertFalse(
            self.check_permission(user)
        )

    def test_pending_school_is_denied(self):
        user, membership = self.create_membership(
            "pending-school@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.school.status = School.Status.PENDING
        self.school.save(update_fields=["status"])

        self.assertFalse(
            self.check_permission(user)
        )

    def test_membership_in_another_school_does_not_grant_access(self):
        user, membership = self.create_membership(
            "other-school@example.com",
            SchoolMembership.Role.SCHOOL_OWNER,
            school=self.other_school,
        )

        self.assertFalse(
            self.check_permission(
                user,
                school_id=self.school.id,
            )
        )

    # School Owner permissions

    def test_school_owner_can_view_students(self):
        user, membership = self.create_membership(
            "owner-view@example.com",
            SchoolMembership.Role.SCHOOL_OWNER,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    def test_school_owner_can_manage_students(self):
        user, membership = self.create_membership(
            "owner-manage@example.com",
            SchoolMembership.Role.SCHOOL_OWNER,
        )

        self.assertTrue(
            self.check_permission(user, "POST")
        )

    def test_school_owner_bypasses_custom_permission_denial(self):
        user, membership = self.create_membership(
            "owner-custom@example.com",
            SchoolMembership.Role.SCHOOL_OWNER,
        )

        self.grant_custom_permission(
            membership,
            SchoolPermissions.STUDENTS_VIEW,
            is_granted=False,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    # Default role permissions

    def test_school_admin_can_view_students(self):
        user, membership = self.create_membership(
            "admin-view@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    def test_school_admin_can_manage_students(self):
        user, membership = self.create_membership(
            "admin-manage@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.assertTrue(
            self.check_permission(user, "POST")
        )

    def test_principal_can_view_students(self):
        user, membership = self.create_membership(
            "principal-view@example.com",
            SchoolMembership.Role.PRINCIPAL,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    def test_principal_can_manage_students(self):
        user, membership = self.create_membership(
            "principal-manage@example.com",
            SchoolMembership.Role.PRINCIPAL,
        )

        self.assertTrue(
            self.check_permission(user, "POST")
        )

    def test_accountant_can_view_students(self):
        user, membership = self.create_membership(
            "accountant-view@example.com",
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    def test_accountant_cannot_manage_students_by_default(self):
        user, membership = self.create_membership(
            "accountant-manage@example.com",
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.assertFalse(
            self.check_permission(user, "POST")
        )

    # Custom permission overrides

    def test_custom_permission_can_grant_accountant_management_access(self):
        user, membership = self.create_membership(
            "accountant-grant@example.com",
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.grant_custom_permission(
            membership,
            SchoolPermissions.STUDENTS_MANAGE,
            is_granted=True,
        )

        self.assertTrue(
            self.check_permission(user, "POST")
        )

    def test_custom_permission_can_deny_admin_view_access(self):
        user, membership = self.create_membership(
            "admin-deny@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.grant_custom_permission(
            membership,
            SchoolPermissions.STUDENTS_VIEW,
            is_granted=False,
        )

        self.assertFalse(
            self.check_permission(user, "GET")
        )

    # Restricted roles

    def test_teacher_is_denied_student_access(self):
        user, membership = self.create_membership(
            "teacher@example.com",
            SchoolMembership.Role.TEACHER,
        )

        self.assertFalse(
            self.check_permission(user, "GET")
        )

    def test_teacher_is_denied_even_with_custom_view_permission(self):
        user, membership = self.create_membership(
            "teacher-custom-view@example.com",
            SchoolMembership.Role.TEACHER,
        )

        self.grant_custom_permission(
            membership,
            SchoolPermissions.STUDENTS_VIEW,
            is_granted=True,
        )

        self.assertFalse(
            self.check_permission(user, "GET")
        )

    def test_parent_can_pass_student_view_permission_check(self):
        user, membership = self.create_membership(
            "parent@example.com",
            SchoolMembership.Role.PARENT,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    def test_student_can_pass_student_view_permission_check(self):
        user, membership = self.create_membership(
            "student@example.com",
            SchoolMembership.Role.STUDENT,
        )

        self.assertTrue(
            self.check_permission(user, "GET")
        )

    # HTTP method restrictions

    def test_delete_is_denied_for_school_owner(self):
        user, membership = self.create_membership(
            "owner-delete@example.com",
            SchoolMembership.Role.SCHOOL_OWNER,
        )

        self.assertFalse(
            self.check_permission(user, "DELETE")
        )

    def test_delete_is_denied_for_school_admin(self):
        user, membership = self.create_membership(
            "admin-delete@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.assertFalse(
            self.check_permission(user, "DELETE")
        )

    def test_unsupported_http_method_is_denied(self):
        user, membership = self.create_membership(
            "admin-unsupported@example.com",
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.assertFalse(
            self.check_permission(user, "TRACE")
        )