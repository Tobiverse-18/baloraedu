
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.schools.models import School, SchoolMembership
from apps.academics.models import (
    AcademicSession,
    ClassLevel,
    SchoolClass,
    Subject,
)

from .models import (
    StaffDepartment,
    StaffProfile,
    ClassTeacherAssignment,
    SubjectTeacherAssignment,
)


User = get_user_model()


class StaffModelTestBase(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Staff Test School",
        )

        self.other_school = School.objects.create(
            name="Another Staff School",
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

        self.department = StaffDepartment.objects.create(
            school=self.school,
            name="Sciences",
        )

        self.other_department = StaffDepartment.objects.create(
            school=self.other_school,
            name="Sciences",
        )

        self.subject = Subject.objects.create(
            school=self.school,
            name="Mathematics",
            code="MTH",
        )

        self.other_subject = Subject.objects.create(
            school=self.other_school,
            name="Mathematics",
            code="MTH",
        )

    def create_user(self, email="teacher@example.com"):
        return User.objects.create_user(
            email=email,
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
        )

    def create_membership(
        self,
        user,
        role=SchoolMembership.Role.TEACHER,
        school=None,
    ):
        return SchoolMembership.objects.create(
            school=school or self.school,
            user=user,
            role=role,
        )

    def create_staff(self, **kwargs):
        defaults = {
            "school": self.school,
            "staff_number": "STF-001",
            "first_name": "John",
            "last_name": "Doe",
            "job_title": "Mathematics Teacher",
            "staff_type": StaffProfile.StaffType.TEACHING,
            "department": self.department,
        }

        defaults.update(kwargs)

        return StaffProfile.objects.create(**defaults)

    def create_class_teacher_assignment(self, **kwargs):
        defaults = {
            "school": self.school,
            "school_class": self.school_class,
            "session": self.session,
        }

        defaults.update(kwargs)

        if "staff" not in defaults:
            defaults["staff"] = self.create_staff()

        return ClassTeacherAssignment.objects.create(**defaults)

    def create_subject_assignment(self, **kwargs):
        defaults = {
            "school": self.school,
            "subject": self.subject,
            "school_class": self.school_class,
            "session": self.session,
        }

        defaults.update(kwargs)

        if "staff" not in defaults:
            defaults["staff"] = self.create_staff()

        return SubjectTeacherAssignment.objects.create(**defaults)


class StaffDepartmentTests(StaffModelTestBase):

    def test_department_can_be_created(self):
        self.assertEqual(self.department.school, self.school)
        self.assertEqual(self.department.name, "Sciences")

    def test_department_has_uuid_primary_key(self):
        self.assertIsNotNone(self.department.id)

    def test_same_department_name_can_exist_in_different_schools(self):
        self.assertEqual(
            StaffDepartment.objects.filter(name="Sciences").count(),
            2,
        )

    def test_duplicate_department_name_in_same_school_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StaffDepartment.objects.create(
                    school=self.school,
                    name="Sciences",
                )

    def test_department_can_be_deactivated(self):
        self.department.is_active = False
        self.department.save()

        self.department.refresh_from_db()

        self.assertFalse(self.department.is_active)


class StaffProfileTests(StaffModelTestBase):

    def test_staff_profile_can_be_created(self):
        staff = self.create_staff()

        self.assertEqual(staff.school, self.school)
        self.assertEqual(staff.staff_number, "STF-001")
        self.assertEqual(staff.staff_type, StaffProfile.StaffType.TEACHING)

    def test_staff_profile_has_uuid_primary_key(self):
        staff = self.create_staff()

        self.assertIsNotNone(staff.id)

    def test_full_name_includes_middle_name_when_available(self):
        staff = self.create_staff(
            middle_name="Michael",
        )

        self.assertEqual(staff.full_name, "John Michael Doe")

    def test_full_name_works_without_middle_name(self):
        staff = self.create_staff()

        self.assertEqual(staff.full_name, "John Doe")

    def test_duplicate_staff_number_in_same_school_is_rejected(self):
        self.create_staff()

        with self.assertRaises(ValidationError):
            self.create_staff(
                staff_number="STF-001",
            )

    def test_same_staff_number_can_exist_in_different_schools(self):
        self.create_staff()

        other_staff = self.create_staff(
            school=self.other_school,
            staff_number="STF-001",
            department=self.other_department,
        )

        self.assertEqual(other_staff.school, self.other_school)

    def test_department_from_another_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_staff(
                department=self.other_department,
            )

    def test_new_staff_cannot_be_assigned_to_inactive_department(self):
        self.department.is_active = False
        self.department.save()

        with self.assertRaises(ValidationError):
            self.create_staff(
                staff_number="STF-002",
            )

    def test_existing_staff_can_keep_inactive_department(self):
        staff = self.create_staff()

        self.department.is_active = False
        self.department.save()

        staff.job_title = "Senior Mathematics Teacher"
        staff.save()

        self.assertEqual(staff.department, self.department)

    def test_termination_date_cannot_precede_employment_date(self):
        with self.assertRaises(ValidationError):
            self.create_staff(
                employment_date=date(2026, 9, 1),
                termination_date=date(2026, 8, 31),
            )

    def test_non_teaching_staff_can_be_created(self):
        staff = self.create_staff(
            staff_number="STF-002",
            staff_type=StaffProfile.StaffType.NON_TEACHING,
            job_title="Accountant",
        )

        self.assertEqual(
            staff.staff_type,
            StaffProfile.StaffType.NON_TEACHING,
        )

    def test_staff_profile_does_not_require_a_user_account(self):
        staff = self.create_staff()

        self.assertIsNone(staff.user)

    def test_teaching_staff_can_link_to_teacher_membership(self):
        user = self.create_user()
        self.create_membership(
            user,
            SchoolMembership.Role.TEACHER,
        )

        staff = self.create_staff(
            user=user,
        )

        self.assertEqual(staff.user, user)

    def test_teaching_staff_can_link_to_principal_membership(self):
        user = self.create_user("principal@example.com")
        self.create_membership(
            user,
            SchoolMembership.Role.PRINCIPAL,
        )

        staff = self.create_staff(
            user=user,
        )

        self.assertEqual(staff.user, user)

    def test_non_teaching_staff_can_link_to_staff_membership(self):
        user = self.create_user("staff@example.com")
        self.create_membership(
            user,
            SchoolMembership.Role.STAFF,
        )

        staff = self.create_staff(
            staff_number="STF-002",
            staff_type=StaffProfile.StaffType.NON_TEACHING,
            job_title="Administrative Officer",
            user=user,
        )

        self.assertEqual(staff.user, user)

    def test_teaching_staff_cannot_link_to_accountant_membership(self):
        user = self.create_user("accountant@example.com")
        self.create_membership(
            user,
            SchoolMembership.Role.ACCOUNTANT,
        )

        with self.assertRaises(ValidationError):
            self.create_staff(
                user=user,
            )

    def test_non_teaching_staff_cannot_link_to_teacher_membership(self):
        user = self.create_user("teacher2@example.com")
        self.create_membership(
            user,
            SchoolMembership.Role.TEACHER,
        )

        with self.assertRaises(ValidationError):
            self.create_staff(
                staff_number="STF-002",
                staff_type=StaffProfile.StaffType.NON_TEACHING,
                job_title="Administrative Officer",
                user=user,
            )

    def test_user_without_school_membership_cannot_be_linked(self):
        user = self.create_user("nomembership@example.com")

        with self.assertRaises(ValidationError):
            self.create_staff(
                user=user,
            )

    def test_user_from_another_school_cannot_be_linked(self):
        user = self.create_user("otherteacher@example.com")

        self.create_membership(
            user,
            SchoolMembership.Role.TEACHER,
            school=self.other_school,
        )

        with self.assertRaises(ValidationError):
            self.create_staff(
                user=user,
            )

    def test_same_user_cannot_be_linked_to_two_staff_profiles_in_school(self):
        user = self.create_user()
        self.create_membership(
            user,
            SchoolMembership.Role.TEACHER,
        )

        self.create_staff(user=user)

        with self.assertRaises(ValidationError):
            self.create_staff(
                staff_number="STF-002",
                user=user,
            )


class ClassTeacherAssignmentTests(StaffModelTestBase):

    def setUp(self):
        super().setUp()

        self.teacher = self.create_staff()

    def test_class_teacher_assignment_can_be_created(self):
        assignment = self.create_class_teacher_assignment(
            staff=self.teacher,
        )

        self.assertEqual(assignment.staff, self.teacher)
        self.assertEqual(assignment.school_class, self.school_class)
        self.assertEqual(assignment.session, self.session)

    def test_non_teaching_staff_cannot_be_class_teacher(self):
        staff = self.create_staff(
            staff_number="STF-002",
            staff_type=StaffProfile.StaffType.NON_TEACHING,
            job_title="Accountant",
        )

        with self.assertRaises(ValidationError):
            self.create_class_teacher_assignment(
                staff=staff,
            )

    def test_staff_from_another_school_cannot_be_class_teacher(self):
        staff = self.create_staff(
            school=self.other_school,
            staff_number="STF-002",
            department=self.other_department,
        )

        with self.assertRaises(ValidationError):
            self.create_class_teacher_assignment(
                staff=staff,
            )

    def test_class_from_another_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_class_teacher_assignment(
                staff=self.teacher,
                school_class=self.other_school_class,
            )

    def test_session_from_another_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_class_teacher_assignment(
                staff=self.teacher,
                session=self.other_session,
            )

    def test_only_one_class_teacher_is_allowed_per_class_per_session(self):
        self.create_class_teacher_assignment(
            staff=self.teacher,
        )

        another_teacher = self.create_staff(
            staff_number="STF-002",
        )

        with self.assertRaises(ValidationError):
            self.create_class_teacher_assignment(
                staff=another_teacher,
            )

    def test_different_classes_can_have_different_class_teachers(self):
        self.create_class_teacher_assignment(
            staff=self.teacher,
        )

        second_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="B",
        )

        another_teacher = self.create_staff(
            staff_number="STF-002",
        )

        assignment = self.create_class_teacher_assignment(
            staff=another_teacher,
            school_class=second_class,
        )

        self.assertEqual(assignment.school_class, second_class)

    def test_non_active_teacher_cannot_receive_new_assignment(self):
        self.teacher.status = StaffProfile.Status.ON_LEAVE
        self.teacher.save()

        with self.assertRaises(ValidationError):
            self.create_class_teacher_assignment(
                staff=self.teacher,
            )

    def test_existing_assignment_remains_when_teacher_goes_on_leave(self):
        assignment = self.create_class_teacher_assignment(
            staff=self.teacher,
        )

        self.teacher.status = StaffProfile.Status.ON_LEAVE
        self.teacher.save()

        self.assertTrue(
            ClassTeacherAssignment.objects.filter(
                pk=assignment.pk,
            ).exists()
        )

    def test_existing_assignment_can_be_updated_when_teacher_goes_on_leave(self):
        assignment = self.create_class_teacher_assignment(
            staff=self.teacher,
        )

        self.teacher.status = StaffProfile.Status.ON_LEAVE
        self.teacher.save()

        second_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="B",
        )

        assignment.school_class = second_class
        assignment.save()

        assignment.refresh_from_db()

        self.assertEqual(assignment.school_class, second_class)

    def test_existing_assignment_cannot_be_reassigned_to_inactive_teacher(self):
        assignment = self.create_class_teacher_assignment(
            staff=self.teacher,
        )

        another_teacher = self.create_staff(
            staff_number="STF-002",
        )

        another_teacher.status = StaffProfile.Status.SUSPENDED
        another_teacher.save()

        assignment.staff = another_teacher

        with self.assertRaises(ValidationError):
            assignment.save()


