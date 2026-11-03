from types import SimpleNamespace

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from .models import School, SchoolMembership
from .permissions import IsActiveSchoolMember


User = get_user_model()


class IsActiveSchoolMemberTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsActiveSchoolMember()

        self.user = User.objects.create_user(
            email="schoolowner@test.com",
            password="TestPassword123!",
            first_name="School",
            last_name="Owner",
        )

        self.school = School.objects.create(
            name="Permission Test School",
            status=School.Status.ACTIVE,
            created_by=self.user,
        )

        self.membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.user,
            role=SchoolMembership.Role.SCHOOL_OWNER,
            status=SchoolMembership.Status.ACTIVE,
        )

    def check_permission(self, user, school_id):
        request = self.factory.get("/")
        request.user = user

        view = SimpleNamespace(
            kwargs={"school_id": school_id}
        )

        return self.permission.has_permission(request, view)

    def test_active_member_of_active_school_is_allowed(self):
        self.assertTrue(
            self.check_permission(self.user, self.school.id)
        )

    def test_pending_school_is_denied(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        self.assertFalse(
            self.check_permission(self.user, self.school.id)
        )

    def test_suspended_membership_is_denied(self):
        self.membership.status = SchoolMembership.Status.SUSPENDED
        self.membership.save()

        self.assertFalse(
            self.check_permission(self.user, self.school.id)
        )

    def test_revoked_membership_is_denied(self):
        self.membership.status = SchoolMembership.Status.REVOKED
        self.membership.save()

        self.assertFalse(
            self.check_permission(self.user, self.school.id)
        )

    def test_user_without_membership_is_denied(self):
        another_user = User.objects.create_user(
            email="outsider@test.com",
            password="TestPassword123!",
            first_name="Outside",
            last_name="User",
        )

        self.assertFalse(
            self.check_permission(another_user, self.school.id)
        )

    def test_missing_school_id_is_denied(self):
        request = self.factory.get("/")
        request.user = self.user

        view = SimpleNamespace(kwargs={})

        self.assertFalse(
            self.permission.has_permission(request, view)
        )

    def test_unauthenticated_user_is_denied(self):
        request = self.factory.get("/")
        request.user = SimpleNamespace(is_authenticated=False)

        view = SimpleNamespace(
            kwargs={"school_id": self.school.id}
        )

        self.assertFalse(
            self.permission.has_permission(request, view)
        )

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class SchoolWorkspaceAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.owner = User.objects.create_user(
            email="workspaceowner@test.com",
            password="TestPassword123!",
            first_name="Workspace",
            last_name="Owner",
        )

        self.outsider = User.objects.create_user(
            email="outsiderworkspace@test.com",
            password="TestPassword123!",
            first_name="Outside",
            last_name="User",
        )

        self.school = School.objects.create(
            name="Workspace API Test School",
            status=School.Status.ACTIVE,
            created_by=self.owner,
        )

        self.membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.owner,
            role=SchoolMembership.Role.SCHOOL_OWNER,
            status=SchoolMembership.Status.ACTIVE,
        )

        self.url = reverse(
            "school_workspace",
            kwargs={"school_id": self.school.id},
        )

    def test_active_school_member_can_access_workspace(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.school.name)

    def test_outsider_cannot_access_workspace(self):
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_suspended_membership_cannot_access_workspace(self):
        self.membership.status = SchoolMembership.Status.SUSPENDED
        self.membership.save()

        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_school_owner_can_access_workspace(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], School.Status.PENDING)

    def test_suspended_school_cannot_be_accessed(self):
        self.school.status = School.Status.SUSPENDED
        self.school.save()

        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_archived_school_cannot_be_accessed(self):
        self.school.status = School.Status.ARCHIVED
        self.school.save()

        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_workspace(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

from apps.schools.permissions import HasSchoolRole


class HasSchoolRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.permission = HasSchoolRole()

        self.user = User.objects.create_user(
            email="rbacowner@test.com",
            password="TestPassword123!",
            first_name="RBAC",
            last_name="Owner",
        )

        self.school = School.objects.create(
            name="RBAC Test School",
            status=School.Status.ACTIVE,
            created_by=self.user,
        )

        self.membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.user,
            role=SchoolMembership.Role.SCHOOL_OWNER,
            status=SchoolMembership.Status.ACTIVE,
        )

    def check_role_permission(self, required_roles):
        request = self.factory.get("/")
        request.user = self.user

        view = SimpleNamespace(
            kwargs={"school_id": self.school.id},
            required_school_roles=required_roles,
        )

        return self.permission.has_permission(request, view)

    def test_school_owner_is_allowed(self):
        self.assertTrue(
            self.check_role_permission([
                SchoolMembership.Role.SCHOOL_OWNER,
            ])
        )

    def test_school_admin_is_allowed(self):
        self.membership.role = SchoolMembership.Role.SCHOOL_ADMIN
        self.membership.save()

        self.assertTrue(
            self.check_role_permission([
                SchoolMembership.Role.SCHOOL_ADMIN,
            ])
        )

    def test_teacher_is_denied_administrative_access(self):
        self.membership.role = SchoolMembership.Role.TEACHER
        self.membership.save()

        self.assertFalse(
            self.check_role_permission([
                SchoolMembership.Role.SCHOOL_OWNER,
                SchoolMembership.Role.SCHOOL_ADMIN,
            ])
        )

    def test_empty_required_roles_are_denied(self):
        self.assertFalse(
            self.check_role_permission([])
        )

    def test_inactive_membership_is_denied(self):
        self.membership.status = SchoolMembership.Status.SUSPENDED
        self.membership.save()

        self.assertFalse(
            self.check_role_permission([
                SchoolMembership.Role.SCHOOL_OWNER,
            ])
        )

    def test_all_seven_roles_can_be_authorized(self):
        all_roles = [
            SchoolMembership.Role.SCHOOL_OWNER,
            SchoolMembership.Role.SCHOOL_ADMIN,
            SchoolMembership.Role.PRINCIPAL,
            SchoolMembership.Role.ACCOUNTANT,
            SchoolMembership.Role.TEACHER,
            SchoolMembership.Role.PARENT,
            SchoolMembership.Role.STUDENT,
        ]

        for role in all_roles:
            with self.subTest(role=role):
                self.membership.role = role
                self.membership.status = SchoolMembership.Status.ACTIVE
                self.membership.save()

                self.assertTrue(
                    self.check_role_permission([role])
                )

