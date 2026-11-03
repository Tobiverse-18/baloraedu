
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.schools.models import School, SchoolMembership
from apps.academics.models import (
    AcademicSession,
    ClassLevel,
    SchoolClass,
)

from .models import (
    Student,
    Guardian,
    StudentGuardian,
    StudentEnrollment,
)


User = get_user_model()


class StudentModelTestBase(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Student Test School",
        )

        self.other_school = School.objects.create(
            name="Another Student Test School",
        )

        self.session = AcademicSession.objects.create(
            school=self.school,
            name="2026/2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
        )

        self.other_session = AcademicSession.objects.create(
            school=self.other_school,
            name="2026/2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
        )

        self.class_level = ClassLevel.objects.create(
            school=self.school,
            name="JSS 1",
            category=ClassLevel.Category.JUNIOR_SECONDARY,
        )

        self.school_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="A",
        )

        self.other_class_level = ClassLevel.objects.create(
            school=self.other_school,
            name="JSS 1",
            category=ClassLevel.Category.JUNIOR_SECONDARY,
        )

        self.other_school_class = SchoolClass.objects.create(
            school=self.other_school,
            class_level=self.other_class_level,
            section_name="A",
        )

    def create_student(self, **kwargs):
        defaults = {
            "school": self.school,
            "admission_number": "BAL-001",
            "first_name": "John",
            "last_name": "Doe",
        }

        defaults.update(kwargs)

        return Student.objects.create(**defaults)

    def create_guardian(self, **kwargs):
        defaults = {
            "school": self.school,
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": "08012345678",
        }

        defaults.update(kwargs)

        return Guardian.objects.create(**defaults)

    def create_enrollment(self, **kwargs):
        defaults = {
            "school": self.school,
            "session": self.session,
            "school_class": self.school_class,
            "enrollment_date": date(2026, 9, 10),
        }

        defaults.update(kwargs)

        if "student" not in defaults:
            defaults["student"] = self.create_student()

        return StudentEnrollment.objects.create(**defaults)


