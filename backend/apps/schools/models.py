
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .permission_registry import (
    SCHOOL_PERMISSION_CHOICES,
    SCHOOL_PERMISSION_CHOICES_VALUES,
)


class School(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=280,
        unique=True,
        blank=True,
    )

    email = models.EmailField(blank=True, default="")

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    address = models.TextField(blank=True, default="")

    website = models.URLField(blank=True, default="")

    logo = models.ImageField(
        upload_to="schools/logos/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    timezone = models.CharField(
        max_length=50,
        default="Africa/Lagos",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "school"
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SchoolMembership(models.Model):

    class Role(models.TextChoices):
        SCHOOL_OWNER = "school_owner", "School Owner"
        SCHOOL_ADMIN = "school_admin", "School Admin"
        PRINCIPAL = "principal", "Principal"
        ACCOUNTANT = "accountant", "Accountant"
        TEACHER = "teacher", "Teacher"
        STAFF = "staff", "Staff"
        PARENT = "parent", "Parent"
        STUDENT = "student", "Student"

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="school_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INVITED,
        db_index=True,
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="school_invitations_sent",
    )

    invited_at = models.DateTimeField(default=timezone.now)

    joined_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Membership"
        verbose_name_plural = "School Memberships"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "user"],
                name="unique_user_school_membership",
            )
        ]

        indexes = [
            models.Index(
                fields=["school", "status"],
                name="membership_school_status_idx",
            ),
            models.Index(
                fields=["user", "status"],
                name="membership_user_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.school.name} ({self.get_role_display()})"
        )


class SchoolMemberPermission(models.Model):
    """
    Stores custom permission overrides for individual
    members of a school.

    is_granted=True grants the permission.
    is_granted=False explicitly denies the permission.
    """

    membership = models.ForeignKey(
        SchoolMembership,
        on_delete=models.CASCADE,
        related_name="custom_permissions",
    )

    permission = models.CharField(
        max_length=100,
        choices=SCHOOL_PERMISSION_CHOICES,
    )

    is_granted = models.BooleanField(default=True)

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="school_permissions_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Member Permission"
        verbose_name_plural = "School Member Permissions"

        constraints = [
            models.UniqueConstraint(
                fields=["membership", "permission"],
                name="unique_member_custom_permission",
            )
        ]

        ordering = ["permission"]

    def clean(self):
        super().clean()

        if self.permission not in SCHOOL_PERMISSION_CHOICES_VALUES:
            raise ValidationError({
                "permission": (
                    "This permission is not registered in Balora Edu."
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Granted" if self.is_granted else "Denied"

        return (
            f"{self.membership.user.email} - "
            f"{self.permission} ({status})"
        )