
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.schools.models import School


class AcademicSession(models.Model):
    """
    Represents an academic year belonging to one school.
    Example: 2026/2027.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="academic_sessions",
    )

    name = models.CharField(max_length=50)

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Academic Session"
        verbose_name_plural = "Academic Sessions"
        ordering = ["-start_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_school_academic_session",
            ),
            models.UniqueConstraint(
                fields=["school"],
                condition=Q(is_current=True),
                name="unique_current_session_per_school",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "is_current"],
                name="acad_sess_school_curr_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({
                    "end_date": (
                        "The end date must be after the start date."
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class AcademicTerm(models.Model):
    """
    Represents a term, semester or academic period
    within an academic session.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="terms",
    )

    name = models.CharField(max_length=50)

    term_number = models.PositiveSmallIntegerField(
        help_text="The order of this term within its academic session."
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Academic Term"
        verbose_name_plural = "Academic Terms"
        ordering = ["term_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["session", "name"],
                name="unique_session_term_name",
            ),
            models.UniqueConstraint(
                fields=["session", "term_number"],
                name="unique_session_term_number",
            ),
            models.UniqueConstraint(
                fields=["session"],
                condition=Q(is_current=True),
                name="unique_current_term_per_session",
            ),
        ]

        indexes = [
            models.Index(
                fields=["session", "is_current"],
                name="acad_term_session_current_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.term_number is not None and self.term_number < 1:
            errors["term_number"] = (
                "Term number must be at least 1."
            )

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                errors["end_date"] = (
                    "The end date must be after the start date."
                )

        if self.session_id:
            session = self.session

            if self.start_date and self.end_date:
                if (
                    self.start_date < session.start_date
                    or self.end_date > session.end_date
                ):
                    errors["start_date"] = (
                        "The term dates must fall within "
                        "the academic session."
                    )

            if self.is_current and not session.is_current:
                errors["is_current"] = (
                    "A term cannot be current unless "
                    "its academic session is current."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session.name} - {self.name}"


class ClassLevel(models.Model):
    """
    Represents an educational level within a school.

    Schools can use predefined categories or create
    completely custom class levels.
    """

    class Category(models.TextChoices):
        CRECHE = "creche", "Creche"
        NURSERY = "nursery", "Nursery"
        PRIMARY = "primary", "Primary"
        JUNIOR_SECONDARY = (
            "junior_secondary",
            "Junior Secondary",
        )
        SENIOR_SECONDARY = (
            "senior_secondary",
            "Senior Secondary",
        )
        OTHER = "other", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="class_levels",
    )

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
    )

    display_order = models.PositiveSmallIntegerField(
        default=0,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class Level"
        verbose_name_plural = "Class Levels"
        ordering = ["display_order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_school_class_level",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "is_active"],
                name="class_level_school_active_idx",
            ),
        ]

    def __str__(self):
        return self.name


class SchoolClass(models.Model):
    """
    Represents a specific class section.

    Examples:
    JSS 1A
    JSS 1B
    Primary 3 Blue
    Nursery 2
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="school_classes",
    )

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name="sections",
    )

    section_name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=(
            "Examples: A, B, Blue or Red. "
            "Leave blank if there is no section."
        ),
    )

    capacity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Class"
        verbose_name_plural = "School Classes"
        ordering = [
            "class_level__display_order",
            "section_name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["class_level", "section_name"],
                name="unique_class_level_section",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "is_active"],
                name="school_class_school_active_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.school_id
            and self.class_level_id
            and self.school_id != self.class_level.school_id
        ):
            raise ValidationError({
                "class_level": (
                    "This class level does not belong to this school."
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        if self.section_name:
            return f"{self.class_level.name} {self.section_name}"

        return self.class_level.name

    def __str__(self):
        return self.full_name
