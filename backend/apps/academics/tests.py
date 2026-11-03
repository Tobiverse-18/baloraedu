
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from django.db import IntegrityError, transaction

from apps.schools.models import School
from .models import (
    AcademicSession,
    AcademicTerm,
    ClassLevel,
    SchoolClass,
)


class AcademicModelTestBase(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Academic Test School",
        )

        self.other_school = School.objects.create(
            name="Another Academic School",
        )

        self.session = AcademicSession.objects.create(
            school=self.school,
            name="2026/2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
            is_current=True,
        )

        self.other_session = AcademicSession.objects.create(
            school=self.other_school,
            name="2026/2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
            is_current=True,
        )


class AcademicSessionTests(AcademicModelTestBase):

    def test_session_can_be_created(self):
        self.assertEqual(self.session.school, self.school)
        self.assertEqual(self.session.name, "2026/2027")

    def test_session_has_uuid_primary_key(self):
        self.assertIsNotNone(self.session.id)

    def test_same_session_name_can_exist_in_different_schools(self):
        self.assertEqual(
            AcademicSession.objects.filter(
                name="2026/2027"
            ).count(),
            2,
        )

    def test_duplicate_session_name_in_same_school_is_rejected(self):
        with self.assertRaises(ValidationError):
            AcademicSession.objects.create(
                school=self.school,
                name="2026/2027",
                start_date=date(2026, 9, 1),
                end_date=date(2027, 7, 31),
            )

    def test_end_date_must_be_after_start_date(self):
        with self.assertRaises(ValidationError):
            AcademicSession.objects.create(
                school=self.school,
                name="Invalid Session",
                start_date=date(2027, 7, 31),
                end_date=date(2027, 7, 30),
            )

    def test_only_one_current_session_per_school(self):
        with self.assertRaises(ValidationError):
                AcademicSession.objects.create(
                    school=self.school,
                    name="2027/2028",
                    start_date=date(2027, 9, 1),
                    end_date=date(2028, 7, 31),
                    is_current=True,
                )

    def test_different_schools_can_have_different_current_sessions(self):
        self.assertTrue(self.session.is_current)
        self.assertTrue(self.other_session.is_current)


class AcademicTermTests(AcademicModelTestBase):

    def test_term_can_be_created(self):
        term = AcademicTerm.objects.create(
            session=self.session,
            name="First Term",
            term_number=1,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
            is_current=True,
        )

        self.assertEqual(term.session, self.session)
        self.assertTrue(term.is_current)

    def test_duplicate_term_name_in_session_is_rejected(self):
        AcademicTerm.objects.create(
            session=self.session,
            name="First Term",
            term_number=1,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )

        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                session=self.session,
                name="First Term",
                term_number=2,
                start_date=date(2027, 1, 5),
                end_date=date(2027, 4, 10),
            )

    def test_duplicate_term_number_in_session_is_rejected(self):
        AcademicTerm.objects.create(
            session=self.session,
            name="First Term",
            term_number=1,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )

        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                session=self.session,
                name="Second Term",
                term_number=1,
                start_date=date(2027, 1, 5),
                end_date=date(2027, 4, 10),
            )

    def test_same_term_can_exist_in_different_sessions(self):
        term_one = AcademicTerm.objects.create(
            session=self.session,
            name="First Term",
            term_number=1,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )

        term_two = AcademicTerm.objects.create(
            session=self.other_session,
            name="First Term",
            term_number=1,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )

        self.assertNotEqual(term_one.id, term_two.id)

    def test_term_dates_must_fall_within_session(self):
        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                session=self.session,
                name="Invalid Term",
                term_number=1,
                start_date=date(2026, 8, 1),
                end_date=date(2026, 12, 15),
            )

    def test_term_end_date_must_be_after_start_date(self):
        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                session=self.session,
                name="Invalid Term",
                term_number=1,
                start_date=date(2026, 12, 15),
                end_date=date(2026, 12, 1),
            )

    def test_term_number_must_be_at_least_one(self):
        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                session=self.session,
                name="Invalid Term",
                term_number=0,
                start_date=date(2026, 9, 1),
                end_date=date(2026, 12, 15),
            )

    def test_only_one_current_term_per_session(self):
        AcademicTerm.objects.create(
            session=self.session,
            name="First Term",
            term_number=1,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
            is_current=True,
        )

        with self.assertRaises(ValidationError):
                AcademicTerm.objects.create(
                    session=self.session,
                    name="Second Term",
                    term_number=2,
                    start_date=date(2027, 1, 5),
                    end_date=date(2027, 4, 10),
                    is_current=True,
                )

    def test_term_cannot_be_current_if_session_is_not_current(self):
        non_current_session = AcademicSession.objects.create(
            school=self.school,
            name="2027/2028",
            start_date=date(2027, 9, 1),
            end_date=date(2028, 7, 31),
            is_current=False,
        )

        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                session=non_current_session,
                name="First Term",
                term_number=1,
                start_date=date(2027, 9, 1),
                end_date=date(2027, 12, 15),
                is_current=True,
            )


