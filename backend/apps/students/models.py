
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.schools.models import School
from apps.academics.models import AcademicSession, SchoolClass


class Student(models.Model):
    """
    A student's permanent profile within a school.

    Student records do not require login accounts.
    """

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        GRADUATED = "graduated", "Graduated"
        TRANSFERRED = "transferred", "Transferred"
        WITHDRAWN = "withdrawn", "Withdrawn"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="students",
    )

    admission_number = models.CharField(
        max_length=50,
    )

    first_name = models.CharField(max_length=100)

    middle_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        default="",
    )

    email = models.EmailField(
        blank=True,
        default="",
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    address = models.TextField(
        blank=True,
        default="",
    )

    passport = models.ImageField(
        upload_to="students/passports/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
        help_text="Optional student portal account.",
    )

    admission_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["last_name", "first_name"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "admission_number"],
                name="unique_school_admission_number",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "status"],
                name="student_school_status_idx",
            ),
            models.Index(
                fields=["school", "last_name", "first_name"],
                name="student_school_name_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if self.date_of_birth and self.admission_date:
            if self.admission_date < self.date_of_birth:
                raise ValidationError({
                    "admission_date": (
                        "Admission date cannot be before date of birth."
                    )
                })

        if self.user_id and self.school_id:
            from apps.schools.models import SchoolMembership

            membership = SchoolMembership.objects.filter(
                school=self.school,
                user=self.user,
                role=SchoolMembership.Role.STUDENT,
            ).first()

            if membership is None:
                raise ValidationError({
                    "user": (
                        "The linked account must have a student "
                        "membership in this school."
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return " ".join(
            part for part in [
                self.first_name,
                self.middle_name,
                self.last_name,
            ]
            if part
        )

    def __str__(self):
        return f"{self.full_name} ({self.admission_number})"


class Guardian(models.Model):
    """
    A parent or guardian belonging to a school.

    A guardian can be linked to multiple students.
    """

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="guardians",
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        default="",
    )

    email = models.EmailField(
        blank=True,
        default="",
    )

    phone_number = models.CharField(max_length=20)

    alternative_phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    occupation = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    address = models.TextField(
        blank=True,
        default="",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guardian_profiles",
        help_text="Optional parent portal account.",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Guardian"
        verbose_name_plural = "Guardians"
        ordering = ["last_name", "first_name"]

        indexes = [
            models.Index(
                fields=["school", "phone_number"],
                name="guardian_school_phone_idx",
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StudentGuardian(models.Model):
    """
    Connects students to their parents or guardians.

    Supports multiple guardians per student and
    multiple students per guardian.
    """

    class Relationship(models.TextChoices):
        FATHER = "father", "Father"
        MOTHER = "mother", "Mother"
        GUARDIAN = "guardian", "Guardian"
        STEPFATHER = "stepfather", "Stepfather"
        STEPMOTHER = "stepmother", "Stepmother"
        GRANDPARENT = "grandparent", "Grandparent"
        UNCLE = "uncle", "Uncle"
        AUNT = "aunt", "Aunt"
        OTHER = "other", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="guardian_links",
    )

    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="student_links",
    )

    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices,
        default=Relationship.GUARDIAN,
    )

    is_primary = models.BooleanField(default=False)

    is_emergency_contact = models.BooleanField(default=False)

    can_pickup_student = models.BooleanField(default=True)

    receives_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Guardian"
        verbose_name_plural = "Student Guardians"

        constraints = [
            models.UniqueConstraint(
                fields=["student", "guardian"],
                name="unique_student_guardian",
            ),
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(is_primary=True),
                name="unique_primary_guardian_per_student",
            ),
        ]

        indexes = [
            models.Index(
                fields=["student", "is_primary"],
                name="student_guardian_primary_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.student_id
            and self.guardian_id
            and self.student.school_id != self.guardian.school_id
        ):
            raise ValidationError({
                "guardian": (
                    "The guardian and student must belong "
                    "to the same school."
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.guardian} - {self.student}"
        )


class StudentEnrollment(models.Model):
    """
    Records a student's placement in a class
    for a particular academic session.

    Historical enrollments are retained.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        PROMOTED = "promoted", "Promoted"
        TRANSFERRED = "transferred", "Transferred"
        WITHDRAWN = "withdrawn", "Withdrawn"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="student_enrollments",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
    )

    enrollment_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    remarks = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Enrollment"
        verbose_name_plural = "Student Enrollments"
        ordering = ["-session__start_date", "student__last_name"]

        constraints = [
            models.UniqueConstraint(
                fields=["student", "session"],
                condition=Q(status="active"),
                name="unique_active_student_session",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "session", "status"],
                name="enrollment_school_session_idx",
            ),
            models.Index(
                fields=["school_class", "status"],
                name="enrollment_class_status_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.student_id and self.school_id:
            if self.student.school_id != self.school_id:
                errors["student"] = (
                    "The student does not belong to this school."
                )

        if self.session_id and self.school_id:
            if self.session.school_id != self.school_id:
                errors["session"] = (
                    "The academic session does not belong "
                    "to this school."
                )

        if self.school_class_id and self.school_id:
            if self.school_class.school_id != self.school_id:
                errors["school_class"] = (
                    "The class does not belong to this school."
                )

        if self.session_id and self.enrollment_date:
            if (
                self.enrollment_date < self.session.start_date
                or self.enrollment_date > self.session.end_date
            ):
                errors["enrollment_date"] = (
                    "The enrollment date must fall within "
                    "the academic session."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.school_class} - "
            f"{self.session.name}"
        )