class StudentModelTests(StudentModelTestBase):

    def test_student_can_be_created(self):
        student = self.create_student()

        self.assertEqual(student.school, self.school)
        self.assertEqual(student.admission_number, "BAL-001")
        self.assertEqual(student.status, Student.Status.ACTIVE)

    def test_student_has_uuid_primary_key(self):
        student = self.create_student()

        self.assertIsNotNone(student.id)

    def test_student_full_name_includes_middle_name(self):
        student = self.create_student(
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
        )

        self.assertEqual(
            student.full_name,
            "John Michael Doe",
        )

    def test_student_full_name_works_without_middle_name(self):
        student = self.create_student()

        self.assertEqual(student.full_name, "John Doe")

    def test_student_string_representation(self):
        student = self.create_student()

        self.assertEqual(
            str(student),
            "John Doe (BAL-001)",
        )

    def test_student_can_exist_without_portal_account(self):
        student = self.create_student()

        self.assertIsNone(student.user)

    def test_admission_number_must_be_unique_within_school(self):
        self.create_student()

        with self.assertRaises(ValidationError):
            self.create_student(
                first_name="Another",
            )

    def test_same_admission_number_can_exist_in_another_school(self):
        first = self.create_student()

        second = self.create_student(
            school=self.other_school,
        )

        self.assertEqual(
            first.admission_number,
            second.admission_number,
        )

    def test_student_gender_choices_are_available(self):
        expected = {
            "male",
            "female",
            "other",
        }

        actual = {
            value for value, label in Student.Gender.choices
        }

        self.assertEqual(actual, expected)

    def test_student_status_choices_are_available(self):
        expected = {
            "active",
            "inactive",
            "graduated",
            "transferred",
            "withdrawn",
        }

        actual = {
            value for value, label in Student.Status.choices
        }

        self.assertEqual(actual, expected)

    def test_admission_date_cannot_be_before_date_of_birth(self):
        with self.assertRaises(ValidationError):
            self.create_student(
                date_of_birth=date(2010, 5, 10),
                admission_date=date(2009, 9, 1),
            )

    def test_admission_date_can_be_after_date_of_birth(self):
        student = self.create_student(
            date_of_birth=date(2010, 5, 10),
            admission_date=date(2020, 9, 1),
        )

        self.assertEqual(
            student.admission_date,
            date(2020, 9, 1),
        )

    def test_student_can_be_linked_to_valid_student_account(self):
        user = User.objects.create_user(
            email="student@test.com",
            password="TestPassword123!",
            first_name="John",
            last_name="Doe",
        )

        SchoolMembership.objects.create(
            school=self.school,
            user=user,
            role=SchoolMembership.Role.STUDENT,
            status=SchoolMembership.Status.ACTIVE,
        )

        student = self.create_student(user=user)

        self.assertEqual(student.user, user)

    def test_student_account_requires_student_membership(self):
        user = User.objects.create_user(
            email="wrongrole@test.com",
            password="TestPassword123!",
            first_name="Wrong",
            last_name="Role",
        )

        SchoolMembership.objects.create(
            school=self.school,
            user=user,
            role=SchoolMembership.Role.TEACHER,
            status=SchoolMembership.Status.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            self.create_student(user=user)

    def test_student_account_must_belong_to_same_school(self):
        user = User.objects.create_user(
            email="otherschool@test.com",
            password="TestPassword123!",
            first_name="Other",
            last_name="School",
        )

        SchoolMembership.objects.create(
            school=self.other_school,
            user=user,
            role=SchoolMembership.Role.STUDENT,
            status=SchoolMembership.Status.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            self.create_student(user=user)

    def test_one_user_can_be_linked_to_student_profiles_in_multiple_schools(self):
        user = User.objects.create_user(
            email="multischoolstudent@test.com",
            password="TestPassword123!",
            first_name="Multi",
            last_name="School",
        )

        SchoolMembership.objects.create(
            school=self.school,
            user=user,
            role=SchoolMembership.Role.STUDENT,
            status=SchoolMembership.Status.ACTIVE,
        )

        SchoolMembership.objects.create(
            school=self.other_school,
            user=user,
            role=SchoolMembership.Role.STUDENT,
            status=SchoolMembership.Status.ACTIVE,
        )

        first = self.create_student(
            user=user,
        )

        second = self.create_student(
            school=self.other_school,
            user=user,
        )

        self.assertEqual(first.user, second.user)
        self.assertNotEqual(first.school, second.school)


class GuardianModelTests(StudentModelTestBase):

    def test_guardian_can_be_created(self):
        guardian = self.create_guardian()

        self.assertEqual(guardian.school, self.school)
        self.assertEqual(guardian.phone_number, "08012345678")
        self.assertTrue(guardian.is_active)

    def test_guardian_has_uuid_primary_key(self):
        guardian = self.create_guardian()

        self.assertIsNotNone(guardian.id)

    def test_guardian_string_representation(self):
        guardian = self.create_guardian()

        self.assertEqual(str(guardian), "Jane Doe")

    def test_guardian_can_exist_without_portal_account(self):
        guardian = self.create_guardian()

        self.assertIsNone(guardian.user)

    def test_guardian_can_have_optional_contact_information(self):
        guardian = self.create_guardian()

        self.assertEqual(guardian.email, "")
        self.assertEqual(guardian.alternative_phone_number, "")
        self.assertEqual(guardian.occupation, "")
        self.assertEqual(guardian.address, "")

    def test_guardian_can_be_deactivated(self):
        guardian = self.create_guardian(
            is_active=False,
        )

        self.assertFalse(guardian.is_active)

    def test_same_guardian_details_can_exist_in_different_schools(self):
        first = self.create_guardian()

        second = self.create_guardian(
            school=self.other_school,
        )

        self.assertNotEqual(first.id, second.id)


class StudentGuardianTests(StudentModelTestBase):

    def setUp(self):
        super().setUp()

        self.student = self.create_student()

        self.guardian = self.create_guardian()

    def test_student_guardian_link_can_be_created(self):
        link = StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
            relationship=StudentGuardian.Relationship.MOTHER,
        )

        self.assertEqual(link.student, self.student)
        self.assertEqual(link.guardian, self.guardian)
        self.assertEqual(
            link.relationship,
            StudentGuardian.Relationship.MOTHER,
        )

    def test_guardian_can_be_linked_to_multiple_students(self):
        second_student = self.create_student(
            admission_number="BAL-002",
            first_name="Mary",
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
        )

        StudentGuardian.objects.create(
            student=second_student,
            guardian=self.guardian,
        )

        self.assertEqual(
            self.guardian.student_links.count(),
            2,
        )

    def test_student_can_have_multiple_guardians(self):
        second_guardian = self.create_guardian(
            first_name="Peter",
            phone_number="08098765432",
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=second_guardian,
        )

        self.assertEqual(
            self.student.guardian_links.count(),
            2,
        )

    def test_duplicate_student_guardian_link_is_rejected(self):
        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
        )

        with self.assertRaises(ValidationError):
            StudentGuardian.objects.create(
                student=self.student,
                guardian=self.guardian,
            )

    def test_only_one_primary_guardian_is_allowed(self):
        second_guardian = self.create_guardian(
            first_name="Peter",
            phone_number="08098765432",
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
            is_primary=True,
        )

        with self.assertRaises(ValidationError):
            StudentGuardian.objects.create(
                student=self.student,
                guardian=second_guardian,
                is_primary=True,
            )

    def test_multiple_non_primary_guardians_are_allowed(self):
        second_guardian = self.create_guardian(
            first_name="Peter",
            phone_number="08098765432",
        )

        third_guardian = self.create_guardian(
            first_name="Mary",
            phone_number="08087654321",
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=second_guardian,
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=third_guardian,
        )

        self.assertEqual(
            self.student.guardian_links.count(),
            3,
        )

    def test_primary_guardian_can_be_changed(self):
        second_guardian = self.create_guardian(
            first_name="Peter",
            phone_number="08098765432",
        )

        first_link = StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
            is_primary=True,
        )

        first_link.is_primary = False
        first_link.save()

        second_link = StudentGuardian.objects.create(
            student=self.student,
            guardian=second_guardian,
            is_primary=True,
        )

        self.assertTrue(second_link.is_primary)

    def test_guardian_and_student_must_belong_to_same_school(self):
        other_guardian = self.create_guardian(
            school=self.other_school,
        )

        with self.assertRaises(ValidationError):
            StudentGuardian.objects.create(
                student=self.student,
                guardian=other_guardian,
            )

    def test_guardian_link_default_permissions_are_enabled(self):
        link = StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
        )

        self.assertTrue(link.can_pickup_student)
        self.assertTrue(link.receives_notifications)
        self.assertFalse(link.is_primary)
        self.assertFalse(link.is_emergency_contact)

    def test_relationship_choices_are_available(self):
        expected = {
            "father",
            "mother",
            "guardian",
            "stepfather",
            "stepmother",
            "grandparent",
            "uncle",
            "aunt",
            "other",
        }

        actual = {
            value
            for value, label in StudentGuardian.Relationship.choices
        }

        self.assertEqual(actual, expected)


