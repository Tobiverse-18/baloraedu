from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from apps.schools.models import School, SchoolMembership
from apps.schools.permission_registry import SchoolPermissions
from apps.staff.models import StaffDepartment, StaffProfile


User = get_user_model()


class StaffProfileAPITestBase(APITestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Staff Profile Test School",
            status=School.Status.ACTIVE,
        )

        self.other_school = School.objects.create(
            name="Another Staff Profile Test School",
            status=School.Status.ACTIVE,
        )

        self.admin = self.create_user("profile-admin@example.com")

        self.create_membership(
            self.admin,
            self.school,
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.list_url = (
            f"/api/schools/{self.school.id}/staff/profiles/"
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
        name="Sciences",
        school=None,
        is_active=True,
    ):
        return StaffDepartment.objects.create(
            school=school or self.school,
            name=name,
            is_active=is_active,
        )

    def create_staff_profile(
        self,
        staff_number="STF001",
        school=None,
        **kwargs,
    ):
        return StaffProfile.objects.create(
            school=school or self.school,
            staff_number=staff_number,
            first_name=kwargs.pop("first_name", "John"),
            last_name=kwargs.pop("last_name", "Doe"),
            job_title=kwargs.pop("job_title", "Administrator"),
            **kwargs,
        )

    def profile_detail_url(self, profile):
        return (
            f"/api/schools/{self.school.id}/staff/"
            f"profiles/{profile.id}/"
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def response_items(self, response):
        if isinstance(response.data, dict):
            return response.data.get("results", [])

        return response.data


class StaffProfileListAPITests(StaffProfileAPITestBase):

    def test_school_admin_can_list_staff_profiles(self):
        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        profile_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(profile.id), profile_ids)

    def test_staff_profile_list_is_isolated_to_requested_school(self):
        local_profile = self.create_staff_profile(
            staff_number="LOCAL001",
        )

        foreign_profile = self.create_staff_profile(
            staff_number="FOREIGN001",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        profile_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(local_profile.id), profile_ids)
        self.assertNotIn(str(foreign_profile.id), profile_ids)

    def test_principal_can_list_staff_profiles(self):
        principal = self.create_user("profile-principal@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        self.create_staff_profile()

        self.authenticate(principal)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_accountant_cannot_list_staff_profiles(self):
        accountant = self.create_user("profile-accountant@example.com")

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

    def test_teacher_cannot_list_staff_profiles(self):
        teacher = self.create_user("profile-teacher@example.com")

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

    def test_staff_role_cannot_list_profiles_by_default(self):
        staff = self.create_user("profile-staff@example.com")

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

    def test_user_without_membership_cannot_list_profiles(self):
        outsider = self.create_user("profile-outsider@example.com")

        self.authenticate(outsider)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_list_profiles(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_suspended_membership_cannot_list_profiles(self):
        user = self.create_user("profile-suspended@example.com")

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


class StaffProfileCreateAPITests(StaffProfileAPITestBase):

    def test_school_admin_can_create_non_teaching_profile(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF100",
                "first_name": "Jane",
                "last_name": "Smith",
                "job_title": "Accountant",
                "staff_type": StaffProfile.StaffType.NON_TEACHING,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        profile = StaffProfile.objects.get(
            school=self.school,
            staff_number="STF100",
        )

        self.assertEqual(profile.first_name, "Jane")
        self.assertEqual(profile.last_name, "Smith")
        self.assertEqual(profile.user, None)

    def test_school_admin_can_create_teaching_profile(self):
        department = self.create_department()

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "TCH100",
                "first_name": "Mary",
                "last_name": "Johnson",
                "job_title": "Mathematics Teacher",
                "staff_type": StaffProfile.StaffType.TEACHING,
                "department": str(department.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        profile = StaffProfile.objects.get(
            staff_number="TCH100",
            school=self.school,
        )

        self.assertEqual(
            profile.staff_type,
            StaffProfile.StaffType.TEACHING,
        )

        self.assertEqual(
            profile.department_id,
            department.id,
        )

    def test_school_is_assigned_from_url(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF101",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Secretary",
                "school": str(self.other_school.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        profile = StaffProfile.objects.get(
            staff_number="STF101",
        )

        self.assertEqual(
            profile.school_id,
            self.school.id,
        )

    def test_creating_profile_does_not_create_login_account(self):
        initial_user_count = User.objects.count()

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF102",
                "first_name": "Peter",
                "last_name": "James",
                "job_title": "Cleaner",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            User.objects.count(),
            initial_user_count,
        )

        profile = StaffProfile.objects.get(
            staff_number="STF102",
        )

        self.assertIsNone(profile.user)

    def test_duplicate_staff_number_is_rejected(self):
        self.create_staff_profile(
            staff_number="STF200",
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF200",
                "first_name": "Another",
                "last_name": "Person",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_number_duplicate_check_is_case_insensitive(self):
        self.create_staff_profile(
            staff_number="STF200",
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "stf200",
                "first_name": "Another",
                "last_name": "Person",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_number_is_trimmed(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "  STF201  ",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertTrue(
            StaffProfile.objects.filter(
                school=self.school,
                staff_number="STF201",
            ).exists()
        )

    def test_empty_staff_number_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "   ",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_empty_first_name_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF202",
                "first_name": "   ",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_empty_last_name_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF203",
                "first_name": "John",
                "last_name": "   ",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_empty_job_title_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF204",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "   ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_profile_names_are_trimmed(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF205",
                "first_name": "  John  ",
                "middle_name": "  Michael  ",
                "last_name": "  Smith  ",
                "job_title": "  Teacher  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        profile = StaffProfile.objects.get(
            staff_number="STF205",
        )

        self.assertEqual(profile.first_name, "John")
        self.assertEqual(profile.middle_name, "Michael")
        self.assertEqual(profile.last_name, "Smith")
        self.assertEqual(profile.job_title, "Teacher")

    def test_department_from_another_school_is_rejected(self):
        foreign_department = self.create_department(
            name="Foreign Department",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF206",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
                "department": str(foreign_department.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_inactive_department_cannot_be_assigned(self):
        department = self.create_department(
            is_active=False,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF207",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
                "department": str(department.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_same_staff_number_is_allowed_in_another_school(self):
        self.create_staff_profile(
            staff_number="SHARED001",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "SHARED001",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

    def test_teacher_account_can_be_linked_to_teaching_profile(self):
        teacher = self.create_user("linked-teacher@example.com")

        self.create_membership(
            teacher,
            self.school,
            SchoolMembership.Role.TEACHER,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "TCH300",
                "first_name": "Mary",
                "last_name": "Teacher",
                "job_title": "Mathematics Teacher",
                "staff_type": StaffProfile.StaffType.TEACHING,
                "user": str(teacher.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        profile = StaffProfile.objects.get(
            staff_number="TCH300",
        )

        self.assertEqual(profile.user_id, teacher.id)

    def test_principal_account_can_be_linked_to_teaching_profile(self):
        principal = self.create_user("linked-principal@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "TCH301",
                "first_name": "Mary",
                "last_name": "Principal",
                "job_title": "Principal",
                "staff_type": StaffProfile.StaffType.TEACHING,
                "user": str(principal.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

    def test_teacher_account_cannot_be_linked_to_non_teaching_profile(self):
        teacher = self.create_user("wrong-role-teacher@example.com")

        self.create_membership(
            teacher,
            self.school,
            SchoolMembership.Role.TEACHER,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF300",
                "first_name": "Mary",
                "last_name": "Teacher",
                "job_title": "Office Assistant",
                "staff_type": StaffProfile.StaffType.NON_TEACHING,
                "user": str(teacher.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_account_from_another_school_cannot_be_linked(self):
        foreign_user = self.create_user("foreign-teacher@example.com")

        self.create_membership(
            foreign_user,
            self.other_school,
            SchoolMembership.Role.TEACHER,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "TCH302",
                "first_name": "Foreign",
                "last_name": "Teacher",
                "job_title": "Teacher",
                "staff_type": StaffProfile.StaffType.TEACHING,
                "user": str(foreign_user.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_same_account_cannot_be_linked_to_two_profiles(self):
        teacher = self.create_user("duplicate-link@example.com")

        self.create_membership(
            teacher,
            self.school,
            SchoolMembership.Role.TEACHER,
        )

        self.create_staff_profile(
            staff_number="TCH303",
            staff_type=StaffProfile.StaffType.TEACHING,
            user=teacher,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "TCH304",
                "first_name": "Another",
                "last_name": "Teacher",
                "job_title": "Teacher",
                "staff_type": StaffProfile.StaffType.TEACHING,
                "user": str(teacher.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_principal_cannot_create_profile_by_default(self):
        principal = self.create_user("profile-principal-create@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        self.authenticate(principal)

        response = self.client.post(
            self.list_url,
            {
                "staff_number": "STF400",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_principal_can_create_profile_with_custom_permission(self):
        principal = self.create_user(
            "profile-principal-custom@example.com"
        )

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
            {
                "staff_number": "STF401",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

    def test_custom_permission_can_deny_admin_profile_creation(self):
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
            {
                "staff_number": "STF402",
                "first_name": "John",
                "last_name": "Smith",
                "job_title": "Teacher",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class StaffProfileDetailAPITests(StaffProfileAPITestBase):

    def test_school_admin_can_retrieve_profile(self):
        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.get(
            self.profile_detail_url(profile)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(profile.id),
        )

    def test_school_admin_can_update_profile(self):
        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {
                "job_title": "Senior Administrator",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.job_title,
            "Senior Administrator",
        )

    def test_staff_profile_from_another_school_is_not_accessible(self):
        foreign_profile = self.create_staff_profile(
            staff_number="FOREIGN002",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.get(
            self.profile_detail_url(foreign_profile)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_principal_can_retrieve_profile(self):
        principal = self.create_user("profile-principal-detail@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        profile = self.create_staff_profile()

        self.authenticate(principal)

        response = self.client.get(
            self.profile_detail_url(profile)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_principal_cannot_update_profile_by_default(self):
        principal = self.create_user("profile-principal-edit@example.com")

        self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        profile = self.create_staff_profile()

        self.authenticate(principal)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"job_title": "Updated Title"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_principal_can_update_profile_with_custom_permission(self):
        principal = self.create_user(
            "profile-principal-edit-custom@example.com"
        )

        membership = self.create_membership(
            principal,
            self.school,
            SchoolMembership.Role.PRINCIPAL,
        )

        membership.custom_permissions.create(
            permission=SchoolPermissions.STAFF_MANAGE,
            is_granted=True,
        )

        profile = self.create_staff_profile()

        self.authenticate(principal)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"job_title": "Senior Teacher"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.job_title,
            "Senior Teacher",
        )

    def test_school_admin_can_update_staff_status(self):
        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"status": StaffProfile.Status.ON_LEAVE},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.status,
            StaffProfile.Status.ON_LEAVE,
        )

    def test_school_admin_can_reassign_department(self):
        old_department = self.create_department("Sciences")

        new_department = self.create_department("Administration")

        profile = self.create_staff_profile(
            department=old_department,
        )

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"department": str(new_department.id)},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.department_id,
            new_department.id,
        )

    def test_existing_staff_can_keep_inactive_department(self):
        department = self.create_department("Sciences")

        profile = self.create_staff_profile(
            department=department,
        )

        department.is_active = False
        department.save()

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"job_title": "Senior Teacher"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.department_id,
            department.id,
        )

    def test_staff_cannot_be_reassigned_to_inactive_department(self):
        department = self.create_department(
            "Inactive Department",
            is_active=False,
        )

        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"department": str(department.id)},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_number_cannot_be_changed_to_duplicate(self):
        first = self.create_staff_profile(
            staff_number="STF501",
        )

        self.create_staff_profile(
            staff_number="STF502",
        )

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(first),
            {"staff_number": "STF502"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_school_field_cannot_be_changed(self):
        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"school": str(self.other_school.id)},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.school_id,
            self.school.id,
        )

    def test_invalid_termination_date_is_rejected(self):
        profile = self.create_staff_profile(
            employment_date="2025-01-01",
        )

        self.authenticate(self.admin)

        response = self.client.patch(
            self.profile_detail_url(profile),
            {"termination_date": "2024-01-01"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_profile_cannot_be_deleted(self):
        profile = self.create_staff_profile()

        self.authenticate(self.admin)

        response = self.client.delete(
            self.profile_detail_url(profile)
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ],
        )

        self.assertTrue(
            StaffProfile.objects.filter(
                pk=profile.pk,
            ).exists()
        )