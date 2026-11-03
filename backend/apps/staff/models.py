import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.schools.models import School, SchoolMembership
from apps.academics.models import AcademicSession, SchoolClass, Subject


class StaffDepartment(models.Model):
    """
    A department belonging to one school.
    Each staff member can have one primary department.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="staff_departments",
    )

    name = models.CharField(max_length=100)

    description = models.TextField(
        blank=True,
        default="",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff Department"
        verbose_name_plural = "Staff Departments"
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_school_staff_department",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "is_active"],
                name="staff_dept_school_active_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class StaffProfile(models.Model):
    """
    A permanent employee profile belonging to one school.

    Login accounts are optional and are not created automatically.
    """

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    class StaffType(models.TextChoices):
        TEACHING = "teaching", "Teaching Staff"
        NON_TEACHING = "non_teaching", "Non-Teaching Staff"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full-Time"
        PART_TIME = "part_time", "Part-Time"
        CONTRACT = "contract", "Contract"
        TEMPORARY = "temporary", "Temporary"
        VOLUNTEER = "volunteer", "Volunteer"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        SUSPENDED = "suspended", "Suspended"
        TERMINATED = "terminated", "Terminated"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="staff_profiles",
    )

    staff_number = models.CharField(max_length=50)

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

    alternative_phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    address = models.TextField(
        blank=True,
        default="",
    )

    passport = models.ImageField(
        upload_to="staff/passports/",
        null=True,
        blank=True,
    )

    staff_type = models.CharField(
        max_length=20,
        choices=StaffType.choices,
        default=StaffType.NON_TEACHING,
        db_index=True,
    )

    department = models.ForeignKey(
        StaffDepartment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="staff_members",
    )

    job_title = models.CharField(max_length=100)

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )

    employment_date = models.DateField(
        null=True,
        blank=True,
    )

    termination_date = models.DateField(
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
        related_name="staff_profiles",
        help_text="Optional employee portal account.",
    )

    notes = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"
        ordering = ["last_name", "first_name"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "staff_number"],
                name="unique_school_staff_number",
            ),
            models.UniqueConstraint(
                fields=["school", "user"],
                condition=Q(user__isnull=False),
                name="unique_school_staff_user",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "status"],
                name="staff_school_status_idx",
            ),
            models.Index(
                fields=["school", "staff_type"],
                name="staff_school_type_idx",
            ),
            models.Index(
                fields=["school", "last_name", "first_name"],
                name="staff_school_name_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        # Department must belong to the same school.
        if self.department_id and self.school_id:
            if self.department.school_id != self.school_id:
                errors["department"] = (
                    "The department must belong to this school."
                )

            else:
                # An inactive department cannot be newly assigned.
                # Existing staff can retain their department if it
                # is deactivated later.
                department_changed = True

                if self.pk:
                    previous = (
                        StaffProfile.objects
                        .filter(pk=self.pk)
                        .values_list("department_id", flat=True)
                        .first()
                    )

                    department_changed = (
                        previous != self.department_id
                    )

                if (
                    department_changed
                    and not self.department.is_active
                ):
                    errors["department"] = (
                        "You cannot assign staff to an inactive "
                        "department."
                    )

        # Employment dates must be consistent.
        if self.employment_date and self.termination_date:
            if self.termination_date < self.employment_date:
                errors["termination_date"] = (
                    "Termination date cannot be before "
                    "the employment date."
                )

        # Validate optional portal account membership.
        if self.user_id and self.school_id:

            if self.staff_type == self.StaffType.TEACHING:
                allowed_roles = [
                    SchoolMembership.Role.TEACHER,
                    SchoolMembership.Role.PRINCIPAL,
                ]

            else:
                allowed_roles = [
                    SchoolMembership.Role.SCHOOL_OWNER,
                    SchoolMembership.Role.SCHOOL_ADMIN,
                    SchoolMembership.Role.PRINCIPAL,
                    SchoolMembership.Role.ACCOUNTANT,
                    SchoolMembership.Role.STAFF,
                ]

            membership_exists = SchoolMembership.objects.filter(
                school_id=self.school_id,
                user_id=self.user_id,
                role__in=allowed_roles,
            ).exists()

            if not membership_exists:
                errors["user"] = (
                    "The linked account must have a compatible "
                    "employee membership in this school."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return " ".join(
            part
            for part in [
                self.first_name,
                self.middle_name,
                self.last_name,
            ]
            if part
        )

    def __str__(self):
        return f"{self.full_name} ({self.staff_number})"


class ClassTeacherAssignment(models.Model):
    """
    Assigns a teaching staff member as the class teacher
    for a particular class during an academic session.

    Only one class teacher is allowed per class per session.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="class_teacher_assignments",
    )

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.PROTECT,
        related_name="class_teacher_assignments",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="class_teacher_assignments",
    )

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name="class_teacher_assignments",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class Teacher Assignment"
        verbose_name_plural = "Class Teacher Assignments"
        ordering = ["-session__start_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "session"],
                name="unique_class_teacher_per_session",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "session"],
                name="cls_tch_school_sess_idx",
            ),
            models.Index(
                fields=["staff", "session"],
                name="cls_tch_staff_sess_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.staff_id and self.school_id:
            if self.staff.school_id != self.school_id:
                errors["staff"] = (
                    "The teacher must belong to this school."
                )

            if self.staff.staff_type != StaffProfile.StaffType.TEACHING:
                errors["staff"] = (
                    "Only teaching staff can be assigned "
                    "as class teachers."
                )

            # Only new assignments or teacher changes require
            # the selected teacher to be ACTIVE.
            staff_assignment_changed = self._state.adding

            if not self._state.adding:
                previous_staff_id = (
                    ClassTeacherAssignment.objects
                    .filter(pk=self.pk)
                    .values_list("staff_id", flat=True)
                    .first()
                )

                staff_assignment_changed = (
                    previous_staff_id != self.staff_id
                )

            if (
                staff_assignment_changed
                and self.staff.status != StaffProfile.Status.ACTIVE
            ):
                errors["staff"] = (
                    "Only active teaching staff can receive "
                    "new class teacher assignments."
                )

        if self.school_class_id and self.school_id:
            if self.school_class.school_id != self.school_id:
                errors["school_class"] = (
                    "The class must belong to this school."
                )
            elif not self.school_class.is_active:
                errors["school_class"] = (
                    "You cannot assign a class teacher "
                    "to an inactive class."
                )

        if self.session_id and self.school_id:
            if self.session.school_id != self.school_id:
                errors["session"] = (
                    "The academic session must belong "
                    "to this school."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.staff.full_name} - "
            f"{self.school_class.full_name} - "
            f"{self.session.name}"
        )


