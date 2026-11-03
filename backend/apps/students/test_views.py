from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.schools.models import School, SchoolMembership
from apps.students.models import (
    Student,
    Guardian,
    StudentGuardian,
)


User = get_user_model()


class StudentAPITestBase(APITestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Student API Test School",
            status=School.Status.ACTIVE,
        )

        self.other_school = School.objects.create(
            name="Another Student API Test School",
            status=School.Status.ACTIVE,
        )

        self.admin = self.create_user("admin@example.com")
        self.admin_membership = self.create_membership(
            self.admin,
            self.school,
            SchoolMembership.Role.SCHOOL_ADMIN,
        )

        self.list_url = (
            f"/api/schools/{self.school.id}/students/"
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

    def create_student(
        self,
        admission_number,
        school=None,
        user=None,
        first_name="John",
        last_name="Doe",
    ):
        return Student.objects.create(
            school=school or self.school,
            admission_number=admission_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth="2012-05-10",
            gender=Student.Gender.MALE,
            email=f"{admission_number.lower()}@example.com",
            phone_number="08012345678",
            address="Test Street",
            admission_date="2026-09-01",
            notes="Internal student notes",
            user=user,
        )

    def response_items(self, response):
        if isinstance(response.data, dict):
            return response.data.get("results", [])

        return response.data

    def student_detail_url(self, student):
        return (
            f"/api/schools/{self.school.id}/"
            f"students/{student.id}/"
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)


class StudentListAPITests(StudentAPITestBase):

    def test_school_admin_can_list_students(self):
        student = self.create_student("ADM001")

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        student_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(student.id), student_ids)

    def test_student_list_is_isolated_to_requested_school(self):
        local_student = self.create_student("LOCAL001")

        foreign_student = self.create_student(
            "FOREIGN001",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        student_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(local_student.id), student_ids)
        self.assertNotIn(str(foreign_student.id), student_ids)

    def test_user_without_school_membership_cannot_list_students(self):
        outsider = self.create_user("outsider@example.com")

        self.authenticate(outsider)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_list_students(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_teacher_cannot_list_students(self):
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

    def test_parent_only_sees_linked_children(self):
        parent = self.create_user("parent@example.com")

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        linked_child = self.create_student("CHILD001")
        unrelated_child = self.create_student("CHILD002")

        guardian = Guardian.objects.create(
            school=self.school,
            first_name="Parent",
            last_name="User",
            phone_number="08011111111",
            user=parent,
        )

        StudentGuardian.objects.create(
            student=linked_child,
            guardian=guardian,
            relationship=StudentGuardian.Relationship.FATHER,
        )

        self.authenticate(parent)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        student_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(linked_child.id), student_ids)
        self.assertNotIn(str(unrelated_child.id), student_ids)

    def test_student_only_sees_own_profile(self):
        student_user = self.create_user("student@example.com")

        self.create_membership(
            student_user,
            self.school,
            SchoolMembership.Role.STUDENT,
        )

        own_profile = self.create_student(
            "SELF001",
            user=student_user,
        )

        another_profile = self.create_student("OTHER001")

        self.authenticate(student_user)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        student_ids = [
            str(item["id"])
            for item in self.response_items(response)
        ]

        self.assertIn(str(own_profile.id), student_ids)
        self.assertNotIn(str(another_profile.id), student_ids)


