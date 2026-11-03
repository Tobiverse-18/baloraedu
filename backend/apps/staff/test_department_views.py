from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from apps.schools.models import School, SchoolMembership
from apps.schools.permission_registry import SchoolPermissions

from apps.staff.models import StaffDepartment

from apps.schools.models import SchoolMembership


User = get_user_model()


class StaffDepartmentAPITestBase(APITestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Staff API Test School",
            status=School.Status.ACTIVE,
        )

        self.other_school = School.objects.create(
            name="Another Staff API Test School",
            status=School.Status.ACTIVE,
        )

        self.admin = self.create_user("admin@example.com")

        self.create_membership(
            self.admin,
            self.school,
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.list_url = (
            f"/api/schools/{self.school.id}/staff/departments/"
        )

    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
        )

    def create_membership(
        self,
        user,
        school,
        role,
        membership_status=SchoolMembership.Status.ACTIVE,
    ):
        return SchoolMembership.objects.create(
            school=school,
            user=user,
            role=role,
            status=membership_status,
        )

    def create_department(
        self,
        name,
        school=None,
        description="Test department",
        is_active=True,
    ):
        return StaffDepartment.objects.create(
            school=school or self.school,
            name=name,
            description=description,
            is_active=is_active,
        )

    def department_detail_url(self, department):
        return (
            f"/api/schools/{self.school.id}/staff/"
            f"departments/{department.id}/"
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def response_items(self, response):
        if isinstance(response.data, dict):
            return response.data.get("results", [])

        return response.data


class StaffDepartmentListAPITests(StaffDepartmentAPITestBase):

    def test_school_admin_can_list_departments(self):
        department = self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(department.id), department_ids)

    def test_department_list_is_isolated_to_requested_school(self):
        local_department = self.create_department("Sciences")

        foreign_department = self.create_department(
            "Foreign Department",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(local_department.id), department_ids)
        self.assertNotIn(str(foreign_department.id), department_ids)

    def test_principal_can_list_departments(self):
        principal = self.create_user("principal@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        self.create_department("Sciences")

        self.authenticate(principal)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_accountant_cannot_list_departments(self):
        accountant = self.create_user("accountant@example.com")

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.authenticate(accountant)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_cannot_list_departments(self):
        teacher = self.create_user("teacher@example.com")

        self.create_membership(
            teacher,
            self.school,
            SchoolMembership.Role.TEACHER,
        )

        self.authenticate(teacher)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_role_cannot_list_departments_by_default(self):
        staff = self.create_user("staff@example.com")

        self.create_membership(
            staff,
            self.school,
            SchoolMembership.Role.STAFF,
        )

        self.authenticate(staff)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_without_membership_cannot_list_departments(self):
        outsider = self.create_user("outsider@example.com")

        self.authenticate(outsider)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_list_departments(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_inactive_membership_cannot_list_departments(self):
        user = self.create_user("inactive@example.com")

        self.create_membership(
            user,
            self.school,
            SchoolMembership.Role.SCHOOL_ADMIN,
            membership_status=SchoolMembership.Status.SUSPENDED,
        )

        self.authenticate(user)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_departments_cannot_be_accessed_when_school_is_suspended(self):
        self.school.status = School.Status.SUSPENDED
        self.school.save()

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class StaffDepartmentCreateAPITests(StaffDepartmentAPITestBase):

    def test_school_admin_can_create_department(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "name": "Sciences",
                "description": "Science department",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            StaffDepartment.objects.filter(
                school=self.school,
                name="Sciences",
            ).exists()
        )

    def test_created_department_belongs_to_url_school(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "name": "Mathematics",
                "school": str(self.other_school.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        department = StaffDepartment.objects.get(
            name="Mathematics",
        )

        self.assertEqual(
            department.school_id,
            self.school.id,
        )

    def test_principal_cannot_create_department_by_default(self):
        principal = self.create_user("principal-create@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        self.authenticate(principal)

        response = self.client.post(
            self.list_url,
            {"name": "Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_principal_can_create_department_with_custom_permission(self):
        principal = self.create_user("principal-custom@example.com")

        membership = self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        membership.custom_permissions.create(
            permission=SchoolPermissions.STAFF_MANAGE,
            is_granted=True,
        )

        self.authenticate(principal)

        response = self.client.post(
            self.list_url,
            {"name": "Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_custom_permission_can_deny_staff_management(self):
        membership = SchoolMembership.objects.get(
            school=self.school,
            user=self.admin,
        )

        membership.custom_permissions.create(
            permission=SchoolPermissions.STAFF_MANAGE,
            is_granted=False,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {"name": "Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_duplicate_department_name_is_rejected(self):
        self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {"name": "Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_department_name_is_case_insensitive_for_duplicate_check(self):
        self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {"name": "SCIENCES"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_department_name_is_trimmed(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {"name": "  Sciences  "},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            StaffDepartment.objects.filter(
                school=self.school,
                name="Sciences",
            ).exists()
        )

    def test_empty_department_name_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {"name": "   "},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_same_department_name_is_allowed_in_another_school(self):
        self.create_department(
            "Sciences",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {"name": "Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


class StaffDepartmentDetailAPITests(StaffDepartmentAPITestBase):

    def test_school_admin_can_retrieve_department(self):
        department = self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.get(
            self.department_detail_url(department)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(department.id),
        )

    def test_school_admin_can_update_department(self):
        department = self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.patch(
            self.department_detail_url(department),
            {"name": "Natural Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department.refresh_from_db()

        self.assertEqual(
            department.name,
            "Natural Sciences",
        )

    def test_department_from_another_school_is_not_accessible(self):
        foreign_department = self.create_department(
            "Foreign Department",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.get(
            self.department_detail_url(foreign_department)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_principal_can_retrieve_department(self):
        principal = self.create_user("principal-detail@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        department = self.create_department("Sciences")

        self.authenticate(principal)

        response = self.client.get(
            self.department_detail_url(department)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_principal_cannot_update_department_by_default(self):
        principal = self.create_user("principal-update@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        department = self.create_department("Sciences")

        self.authenticate(principal)

        response = self.client.patch(
            self.department_detail_url(department),
            {"name": "Updated Sciences"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_school_admin_can_deactivate_department(self):
        department = self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.patch(
            self.department_detail_url(department),
            {"is_active": False},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department.refresh_from_db()

        self.assertFalse(department.is_active)

    def test_school_admin_can_reactivate_department(self):
        department = self.create_department(
            "Sciences",
            is_active=False,
        )

        self.authenticate(self.admin)

        response = self.client.patch(
            self.department_detail_url(department),
            {"is_active": True},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department.refresh_from_db()

        self.assertTrue(department.is_active)

    def test_department_cannot_be_deleted(self):
        department = self.create_department("Sciences")

        self.authenticate(self.admin)

        response = self.client.delete(
            self.department_detail_url(department)
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ],
        )

        self.assertTrue(
            StaffDepartment.objects.filter(
                pk=department.pk,
            ).exists()
        )