class StudentEnrollmentTests(StudentModelTestBase):

    def setUp(self):
        super().setUp()

        self.student = self.create_student()

    def test_student_enrollment_can_be_created(self):
        enrollment = self.create_enrollment(
            student=self.student,
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.session, self.session)
        self.assertEqual(enrollment.school_class, self.school_class)
        self.assertEqual(
            enrollment.status,
            StudentEnrollment.Status.ACTIVE,
        )

    def test_enrollment_has_uuid_primary_key(self):
        enrollment = self.create_enrollment(
            student=self.student,
        )

        self.assertIsNotNone(enrollment.id)

    def test_student_can_have_enrollments_in_different_sessions(self):
        first = self.create_enrollment(
            student=self.student,
        )

        next_session = AcademicSession.objects.create(
            school=self.school,
            name="2027/2028",
            start_date=date(2027, 9, 1),
            end_date=date(2028, 7, 31),
        )

        second = self.create_enrollment(
            student=self.student,
            session=next_session,
            enrollment_date=date(2027, 9, 5),
        )

        self.assertNotEqual(first.session, second.session)

    def test_only_one_active_enrollment_per_student_per_session(self):
        self.create_enrollment(
            student=self.student,
        )

        with self.assertRaises(ValidationError):
            self.create_enrollment(
                student=self.student,
            )

    def test_historical_enrollment_can_be_kept_after_transfer(self):
        first_enrollment = self.create_enrollment(
            student=self.student,
            school_class=self.school_class,
        )

        first_enrollment.status = StudentEnrollment.Status.TRANSFERRED
        first_enrollment.save()

        second_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="B",
        )

        second_enrollment = self.create_enrollment(
            student=self.student,
            school_class=second_class,
        )

        self.assertEqual(
            self.student.enrollments.count(),
            2,
        )

        self.assertEqual(
            first_enrollment.status,
            StudentEnrollment.Status.TRANSFERRED,
        )

        self.assertEqual(
            second_enrollment.status,
            StudentEnrollment.Status.ACTIVE,
        )

    def test_multiple_historical_enrollments_in_same_session_are_allowed(self):
        first = self.create_enrollment(
            student=self.student,
            status=StudentEnrollment.Status.TRANSFERRED,
        )

        second_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="B",
        )

        second = self.create_enrollment(
            student=self.student,
            school_class=second_class,
            status=StudentEnrollment.Status.COMPLETED,
        )

        self.assertEqual(first.session, second.session)
        self.assertEqual(
            self.student.enrollments.count(),
            2,
        )

    def test_student_cannot_be_enrolled_in_another_schools_session(self):
        with self.assertRaises(ValidationError):
            self.create_enrollment(
                student=self.student,
                session=self.other_session,
            )

    def test_student_cannot_be_enrolled_in_another_schools_class(self):
        with self.assertRaises(ValidationError):
            self.create_enrollment(
                student=self.student,
                school_class=self.other_school_class,
            )

    def test_enrollment_school_must_match_student_school(self):
        with self.assertRaises(ValidationError):
            self.create_enrollment(
                student=self.student,
                school=self.other_school,
            )

    def test_enrollment_date_must_be_within_session(self):
        with self.assertRaises(ValidationError):
            self.create_enrollment(
                student=self.student,
                enrollment_date=date(2026, 8, 31),
            )

    def test_enrollment_date_cannot_be_after_session(self):
        with self.assertRaises(ValidationError):
            self.create_enrollment(
                student=self.student,
                enrollment_date=date(2027, 8, 1),
            )

    def test_enrollment_status_choices_are_available(self):
        expected = {
            "active",
            "completed",
            "promoted",
            "transferred",
            "withdrawn",
        }

        actual = {
            value
            for value, label in StudentEnrollment.Status.choices
        }

        self.assertEqual(actual, expected)

    def test_enrollment_string_representation(self):
        enrollment = self.create_enrollment(
            student=self.student,
        )

        self.assertIn("John Doe", str(enrollment))
        self.assertIn("JSS 1 A", str(enrollment))
        self.assertIn("2026/2027", str(enrollment))
