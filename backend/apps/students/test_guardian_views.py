
from rest_framework import status

from apps.schools.models import SchoolMembership
from apps.students.models import Guardian

from .test_views import StudentAPITestBase


class GuardianAPITestBase(StudentAPITestBase):

    @property
    def guardian_list_url(self):
        return f"/api/schools/{self.school.id}/guardians/"

    def guardian_detail_url(self, guardian):
        return (
            f"/api/schools/{self.school.id}/"
            f"guardians/{guardian.id}/"
        )

    def create_guardian(
        self,
        first_name="Jane",
        last_name="Doe",
        school=None,
        user=None,
        phone_number="08012345678",
        **kwargs,
    ):
        return Guardian.objects.create(
            school=school or self.school,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user=user,
            **kwargs,
        )


class GuardianListAPITests(GuardianAPITestBase):

    def test_school_admin_can_list_guardians(self):
        guardian = self.create_guardian(
            first_name="Mary",
            last_name="Johnson",
        )

        self.authenticate(self.admin)

        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        guardian_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(guardian.id), guardian_ids)

    def test_guardian_list_is_isolated_to_requested_school(self):
        local_guardian = self.create_guardian(
            phone_number="08011111111",
        )

        foreign_guardian = self.create_guardian(
            school=self.other_school,
            phone_number="08022222222",
        )

        self.authenticate(self.admin)

        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        guardian_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(local_guardian.id), guardian_ids)
        self.assertNotIn(str(foreign_guardian.id), guardian_ids)

    def test_user_without_membership_cannot_list_guardians(self):
        outsider = self.create_user("guardian-outsider@example.com")

        self.authenticate(outsider)

        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_list_guardians(self):
        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_teacher_cannot_list_guardians(self):
        teacher = self.create_user("guardian-teacher@example.com")

        self.create_membership(
            teacher,
            self.school,
            SchoolMembership.Role.TEACHER,
        )

        self.authenticate(teacher)

        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_parent_only_sees_own_guardian_profile(self):
        parent = self.create_user("guardian-parent@example.com")

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        own_guardian = self.create_guardian(
            first_name="Parent",
            last_name="One",
            user=parent,
            phone_number="08033333333",
        )

        another_guardian = self.create_guardian(
            first_name="Parent",
            last_name="Two",
            phone_number="08044444444",
        )

        self.authenticate(parent)

        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        guardian_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(own_guardian.id), guardian_ids)
        self.assertNotIn(str(another_guardian.id), guardian_ids)

    def test_student_cannot_list_guardians(self):
        student = self.create_user("guardian-student@example.com")

        self.create_membership(
            student,
            self.school,
            SchoolMembership.Role.STUDENT,
        )

        self.authenticate(student)

        response = self.client.get(self.guardian_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class GuardianCreateAPITests(GuardianAPITestBase):

    def test_school_admin_can_register_guardian(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.guardian_list_url,
            {
                "first_name": "Mary",
                "last_name": "Johnson",
                "gender": "female",
                "email": "mary@example.com",
                "phone_number": "08055555555",
                "alternative_phone_number": "08066666666",
                "occupation": "Teacher",
                "address": "Guardian Street",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Guardian.objects.filter(
                school=self.school,
                phone_number="08055555555",
            ).exists()
        )

    def test_registered_guardian_belongs_to_url_school(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.guardian_list_url,
            {
                "first_name": "John",
                "last_name": "Smith",
                "phone_number": "08077777777",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        guardian = Guardian.objects.get(
            phone_number="08077777777",
            school=self.school,
        )

        self.assertEqual(guardian.school, self.school)

    def test_accountant_cannot_register_guardians(self):
        accountant = self.create_user(
            "guardian-accountant@example.com",
        )

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.authenticate(accountant)

        response = self.client.post(
            self.guardian_list_url,
            {
                "first_name": "Accountant",
                "last_name": "Test",
                "phone_number": "08088888888",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_parent_cannot_register_guardians(self):
        parent = self.create_user(
            "guardian-parent-create@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        self.authenticate(parent)

        response = self.client.post(
            self.guardian_list_url,
            {
                "first_name": "Parent",
                "last_name": "Test",
                "phone_number": "08099999999",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_student_cannot_register_guardians(self):
        student = self.create_user(
            "guardian-student-create@example.com",
        )

        self.create_membership(
            student,
            self.school,
            SchoolMembership.Role.STUDENT,
        )

        self.authenticate(student)

        response = self.client.post(
            self.guardian_list_url,
            {
                "first_name": "Student",
                "last_name": "Test",
                "phone_number": "08012121212",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class GuardianDetailAPITests(GuardianAPITestBase):

    def test_school_admin_can_retrieve_guardian(self):
        guardian = self.create_guardian()

        self.authenticate(self.admin)

        response = self.client.get(
            self.guardian_detail_url(guardian),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(guardian.id),
        )

    def test_school_admin_can_update_guardian(self):
        guardian = self.create_guardian(
            first_name="Old",
        )

        self.authenticate(self.admin)

        response = self.client.patch(
            self.guardian_detail_url(guardian),
            {
                "first_name": "Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        guardian.refresh_from_db()

        self.assertEqual(
            guardian.first_name,
            "Updated",
        )

    def test_guardian_from_another_school_is_not_accessible(self):
        foreign_guardian = self.create_guardian(
            school=self.other_school,
            phone_number="08013131313",
        )

        self.authenticate(self.admin)

        response = self.client.get(
            self.guardian_detail_url(foreign_guardian),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_parent_cannot_retrieve_another_guardian(self):
        parent = self.create_user(
            "guardian-detail-parent@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        another_guardian = self.create_guardian(
            phone_number="08014141414",
        )

        self.authenticate(parent)

        response = self.client.get(
            self.guardian_detail_url(another_guardian),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_parent_can_retrieve_own_guardian_profile(self):
        parent = self.create_user(
            "guardian-own-detail@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        guardian = self.create_guardian(
            first_name="My",
            last_name="Profile",
            user=parent,
            phone_number="08015151515",
        )

        self.authenticate(parent)

        response = self.client.get(
            self.guardian_detail_url(guardian),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_delete_guardian_is_not_allowed(self):
        guardian = self.create_guardian()

        self.authenticate(self.admin)

        response = self.client.delete(
            self.guardian_detail_url(guardian),
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ],
        )

        self.assertTrue(
            Guardian.objects.filter(pk=guardian.pk).exists()
        )


class GuardianDataPrivacyAPITests(GuardianAPITestBase):

    def test_accountant_receives_limited_guardian_information(self):
        accountant = self.create_user(
            "guardian-accountant-privacy@example.com",
        )

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        guardian = self.create_guardian(
            first_name="Private",
            last_name="Guardian",
            email="private@example.com",
            phone_number="08016161616",
            alternative_phone_number="08017171717",
            occupation="Business Owner",
            address="Private Address",
        )

        self.authenticate(accountant)

        response = self.client.get(
            self.guardian_detail_url(guardian),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        restricted_fields = [
            "email",
            "alternative_phone_number",
            "occupation",
            "address",
        ]

        for field in restricted_fields:
            self.assertNotIn(
                field,
                response.data,
                msg=f"Accountant response exposes restricted field: {field}",
            )

    def test_school_admin_can_access_full_guardian_information(self):
        guardian = self.create_guardian(
            email="fullguardian@example.com",
            alternative_phone_number="08018181818",
            occupation="Engineer",
            address="Full Guardian Address",
        )

        self.authenticate(self.admin)

        response = self.client.get(
            self.guardian_detail_url(guardian),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("email", response.data)
        self.assertIn("alternative_phone_number", response.data)
        self.assertIn("occupation", response.data)
        self.assertIn("address", response.data)
