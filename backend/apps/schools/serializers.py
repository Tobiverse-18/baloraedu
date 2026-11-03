
from django.db import transaction
from rest_framework import serializers

from .models import (
    School,
    SchoolMembership,
    SchoolMemberPermission,
)
from .permission_registry import SCHOOL_PERMISSION_CHOICES
from .permission_registry import SchoolPermissions


class SchoolRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "address",
            "website",
        ]

        read_only_fields = ["id"]

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "School name must contain at least 2 characters."
            )

        return value

    def create(self, validated_data):
        request = self.context["request"]

        with transaction.atomic():

            school = School.objects.create(
                created_by=request.user,
                status=School.Status.PENDING,
                **validated_data,
            )

            SchoolMembership.objects.create(
                school=school,
                user=request.user,
                role=SchoolMembership.Role.SCHOOL_OWNER,
                status=SchoolMembership.Status.ACTIVE,
                invited_by=request.user,
            )

        return school


class SchoolSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "slug",
            "email",
            "phone_number",
            "status",
            "created_at",
        ]

        read_only_fields = fields


class SchoolMembershipSerializer(serializers.ModelSerializer):

    school = SchoolSummarySerializer(read_only=True)

    class Meta:
        model = SchoolMembership
        fields = [
            "id",
            "school",
            "role",
            "status",
            "joined_at",
        ]

        read_only_fields = fields


class SchoolMemberPermissionWriteSerializer(serializers.Serializer):

    permission = serializers.ChoiceField(
        choices=SCHOOL_PERMISSION_CHOICES,
    )

    is_granted = serializers.BooleanField()

    def validate(self, attrs):
        membership = self.context["membership"]
        actor_membership = self.context["actor_membership"]

        target_role = membership.role
        actor_role = actor_membership.role
        permission = attrs["permission"]

        # School Owner permissions cannot be overridden.
        if target_role == SchoolMembership.Role.SCHOOL_OWNER:
            raise serializers.ValidationError(
                "A School Owner's permissions cannot be modified."
            )

        # Prevent users from modifying their own permissions.
        if membership.user_id == actor_membership.user_id:
            raise serializers.ValidationError(
                "You cannot modify your own school permissions."
            )

        # School Admins may only manage lower-level school roles.
        if actor_role == SchoolMembership.Role.SCHOOL_ADMIN:

            restricted_roles = {
                SchoolMembership.Role.SCHOOL_OWNER,
                SchoolMembership.Role.SCHOOL_ADMIN,
            }

            if target_role in restricted_roles:
                raise serializers.ValidationError(
                    "School Admins cannot modify the permissions "
                    "of School Owners or other School Admins."
                )

            if permission == SchoolPermissions.SUBSCRIPTION_MANAGE:
                raise serializers.ValidationError({
                    "permission": (
                        "Only a School Owner can assign "
                        "subscription management permission."
                    )
                })

        return attrs


