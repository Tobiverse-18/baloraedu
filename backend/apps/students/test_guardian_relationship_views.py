from rest_framework import status

from apps.schools.models import SchoolMembership
from apps.students.models import Guardian, StudentGuardian

from .test_views import StudentAPITestBase


class StudentGuardianAPITestBase(StudentAPITestBase):

    @property
    def relationship_list_url(self):
        return (
            f"/api/schools/{self.school.id}/"
            "guardians/relationships/"
        )

    def relationship_detail_url(self, relationship):
        return (
            f"/api/schools/{self.school.id}/"
            f"guardians/relationships/{relationship.id}/"
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

    def create_relationship(
        self,
        student=None,
        guardian=None,
        relationship=StudentGuardian.Relationship.GUARDIAN,
        **kwargs,
    ):
        student = student or self.create_student("REL001")
        guardian = guardian or self.create_guardian()

        return StudentGuardian.objects.create(
            student=student,
            guardian=guardian,
            relationship=relationship,
            **kwargs,
        )

    def relationship_payload(
        self,
        student,
        guardian,
        **kwargs,
    ):
        payload = {
            "student": str(student.id),
            "guardian": str(guardian.id),
            "relationship": StudentGuardian.Relationship.GUARDIAN,
            "is_primary": False,
            "is_emergency_contact": False,
            "can_pickup_student": True,
            "receives_notifications": True,
        }

        payload.update(kwargs)

        return payload


class StudentGuardianListAPITests(StudentGuardianAPITestBase):

    def test_school_admin_can_list_relationships(self):
        relationship = self.create_relationship()

        self.authenticate(self.admin)

        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        relationship_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(relationship.id), relationship_ids)

    def test_relationship_list_is_isolated_to_requested_school(self):
        local_relationship = self.create_relationship(
            student=self.create_student("LOCALREL001"),
        )

        foreign_student = self.create_student(
            "FOREIGNREL001",
            school=self.other_school,
        )

        foreign_guardian = self.create_guardian(
            school=self.other_school,
            phone_number="08022222222",
        )

        foreign_relationship = StudentGuardian.objects.create(
            student=foreign_student,
            guardian=foreign_guardian,
        )

        self.authenticate(self.admin)

        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        relationship_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(local_relationship.id), relationship_ids)
        self.assertNotIn(str(foreign_relationship.id), relationship_ids)

    def test_accountant_can_list_relationships(self):
        accountant = self.create_user(
            "relationship-accountant@example.com",
        )

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.create_relationship()

        self.authenticate(accountant)

        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_parent_only_sees_own_relationships(self):
        parent = self.create_user(
            "relationship-parent@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        own_student = self.create_student("PARENTCHILD001")
        another_student = self.create_student("OTHERCHILD001")

        own_guardian = self.create_guardian(
            first_name="Own",
            user=parent,
            phone_number="08033333333",
        )

        another_guardian = self.create_guardian(
            first_name="Another",
            phone_number="08044444444",
        )

        own_relationship = self.create_relationship(
            student=own_student,
            guardian=own_guardian,
        )

        another_relationship = self.create_relationship(
            student=another_student,
            guardian=another_guardian,
        )

        self.authenticate(parent)

        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        relationship_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(own_relationship.id), relationship_ids)
        self.assertNotIn(str(another_relationship.id), relationship_ids)

    def test_teacher_cannot_list_relationships(self):
        teacher = self.create_user(
            "relationship-teacher@example.com",
        )

        self.create_membership(
            teacher,
            self.school,
            SchoolMembership.Role.TEACHER,
        )

        self.authenticate(teacher)

        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_student_cannot_list_relationships(self):
        student = self.create_user(
            "relationship-student@example.com",
        )

        self.create_membership(
            student,
            self.school,
            SchoolMembership.Role.STUDENT,
        )

        self.authenticate(student)

        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_list_relationships(self):
        response = self.client.get(self.relationship_list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class StudentGuardianCreateAPITests(StudentGuardianAPITestBase):

    def test_school_admin_can_create_relationship(self):
        student = self.create_student("CREATE001")
        guardian = self.create_guardian(
            phone_number="08055555555",
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(
                student,
                guardian,
                relationship=StudentGuardian.Relationship.FATHER,
                is_primary=True,
                is_emergency_contact=True,
                can_pickup_student=True,
                receives_notifications=True,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            StudentGuardian.objects.filter(
                student=student,
                guardian=guardian,
                is_primary=True,
                is_emergency_contact=True,
            ).exists()
        )

    def test_created_relationship_uses_school_from_student_and_guardian(self):
        student = self.create_student("SCHOOLREL001")
        guardian = self.create_guardian(
            phone_number="08066666666",
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(student, guardian),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        relationship = StudentGuardian.objects.get(
            student=student,
            guardian=guardian,
        )

        self.assertEqual(relationship.student.school, self.school)
        self.assertEqual(relationship.guardian.school, self.school)

    def test_accountant_cannot_create_relationship(self):
        accountant = self.create_user(
            "relationship-accountant-create@example.com",
        )

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        student = self.create_student("ACCOUNTREL001")
        guardian = self.create_guardian(
            phone_number="08077777777",
        )

        self.authenticate(accountant)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(student, guardian),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_parent_cannot_create_relationship(self):
        parent = self.create_user(
            "relationship-parent-create@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        student = self.create_student("PARENTREL001")
        guardian = self.create_guardian(
            phone_number="08088888888",
        )

        self.authenticate(parent)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(student, guardian),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_duplicate_student_guardian_relationship_is_rejected(self):
        student = self.create_student("DUPREL001")
        guardian = self.create_guardian(
            phone_number="08099999999",
        )

        self.create_relationship(
            student=student,
            guardian=guardian,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(student, guardian),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_second_primary_guardian_for_same_student_is_rejected(self):
        student = self.create_student("PRIMARYREL001")

        first_guardian = self.create_guardian(
            phone_number="08010101010",
        )

        second_guardian = self.create_guardian(
            phone_number="08020202020",
        )

        self.create_relationship(
            student=student,
            guardian=first_guardian,
            is_primary=True,
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(
                student,
                second_guardian,
                is_primary=True,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_relationship_between_different_schools_is_rejected(self):
        student = self.create_student("CROSSREL001")

        foreign_guardian = self.create_guardian(
            school=self.other_school,
            phone_number="08030303030",
        )

        self.authenticate(self.admin)

        response = self.client.post(
            self.relationship_list_url,
            self.relationship_payload(
                student,
                foreign_guardian,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class StudentGuardianDetailAPITests(StudentGuardianAPITestBase):

    def test_school_admin_can_retrieve_relationship(self):
        relationship = self.create_relationship()

        self.authenticate(self.admin)

        response = self.client.get(
            self.relationship_detail_url(relationship),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(relationship.id),
        )

    def test_school_admin_can_update_relationship(self):
        relationship = self.create_relationship(
            can_pickup_student=False,
        )

        self.authenticate(self.admin)

        response = self.client.patch(
            self.relationship_detail_url(relationship),
            {
                "can_pickup_student": True,
                "is_emergency_contact": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        relationship.refresh_from_db()

        self.assertTrue(relationship.can_pickup_student)
        self.assertTrue(relationship.is_emergency_contact)

    def test_relationship_from_another_school_is_not_accessible(self):
        foreign_student = self.create_student(
            "FOREIGNDETAILREL001",
            school=self.other_school,
        )

        foreign_guardian = self.create_guardian(
            school=self.other_school,
            phone_number="08040404040",
        )

        foreign_relationship = StudentGuardian.objects.create(
            student=foreign_student,
            guardian=foreign_guardian,
        )

        self.authenticate(self.admin)

        response = self.client.get(
            self.relationship_detail_url(foreign_relationship),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_parent_cannot_retrieve_another_guardians_relationship(self):
        parent = self.create_user(
            "relationship-detail-parent@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        relationship = self.create_relationship()

        self.authenticate(parent)

        response = self.client.get(
            self.relationship_detail_url(relationship),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_parent_can_retrieve_own_relationship(self):
        parent = self.create_user(
            "relationship-own-parent@example.com",
        )

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        student = self.create_student("OWNREL001")

        guardian = self.create_guardian(
            user=parent,
            phone_number="08050505050",
        )

        relationship = self.create_relationship(
            student=student,
            guardian=guardian,
        )

        self.authenticate(parent)

        response = self.client.get(
            self.relationship_detail_url(relationship),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_delete_relationship_is_not_allowed(self):
        relationship = self.create_relationship()

        self.authenticate(self.admin)

        response = self.client.delete(
            self.relationship_detail_url(relationship),
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ],
        )

        self.assertTrue(
            StudentGuardian.objects.filter(
                pk=relationship.pk,
            ).exists()
        )