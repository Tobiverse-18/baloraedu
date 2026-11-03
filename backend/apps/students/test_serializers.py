from datetime import date

from django.test import TestCase

from apps.schools.models import School
from apps.academics.models import (
    AcademicSession,
    ClassLevel,
    SchoolClass,
)

from apps.students.models import (
    Student,
    Guardian,
    StudentGuardian,
    StudentEnrollment,
)

from apps.students.serializers import (
    StudentSerializer,
    GuardianSerializer,
    StudentGuardianSerializer,
    StudentEnrollmentSerializer,
)


class StudentSerializerTestBase(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Serializer Test School",
        )

        self.other_school = School.objects.create(
            name="Other Serializer School",
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

        self.student = Student.objects.create(
            school=self.school,
            admission_number="BAL-001",
            first_name="John",
            last_name="Doe",
        )

        self.other_student = Student.objects.create(
            school=self.other_school,
            admission_number="BAL-001",
            first_name="Peter",
            last_name="Smith",
        )

        self.guardian = Guardian.objects.create(
            school=self.school,
            first_name="Jane",
            last_name="Doe",
            phone_number="08012345678",
        )

        self.other_guardian = Guardian.objects.create(
            school=self.other_school,
            first_name="Mary",
            last_name="Smith",
            phone_number="08098765432",
        )

    def student_guardian_data(self, **overrides):
        data = {
            "student": str(self.student.id),
            "guardian": str(self.guardian.id),
            "relationship": StudentGuardian.Relationship.MOTHER,
        }

        data.update(overrides)
        return data

    def enrollment_data(self, **overrides):
        data = {
            "student": str(self.student.id),
            "session": str(self.session.id),
            "school_class": str(self.school_class.id),
            "enrollment_date": "2026-09-10",
        }

        data.update(overrides)
        return data


class StudentSerializerTests(StudentSerializerTestBase):

    def test_valid_student_data_is_accepted(self):
        serializer = StudentSerializer(
            data={
                "admission_number": "BAL-002",
                "first_name": "Michael",
                "last_name": "James",
            },
            context={"school": self.school},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_duplicate_admission_number_is_rejected(self):
        serializer = StudentSerializer(
            data={
                "admission_number": "BAL-001",
                "first_name": "Another",
                "last_name": "Student",
            },
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("admission_number", serializer.errors)

    def test_admission_number_is_trimmed(self):
        serializer = StudentSerializer(
            data={
                "admission_number": "  BAL-002  ",
                "first_name": "Michael",
                "last_name": "James",
            },
            context={"school": self.school},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["admission_number"],
            "BAL-002",
        )

    def test_same_admission_number_is_allowed_in_another_school(self):
        serializer = StudentSerializer(
            data={
                "admission_number": "BAL-002",
                "first_name": "Another",
                "last_name": "Student",
            },
            context={"school": self.other_school},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_admission_date_before_birth_date_is_rejected(self):
        serializer = StudentSerializer(
            data={
                "admission_number": "BAL-003",
                "first_name": "Michael",
                "last_name": "James",
                "date_of_birth": "2010-05-10",
                "admission_date": "2009-09-01",
            },
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("admission_date", serializer.errors)

    def test_school_and_user_are_not_writable_serializer_fields(self):
        serializer = StudentSerializer()

        self.assertTrue(serializer.fields["school"].read_only)
        self.assertNotIn("user", serializer.fields)


class GuardianSerializerTests(StudentSerializerTestBase):

    def test_valid_guardian_data_is_accepted(self):
        serializer = GuardianSerializer(
            data={
                "first_name": "Peter",
                "last_name": "James",
                "phone_number": "08011112222",
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_guardian_name_fields_are_trimmed(self):
        serializer = GuardianSerializer(
            data={
                "first_name": "  Peter  ",
                "last_name": "  James  ",
                "phone_number": "08011112222",
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["first_name"], "Peter")
        self.assertEqual(serializer.validated_data["last_name"], "James")

    def test_guardian_user_is_not_exposed(self):
        serializer = GuardianSerializer()

        self.assertNotIn("user", serializer.fields)


class StudentGuardianSerializerTests(StudentSerializerTestBase):

    def test_valid_guardian_link_is_accepted(self):
        serializer = StudentGuardianSerializer(
            data=self.student_guardian_data(),
            context={"school": self.school},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_guardian_from_another_school_is_rejected(self):
        serializer = StudentGuardianSerializer(
            data=self.student_guardian_data(
                guardian=str(self.other_guardian.id),
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("guardian", serializer.errors)

    def test_student_from_another_school_is_rejected(self):
        serializer = StudentGuardianSerializer(
            data=self.student_guardian_data(
                student=str(self.other_student.id),
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("student", serializer.errors)

    def test_missing_school_context_fails_closed(self):
        serializer = StudentGuardianSerializer(
            data=self.student_guardian_data(),
        )

        self.assertFalse(serializer.is_valid())

    def test_duplicate_guardian_link_is_rejected(self):
        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
        )

        serializer = StudentGuardianSerializer(
            data=self.student_guardian_data(),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("guardian", serializer.errors)

    def test_second_primary_guardian_is_rejected(self):
        second_guardian = Guardian.objects.create(
            school=self.school,
            first_name="Peter",
            last_name="Doe",
            phone_number="08022223333",
        )

        StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
            is_primary=True,
        )

        serializer = StudentGuardianSerializer(
            data=self.student_guardian_data(
                guardian=str(second_guardian.id),
                is_primary=True,
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("is_primary", serializer.errors)


class StudentEnrollmentSerializerTests(StudentSerializerTestBase):

    def test_valid_enrollment_data_is_accepted(self):
        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(),
            context={"school": self.school},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_student_from_another_school_is_rejected(self):
        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(
                student=str(self.other_student.id),
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("student", serializer.errors)

    def test_session_from_another_school_is_rejected(self):
        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(
                session=str(self.other_session.id),
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("session", serializer.errors)

    def test_class_from_another_school_is_rejected(self):
        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(
                school_class=str(self.other_school_class.id),
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("school_class", serializer.errors)

    def test_missing_school_context_fails_closed(self):
        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(),
        )

        self.assertFalse(serializer.is_valid())

    def test_enrollment_outside_session_dates_is_rejected(self):
        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(
                enrollment_date="2026-08-31",
            ),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("enrollment_date", serializer.errors)

    def test_duplicate_active_enrollment_is_rejected(self):
        StudentEnrollment.objects.create(
            school=self.school,
            student=self.student,
            session=self.session,
            school_class=self.school_class,
            enrollment_date=date(2026, 9, 10),
        )

        serializer = StudentEnrollmentSerializer(
            data=self.enrollment_data(),
            context={"school": self.school},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("student", serializer.errors)