class StudentCreateAPITests(StudentAPITestBase):

    def test_school_admin_can_register_student(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "admission_number": "NEW001",
                "first_name": "Jane",
                "middle_name": "Mary",
                "last_name": "Smith",
                "date_of_birth": "2012-04-15",
                "gender": "female",
                "email": "jane@example.com",
                "phone_number": "08022222222",
                "address": "New Student Street",
                "admission_date": "2026-09-01",
                "notes": "New student",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Student.objects.filter(
                school=self.school,
                admission_number="NEW001",
            ).exists()
        )

    def test_registered_student_belongs_to_url_school(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "admission_number": "SCHOOL001",
                "first_name": "Jane",
                "last_name": "Smith",
                "admission_date": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        student = Student.objects.get(
            admission_number="SCHOOL001",
            school=self.school,
        )

        self.assertEqual(student.school, self.school)

    def test_accountant_cannot_register_students(self):
        accountant = self.create_user("accountant@example.com")

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        self.authenticate(accountant)

        response = self.client.post(
            self.list_url,
            {
                "admission_number": "ACCOUNT001",
                "first_name": "Jane",
                "last_name": "Smith",
                "admission_date": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_parent_cannot_register_students(self):
        parent = self.create_user("parent-create@example.com")

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        self.authenticate(parent)

        response = self.client.post(
            self.list_url,
            {
                "admission_number": "PARENT001",
                "first_name": "Jane",
                "last_name": "Smith",
                "admission_date": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_duplicate_admission_number_is_rejected(self):
        self.create_student("DUPLICATE001")

        self.authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "admission_number": "DUPLICATE001",
                "first_name": "Jane",
                "last_name": "Smith",
                "admission_date": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class StudentDetailAPITests(StudentAPITestBase):

    def test_school_admin_can_retrieve_student(self):
        student = self.create_student("DETAIL001")

        self.authenticate(self.admin)

        response = self.client.get(
            self.student_detail_url(student)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(student.id),
        )

    def test_school_admin_can_update_student(self):
        student = self.create_student("UPDATE001")

        self.authenticate(self.admin)

        response = self.client.patch(
            self.student_detail_url(student),
            {
                "first_name": "Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        student.refresh_from_db()

        self.assertEqual(
            student.first_name,
            "Updated",
        )

    def test_student_from_another_school_is_not_accessible(self):
        foreign_student = self.create_student(
            "FOREIGNDETAIL001",
            school=self.other_school,
        )

        self.authenticate(self.admin)

        response = self.client.get(
            self.student_detail_url(foreign_student)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_parent_cannot_retrieve_unlinked_child(self):
        parent = self.create_user("parent-detail@example.com")

        self.create_membership(
            parent,
            self.school,
            SchoolMembership.Role.PARENT,
        )

        child = self.create_student("UNLINKED001")

        self.authenticate(parent)

        response = self.client.get(
            self.student_detail_url(child)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_student_cannot_retrieve_another_student_profile(self):
        student_user = self.create_user("student-detail@example.com")

        self.create_membership(
            student_user,
            self.school,
            SchoolMembership.Role.STUDENT,
        )

        another_student = self.create_student("ANOTHER001")

        self.authenticate(student_user)

        response = self.client.get(
            self.student_detail_url(another_student)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_student_is_not_allowed(self):
        student = self.create_student("NODELETE001")

        self.authenticate(self.admin)

        response = self.client.delete(
            self.student_detail_url(student)
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ],
        )

        self.assertTrue(
            Student.objects.filter(pk=student.pk).exists()
        )


class StudentDataPrivacyAPITests(StudentAPITestBase):

    def test_accountant_receives_limited_student_information(self):
        accountant = self.create_user("accountant-privacy@example.com")

        self.create_membership(
            accountant,
            self.school,
            SchoolMembership.Role.ACCOUNTANT,
        )

        student = self.create_student("PRIVACY001")

        self.authenticate(accountant)

        response = self.client.get(
            self.student_detail_url(student)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        restricted_fields = [
            "date_of_birth",
            "email",
            "phone_number",
            "address",
            "passport",
            "notes",
        ]

        for field in restricted_fields:
            self.assertNotIn(
                field,
                response.data,
                msg=f"Accountant response exposes restricted field: {field}",
            )

    def test_school_admin_can_access_full_student_information(self):
        student = self.create_student("FULLDATA001")

        self.authenticate(self.admin)

        response = self.client.get(
            self.student_detail_url(student)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("date_of_birth", response.data)
        self.assertIn("address", response.data)
        self.assertIn("notes", response.data)