class ClassLevelTests(AcademicModelTestBase):

    def test_class_level_can_be_created(self):
        level = ClassLevel.objects.create(
            school=self.school,
            name="Creche",
            category=ClassLevel.Category.CRECHE,
        )

        self.assertEqual(level.name, "Creche")
        self.assertEqual(
            level.category,
            ClassLevel.Category.CRECHE,
        )

    def test_all_educational_categories_are_available(self):
        expected_categories = {
            "creche",
            "nursery",
            "primary",
            "junior_secondary",
            "senior_secondary",
            "other",
        }

        actual_categories = {
            value for value, label in ClassLevel.Category.choices
        }

        self.assertEqual(actual_categories, expected_categories)

    def test_custom_class_level_can_be_created(self):
        level = ClassLevel.objects.create(
            school=self.school,
            name="Grade 10",
            category=ClassLevel.Category.OTHER,
        )

        self.assertEqual(level.name, "Grade 10")

    def test_duplicate_class_level_in_same_school_is_rejected(self):
        ClassLevel.objects.create(
            school=self.school,
            name="Primary 1",
            category=ClassLevel.Category.PRIMARY,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClassLevel.objects.create(
                    school=self.school,
                    name="Primary 1",
                    category=ClassLevel.Category.PRIMARY,
                )

    def test_same_class_level_can_exist_in_different_schools(self):
        first_level = ClassLevel.objects.create(
            school=self.school,
            name="Primary 1",
            category=ClassLevel.Category.PRIMARY,
        )

        second_level = ClassLevel.objects.create(
            school=self.other_school,
            name="Primary 1",
            category=ClassLevel.Category.PRIMARY,
        )

        self.assertNotEqual(first_level.id, second_level.id)


class SchoolClassTests(AcademicModelTestBase):

    def setUp(self):
        super().setUp()

        self.class_level = ClassLevel.objects.create(
            school=self.school,
            name="JSS 1",
            category=ClassLevel.Category.JUNIOR_SECONDARY,
        )

        self.other_class_level = ClassLevel.objects.create(
            school=self.other_school,
            name="JSS 1",
            category=ClassLevel.Category.JUNIOR_SECONDARY,
        )

    def test_school_class_can_be_created(self):
        school_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="A",
            capacity=40,
        )

        self.assertEqual(school_class.full_name, "JSS 1 A")
        self.assertEqual(school_class.capacity, 40)

    def test_class_without_section_uses_level_name(self):
        school_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
        )

        self.assertEqual(school_class.full_name, "JSS 1")

    def test_duplicate_section_in_same_level_is_rejected(self):
        SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="A",
        )

        with self.assertRaises(ValidationError):
            SchoolClass.objects.create(
                school=self.school,
                class_level=self.class_level,
                section_name="A",
            )

    def test_different_sections_can_exist_in_same_level(self):
        first = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="A",
        )

        second = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="B",
        )

        self.assertNotEqual(first.id, second.id)

    def test_different_schools_can_use_same_section_names(self):
        first = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
            section_name="A",
        )

        second = SchoolClass.objects.create(
            school=self.other_school,
            class_level=self.other_class_level,
            section_name="A",
        )

        self.assertNotEqual(first.id, second.id)

    def test_class_cannot_use_another_schools_class_level(self):
        with self.assertRaises(ValidationError):
            SchoolClass.objects.create(
                school=self.school,
                class_level=self.other_class_level,
                section_name="A",
            )

    def test_class_capacity_can_be_blank(self):
        school_class = SchoolClass.objects.create(
            school=self.school,
            class_level=self.class_level,
        )

        self.assertIsNone(school_class.capacity)

    def test_class_capacity_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            SchoolClass.objects.create(
                school=self.school,
                class_level=self.class_level,
                capacity=-1,
            )
