from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.schools.models import SchoolMembership
from apps.staff.models import StaffDepartment, StaffProfile


User = get_user_model()


class StaffDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StaffDepartment
        fields = [
            "id",
            "school",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "school",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Department name is required."
            )

        school = self.context.get("school")

        if school is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        queryset = StaffDepartment.objects.filter(
            school=school,
            name__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "A department with this name already exists in this school."
            )

        return value

    def validate(self, attrs):
        if self.context.get("school") is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        return attrs


class StaffProfileSerializer(serializers.ModelSerializer):

    department = serializers.PrimaryKeyRelatedField(
        queryset=StaffDepartment.objects.none(),
        required=False,
        allow_null=True,
    )

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = StaffProfile

        fields = [
            "id",
            "school",
            "staff_number",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "gender",
            "email",
            "phone_number",
            "alternative_phone_number",
            "address",
            "passport",
            "staff_type",
            "department",
            "job_title",
            "employment_type",
            "employment_date",
            "termination_date",
            "status",
            "user",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "school",
            "full_name",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        fields = super().get_fields()

        school = self.context.get("school")

        if school is not None:
            fields["department"].queryset = (
                StaffDepartment.objects.filter(
                    school=school,
                )
            )

        return fields

    def validate_staff_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Staff number is required."
            )

        school = self.context.get("school")

        if school is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        queryset = StaffProfile.objects.filter(
            school=school,
            staff_number__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "A staff member with this staff number already exists."
            )

        return value

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name is required."
            )

        return value

    def validate_middle_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name is required."
            )

        return value

    def validate_job_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Job title is required."
            )

        return value

    def validate(self, attrs):
        school = self.context.get("school")

        if school is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        # Resolve the effective department, including partial updates.
        department = attrs.get(
            "department",
            self.instance.department if self.instance else None,
        )

        if department is not None:
            if department.school_id != school.id:
                raise serializers.ValidationError({
                    "department": (
                        "The department must belong to this school."
                    )
                })

            department_changed = (
                self.instance is None
                or self.instance.department_id != department.id
            )

            if department_changed and not department.is_active:
                raise serializers.ValidationError({
                    "department": (
                        "You cannot assign staff to an inactive department."
                    )
                })

        # Validate employment dates.
        employment_date = attrs.get(
            "employment_date",
            self.instance.employment_date if self.instance else None,
        )

        termination_date = attrs.get(
            "termination_date",
            self.instance.termination_date if self.instance else None,
        )

        if (
            employment_date
            and termination_date
            and termination_date < employment_date
        ):
            raise serializers.ValidationError({
                "termination_date": (
                    "Termination date cannot be before the employment date."
                )
            })

        # Resolve effective staff type and linked user.
        staff_type = attrs.get(
            "staff_type",
            self.instance.staff_type if self.instance
            else StaffProfile.StaffType.NON_TEACHING,
        )

        user = attrs.get(
            "user",
            self.instance.user if self.instance else None,
        )

        if user is not None:
            if staff_type == StaffProfile.StaffType.TEACHING:
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
                school=school,
                user=user,
                role__in=allowed_roles,
            ).exists()

            if not membership_exists:
                raise serializers.ValidationError({
                    "user": (
                        "The linked account must have a compatible "
                        "employee membership in this school."
                    )
                })

            # Prevent linking one portal account to multiple profiles
            # within the same school.
            duplicate_user = StaffProfile.objects.filter(
                school=school,
                user=user,
            )

            if self.instance:
                duplicate_user = duplicate_user.exclude(
                    pk=self.instance.pk,
                )

            if duplicate_user.exists():
                raise serializers.ValidationError({
                    "user": (
                        "This account is already linked to another "
                        "staff profile in this school."
                    )
                })

        return attrs