from apps.schools.permissions import HasSchoolPermission
from apps.schools.role_permissions import SchoolPermissions


class HasSchoolPermissionTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.permission = HasSchoolPermission()

        self.user = User.objects.create_user(
            email="featuretest@test.com",
            password="TestPassword123!",
            first_name="Feature",
            last_name="Tester",
        )

        self.school = School.objects.create(
            name="Feature Permission Test School",
            status=School.Status.ACTIVE,
            created_by=self.user,
        )

        self.membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.user,
            role=SchoolMembership.Role.SCHOOL_OWNER,
            status=SchoolMembership.Status.ACTIVE,
        )

    def check_feature_permission(self, required_permission):
        request = self.factory.get("/")
        request.user = self.user

        view = SimpleNamespace(
            kwargs={"school_id": self.school.id},
            required_school_permission=required_permission,
        )

        return self.permission.has_permission(request, view)

    def test_owner_can_manage_students(self):
        self.assertTrue(
            self.check_feature_permission(
                SchoolPermissions.STUDENTS_MANAGE
            )
        )

    def test_accountant_can_manage_fees(self):
        self.membership.role = SchoolMembership.Role.ACCOUNTANT
        self.membership.save()

        self.assertTrue(
            self.check_feature_permission(
                SchoolPermissions.FEES_MANAGE
            )
        )

    def test_teacher_cannot_manage_staff(self):
        self.membership.role = SchoolMembership.Role.TEACHER
        self.membership.save()

        self.assertFalse(
            self.check_feature_permission(
                SchoolPermissions.STAFF_MANAGE
            )
        )

    def test_parent_cannot_manage_fees(self):
        self.membership.role = SchoolMembership.Role.PARENT
        self.membership.save()

        self.assertFalse(
            self.check_feature_permission(
                SchoolPermissions.FEES_MANAGE
            )
        )

    def test_student_cannot_manage_examinations(self):
        self.membership.role = SchoolMembership.Role.STUDENT
        self.membership.save()

        self.assertFalse(
            self.check_feature_permission(
                SchoolPermissions.EXAMS_MANAGE
            )
        )

    def test_suspended_membership_is_denied(self):
        self.membership.status = SchoolMembership.Status.SUSPENDED
        self.membership.save()

        self.assertFalse(
            self.check_feature_permission(
                SchoolPermissions.STUDENTS_VIEW
            )
        )

    def test_missing_required_permission_is_denied(self):
        request = self.factory.get("/")
        request.user = self.user

        view = SimpleNamespace(
            kwargs={"school_id": self.school.id},
        )

        self.assertFalse(
            self.permission.has_permission(request, view)
        )

from apps.schools.models import SchoolMemberPermission



class CustomSchoolPermissionTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.permission = HasSchoolPermission()

        self.user = User.objects.create_user(
            email="custompermission@test.com",
            password="TestPassword123!",
            first_name="Custom",
            last_name="Permission",
        )

        self.school = School.objects.create(
            name="Custom Permission Test School",
            status=School.Status.ACTIVE,
            created_by=self.user,
        )

        self.membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.user,
            role=SchoolMembership.Role.TEACHER,
            status=SchoolMembership.Status.ACTIVE,
        )

    def check_permission(self, required_permission):
        request = self.factory.get("/")
        request.user = self.user

        view = SimpleNamespace(
            kwargs={"school_id": self.school.id},
            required_school_permission=required_permission,
        )

        return self.permission.has_permission(request, view)

    def test_custom_permission_can_grant_access(self):
        SchoolMemberPermission.objects.create(
            membership=self.membership,
            permission=SchoolPermissions.STUDENTS_MANAGE,
            is_granted=True,
            assigned_by=self.user,
        )

        self.assertTrue(
            self.check_permission(SchoolPermissions.STUDENTS_MANAGE)
        )

    def test_custom_permission_can_deny_default_access(self):
        SchoolMemberPermission.objects.create(
            membership=self.membership,
            permission=SchoolPermissions.ATTENDANCE_MANAGE,
            is_granted=False,
            assigned_by=self.user,
        )

        self.assertFalse(
            self.check_permission(SchoolPermissions.ATTENDANCE_MANAGE)
        )

    def test_default_role_permissions_apply_without_override(self):
        self.assertTrue(
            self.check_permission(SchoolPermissions.ATTENDANCE_MANAGE)
        )

    def test_school_owner_retains_full_access(self):
        self.membership.role = SchoolMembership.Role.SCHOOL_OWNER
        self.membership.save()

        SchoolMemberPermission.objects.create(
            membership=self.membership,
            permission=SchoolPermissions.STUDENTS_MANAGE,
            is_granted=False,
            assigned_by=self.user,
        )

        self.assertTrue(
            self.check_permission(SchoolPermissions.STUDENTS_MANAGE)
        )

    def test_unassigned_permission_is_denied(self):
        self.assertFalse(
            self.check_permission(SchoolPermissions.STAFF_MANAGE)
        )

    def test_registered_permission_can_be_saved(self):
        custom_permission = SchoolMemberPermission.objects.create(
            membership=self.membership,
            permission=SchoolPermissions.STUDENTS_MANAGE,
            is_granted=True,
            assigned_by=self.user,
        )

        self.assertEqual(
            custom_permission.permission,
            SchoolPermissions.STUDENTS_MANAGE,
        )

    def test_unregistered_permission_is_rejected(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            SchoolMemberPermission.objects.create(
                membership=self.membership,
                permission="invalid.permission",
                is_granted=True,
                assigned_by=self.user,
            )


class SchoolMemberPermissionAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.owner = User.objects.create_user(
            email="permissionowner@test.com",
            password="TestPassword123!",
            first_name="Permission",
            last_name="Owner",
        )

        self.admin = User.objects.create_user(
            email="permissionadmin@test.com",
            password="TestPassword123!",
            first_name="Permission",
            last_name="Admin",
        )

        self.teacher = User.objects.create_user(
            email="permissionteacher@test.com",
            password="TestPassword123!",
            first_name="Permission",
            last_name="Teacher",
        )

        self.school = School.objects.create(
            name="Permission Management API School",
            status=School.Status.ACTIVE,
            created_by=self.owner,
        )

        self.owner_membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.owner,
            role=SchoolMembership.Role.SCHOOL_OWNER,
            status=SchoolMembership.Status.ACTIVE,
        )

        self.admin_membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.admin,
            role=SchoolMembership.Role.SCHOOL_ADMIN,
            status=SchoolMembership.Status.ACTIVE,
        )

        self.teacher_membership = SchoolMembership.objects.create(
            school=self.school,
            user=self.teacher,
            role=SchoolMembership.Role.TEACHER,
            status=SchoolMembership.Status.ACTIVE,
        )

        self.list_url = reverse(
            "school_member_permissions",
            kwargs={
                "school_id": self.school.id,
                "membership_id": self.teacher_membership.id,
            },
        )

        self.detail_url = reverse(
            "school_member_permission_detail",
            kwargs={
                "school_id": self.school.id,
                "membership_id": self.teacher_membership.id,
                "permission": SchoolPermissions.STUDENTS_MANAGE,
            },
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_owner_can_view_member_permissions(self):
        self.authenticate(self.owner)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["permissions"]), 19)

    def test_owner_can_grant_custom_permission(self):
        self.authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        permission = SchoolMemberPermission.objects.get(
            membership=self.teacher_membership,
            permission=SchoolPermissions.STUDENTS_MANAGE,
        )

        self.assertTrue(permission.is_granted)
        self.assertEqual(permission.assigned_by, self.owner)

    def test_owner_can_deny_default_permission(self):
        self.authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.ATTENDANCE_MANAGE,
                "is_granted": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        permission = SchoolMemberPermission.objects.get(
            membership=self.teacher_membership,
            permission=SchoolPermissions.ATTENDANCE_MANAGE,
        )

        self.assertFalse(permission.is_granted)

    def test_repeated_assignment_updates_existing_permission(self):
        self.authenticate(self.owner)

        first_response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        second_response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": False,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            SchoolMemberPermission.objects.filter(
                membership=self.teacher_membership,
                permission=SchoolPermissions.STUDENTS_MANAGE,
            ).count(),
            1,
        )

    def test_owner_can_remove_custom_permission(self):
        self.authenticate(self.owner)

        SchoolMemberPermission.objects.create(
            membership=self.teacher_membership,
            permission=SchoolPermissions.STUDENTS_MANAGE,
            is_granted=True,
            assigned_by=self.owner,
        )

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            SchoolMemberPermission.objects.filter(
                membership=self.teacher_membership,
                permission=SchoolPermissions.STUDENTS_MANAGE,
            ).exists()
        )

    def test_admin_can_manage_teacher_permissions(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_admin_cannot_modify_own_permissions(self):
        self.authenticate(self.admin)

        url = reverse(
            "school_member_permissions",
            kwargs={
                "school_id": self.school.id,
                "membership_id": self.admin_membership.id,
            },
        )

        response = self.client.post(
            url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_modify_owner_permissions(self):
        self.authenticate(self.admin)

        url = reverse(
            "school_member_permissions",
            kwargs={
                "school_id": self.school.id,
                "membership_id": self.owner_membership.id,
            },
        )

        response = self.client.post(
            url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_modify_another_admin_permissions(self):
        another_admin = User.objects.create_user(
            email="anotheradmin@test.com",
            password="TestPassword123!",
            first_name="Another",
            last_name="Admin",
        )

        membership = SchoolMembership.objects.create(
            school=self.school,
            user=another_admin,
            role=SchoolMembership.Role.SCHOOL_ADMIN,
            status=SchoolMembership.Status.ACTIVE,
        )

        self.authenticate(self.admin)

        url = reverse(
            "school_member_permissions",
            kwargs={
                "school_id": self.school.id,
                "membership_id": membership.id,
            },
        )

        response = self.client.post(
            url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_assign_subscription_permission(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.SUBSCRIPTION_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_permission_is_rejected(self):
        self.authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            {
                "permission": "invalid.permission",
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_member_from_another_school_cannot_be_modified(self):
        another_owner = User.objects.create_user(
            email="otherowner@test.com",
            password="TestPassword123!",
            first_name="Other",
            last_name="Owner",
        )

        another_school = School.objects.create(
            name="Another Permission Test School",
            status=School.Status.ACTIVE,
            created_by=another_owner,
        )

        another_membership = SchoolMembership.objects.create(
            school=another_school,
            user=another_owner,
            role=SchoolMembership.Role.SCHOOL_OWNER,
            status=SchoolMembership.Status.ACTIVE,
        )

        self.authenticate(self.owner)

        url = reverse(
            "school_member_permissions",
            kwargs={
                "school_id": self.school.id,
                "membership_id": another_membership.id,
            },
        )

        response = self.client.post(
            url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_pending_school_owner_can_view_member_permissions(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        self.authenticate(self.owner)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_pending_school_owner_can_grant_custom_permission(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        self.authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            {
                "permission": SchoolPermissions.STUDENTS_MANAGE,
                "is_granted": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            SchoolMemberPermission.objects.filter(
                membership=self.teacher_membership,
                permission=SchoolPermissions.STUDENTS_MANAGE,
                is_granted=True,
            ).exists()
        )

    def test_pending_school_owner_can_remove_custom_permission(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        SchoolMemberPermission.objects.create(
            membership=self.teacher_membership,
            permission=SchoolPermissions.STUDENTS_MANAGE,
            is_granted=True,
            assigned_by=self.owner,
        )

        self.authenticate(self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            SchoolMemberPermission.objects.filter(
                membership=self.teacher_membership,
                permission=SchoolPermissions.STUDENTS_MANAGE,
            ).exists()
        )

    def test_pending_school_admin_cannot_manage_member_permissions(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_pending_school_teacher_cannot_manage_member_permissions(self):
        self.school.status = School.Status.PENDING
        self.school.save()

        self.authenticate(self.teacher)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_suspended_school_owner_cannot_manage_member_permissions(self):
        self.school.status = School.Status.SUSPENDED
        self.school.save()

        self.authenticate(self.owner)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_archived_school_owner_cannot_manage_member_permissions(self):
        self.school.status = School.Status.ARCHIVED
        self.school.save()

        self.authenticate(self.owner)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_manage_permissions(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