class SubjectTeacherAssignment(models.Model):
    """
    Assigns a teaching staff member to teach a subject
    in a particular class during an academic session.

    Multiple teachers can teach the same subject
    in the same class.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="subject_teacher_assignments",
    )

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.PROTECT,
        related_name="subject_teacher_assignments",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="subject_teacher_assignments",
    )

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name="subject_teacher_assignments",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subject Teacher Assignment"
        verbose_name_plural = "Subject Teacher Assignments"
        ordering = ["subject__name", "staff__last_name"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "staff",
                    "subject",
                    "school_class",
                    "session",
                ],
                name="unique_staff_subject_class_session",
            ),
        ]

        indexes = [
            models.Index(
                fields=["school", "session", "school_class"],
                name="subj_asgn_school_cls_idx",
            ),
            models.Index(
                fields=["staff", "session"],
                name="subj_asgn_staff_sess_idx",
            ),
            models.Index(
                fields=["subject", "school_class", "session"],
                name="subj_asgn_subj_cls_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.staff_id and self.school_id:
            if self.staff.school_id != self.school_id:
                errors["staff"] = (
                    "The teacher must belong to this school."
                )

            if self.staff.staff_type != StaffProfile.StaffType.TEACHING:
                errors["staff"] = (
                    "Only teaching staff can receive "
                    "subject teaching assignments."
                )

            # Only new assignments or teacher changes require
            # the selected teacher to be ACTIVE.
            staff_assignment_changed = self._state.adding

            if not self._state.adding:
                previous_staff_id = (
                    SubjectTeacherAssignment.objects
                    .filter(pk=self.pk)
                    .values_list("staff_id", flat=True)
                    .first()
                )

                staff_assignment_changed = (
                    previous_staff_id != self.staff_id
                )

            if (
                staff_assignment_changed
                and self.staff.status != StaffProfile.Status.ACTIVE
            ):
                errors["staff"] = (
                    "Only active teaching staff can receive "
                    "new subject teaching assignments."
                )

        if self.subject_id and self.school_id:
            if self.subject.school_id != self.school_id:
                errors["subject"] = (
                    "The subject must belong to this school."
                )
            elif not self.subject.is_active:
                errors["subject"] = (
                    "You cannot assign teachers to an inactive subject."
                )

        if self.school_class_id and self.school_id:
            if self.school_class.school_id != self.school_id:
                errors["school_class"] = (
                    "The class must belong to this school."
                )
            elif not self.school_class.is_active:
                errors["school_class"] = (
                    "You cannot assign teachers to an inactive class."
                )

        if self.session_id and self.school_id:
            if self.session.school_id != self.school_id:
                errors["session"] = (
                    "The academic session must belong "
                    "to this school."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.staff.full_name} - "
            f"{self.subject.name} - "
            f"{self.school_class.full_name} - "
            f"{self.session.name}"
        )