class SubjectTeacherAssignmentTests(StaffModelTestBase):

    def setUp(self):
        super().setUp()

        self.teacher = self.create_staff()

    def test_subject_teacher_assignment_can_be_created(self):
        assignment = self.create_subject_assignment(
            staff=self.teacher,
        )

        self.assertEqual(assignment.staff, self.teacher)
        self.assertEqual(assignment.subject, self.subject)
        self.assertEqual(assignment.school_class, self.school_class)

    def test_multiple_teachers_can_teach_same_subject_in_same_class(self):
        first_teacher = self.teacher

        second_teacher = self.create_staff(
            staff_number="STF-002",
            first_name="Jane",
            last_name="Smith",
        )

        first_assignment = self.create_subject_assignment(
            staff=first_teacher,
        )

        second_assignment = self.create_subject_assignment(
            staff=second_teacher,
        )

        self.assertEqual(
            first_assignment.subject,
            second_assignment.subject,
        )

        self.assertEqual(
            first_assignment.school_class,
            second_assignment.school_class,
        )

        self.assertNotEqual(
            first_assignment.staff,
            second_assignment.staff,
        )

    def test_same_teacher_cannot_receive_duplicate_assignment(self):
        self.create_subject_assignment(
            staff=self.teacher,
        )

        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
            )

    def test_non_teaching_staff_cannot_receive_subject_assignment(self):
        staff = self.create_staff(
            staff_number="STF-002",
            staff_type=StaffProfile.StaffType.NON_TEACHING,
            job_title="Accountant",
        )

        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=staff,
            )

    def test_staff_from_another_school_cannot_teach_subject(self):
        staff = self.create_staff(
            school=self.other_school,
            staff_number="STF-002",
            department=self.other_department,
        )

        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=staff,
            )

    def test_subject_from_another_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
                subject=self.other_subject,
            )

    def test_class_from_another_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
                school_class=self.other_school_class,
            )

    def test_session_from_another_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
                session=self.other_session,
            )

    def test_inactive_subject_cannot_receive_new_assignment(self):
        self.subject.is_active = False
        self.subject.save()

        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
            )

    def test_inactive_class_cannot_receive_new_assignment(self):
        self.school_class.is_active = False
        self.school_class.save()

        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
            )

    def test_non_active_teacher_cannot_receive_new_assignment(self):
        self.teacher.status = StaffProfile.Status.SUSPENDED
        self.teacher.save()

        with self.assertRaises(ValidationError):
            self.create_subject_assignment(
                staff=self.teacher,
            )

    def test_existing_assignment_remains_when_teacher_is_terminated(self):
        assignment = self.create_subject_assignment(
            staff=self.teacher,
        )

        self.teacher.status = StaffProfile.Status.TERMINATED
        self.teacher.save()

        self.assertTrue(
            SubjectTeacherAssignment.objects.filter(
                pk=assignment.pk,
            ).exists()
        )

    def test_existing_assignment_can_be_updated_when_teacher_is_terminated(self):
        assignment = self.create_subject_assignment(
            staff=self.teacher,
        )

        self.teacher.status = StaffProfile.Status.TERMINATED
        self.teacher.save()

        second_subject = Subject.objects.create(
            school=self.school,
            name="Computer Studies",
            code="CST",
        )

        assignment.subject = second_subject
        assignment.save()

        assignment.refresh_from_db()

        self.assertEqual(assignment.subject, second_subject)

    def test_existing_assignment_cannot_be_reassigned_to_inactive_teacher(self):
        assignment = self.create_subject_assignment(
            staff=self.teacher,
        )

        another_teacher = self.create_staff(
            staff_number="STF-002",
        )

        another_teacher.status = StaffProfile.Status.ON_LEAVE
        another_teacher.save()

        assignment.staff = another_teacher

        with self.assertRaises(ValidationError):
            assignment.save()
