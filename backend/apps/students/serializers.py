
from rest_framework import serializers

from apps.academics.models import AcademicSession, SchoolClass
from apps.students.models import (
    Student,
    Guardian,
    StudentGuardian,
    StudentEnrollment,
)


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "school",
            "admission_number",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "gender",
            "email",
            "phone_number",
            "address",
            "passport",
            "status",
            "admission_date",
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

    def validate_admission_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Admission number is required."
            )

        school = self.context.get("school")

        if school is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        queryset = Student.objects.filter(
            school=school,
            admission_number=value,
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This admission number already exists in this school."
            )

        return value

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name is required."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name is required."
            )

        return value

    def validate(self, attrs):
        if self.context.get("school") is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        date_of_birth = attrs.get(
            "date_of_birth",
            getattr(self.instance, "date_of_birth", None),
        )

        admission_date = attrs.get(
            "admission_date",
            getattr(self.instance, "admission_date", None),
        )

        if date_of_birth and admission_date:
            if admission_date < date_of_birth:
                raise serializers.ValidationError({
                    "admission_date": (
                        "Admission date cannot be before date of birth."
                    )
                })

        return attrs


class GuardianSerializer(serializers.ModelSerializer):
    """
    Full guardian serializer for authorised school administrators.
    """

    class Meta:
        model = Guardian
        fields = [
            "id",
            "school",
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone_number",
            "alternative_phone_number",
            "occupation",
            "address",
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

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name is required."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name is required."
            )

        return value

    def validate_phone_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Phone number is required."
            )

        return value


class AccountantGuardianSerializer(serializers.ModelSerializer):
    """
    Restricted guardian information for accountants.

    Accountants do not need access to private contact details
    beyond the primary phone number.
    """

    class Meta:
        model = Guardian
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "phone_number",
            "is_active",
        ]

        read_only_fields = fields


class ParentGuardianSerializer(serializers.ModelSerializer):
    """
    Guardian profile visible to the parent linked to that profile.

    The parent can view their own contact information but cannot
    modify the school-managed guardian record through this API.
    """

    class Meta:
        model = Guardian
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone_number",
            "alternative_phone_number",
            "occupation",
            "address",
            "is_active",
        ]

        read_only_fields = fields


class StudentGuardianSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.full_name",
        read_only=True,
    )

    guardian_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentGuardian
        fields = [
            "id",
            "student",
            "student_name",
            "guardian",
            "guardian_name",
            "relationship",
            "is_primary",
            "is_emergency_contact",
            "can_pickup_student",
            "receives_notifications",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student_name",
            "guardian_name",
            "created_at",
            "updated_at",
        ]

        validators = []

    def get_fields(self):
        fields = super().get_fields()

        school = self.context.get("school")

        if school is None:
            fields["student"].queryset = Student.objects.none()
            fields["guardian"].queryset = Guardian.objects.none()
        else:
            fields["student"].queryset = Student.objects.filter(
                school=school,
            )

            fields["guardian"].queryset = Guardian.objects.filter(
                school=school,
            )

        return fields

    def get_guardian_name(self, obj):
        return str(obj.guardian)

    def validate(self, attrs):
        if self.context.get("school") is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        student = attrs.get(
            "student",
            getattr(self.instance, "student", None),
        )

        guardian = attrs.get(
            "guardian",
            getattr(self.instance, "guardian", None),
        )

        is_primary = attrs.get(
            "is_primary",
            getattr(self.instance, "is_primary", False),
        )

        if student and guardian:
            if student.school_id != guardian.school_id:
                raise serializers.ValidationError({
                    "guardian": (
                        "The guardian and student must belong "
                        "to the same school."
                    )
                })

            duplicate = StudentGuardian.objects.filter(
                student=student,
                guardian=guardian,
            )

            if self.instance:
                duplicate = duplicate.exclude(pk=self.instance.pk)

            if duplicate.exists():
                raise serializers.ValidationError({
                    "guardian": (
                        "This guardian is already linked to this student."
                    )
                })

        if student and is_primary:
            existing_primary = StudentGuardian.objects.filter(
                student=student,
                is_primary=True,
            )

            if self.instance:
                existing_primary = existing_primary.exclude(
                    pk=self.instance.pk,
                )

            if existing_primary.exists():
                raise serializers.ValidationError({
                    "is_primary": (
                        "This student already has a primary guardian."
                    )
                })

        return attrs


class StudentEnrollmentSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.full_name",
        read_only=True,
    )

    session_name = serializers.CharField(
        source="session.name",
        read_only=True,
    )

    class_name = serializers.CharField(
        source="school_class.full_name",
        read_only=True,
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "school",
            "student",
            "student_name",
            "session",
            "session_name",
            "school_class",
            "class_name",
            "enrollment_date",
            "status",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "school",
            "student_name",
            "session_name",
            "class_name",
            "created_at",
            "updated_at",
        ]

        validators = []

    def get_fields(self):
        fields = super().get_fields()

        school = self.context.get("school")

        if school is None:
            fields["student"].queryset = Student.objects.none()
            fields["session"].queryset = AcademicSession.objects.none()
            fields["school_class"].queryset = SchoolClass.objects.none()
        else:
            fields["student"].queryset = Student.objects.filter(
                school=school,
            )

            fields["session"].queryset = AcademicSession.objects.filter(
                school=school,
            )

            fields["school_class"].queryset = SchoolClass.objects.filter(
                school=school,
            )

        return fields

    def validate(self, attrs):
        student = attrs.get(
            "student",
            getattr(self.instance, "student", None),
        )

        session = attrs.get(
            "session",
            getattr(self.instance, "session", None),
        )

        school_class = attrs.get(
            "school_class",
            getattr(self.instance, "school_class", None),
        )

        enrollment_date = attrs.get(
            "enrollment_date",
            getattr(self.instance, "enrollment_date", None),
        )

        status = attrs.get(
            "status",
            getattr(
                self.instance,
                "status",
                StudentEnrollment.Status.ACTIVE,
            ),
        )

        school = self.context.get("school")

        if school is None:
            raise serializers.ValidationError(
                "School context is required."
            )

        if student and student.school_id != school.id:
            raise serializers.ValidationError({
                "student": "Student does not belong to this school."
            })

        if session and session.school_id != school.id:
            raise serializers.ValidationError({
                "session": "Academic session does not belong to this school."
            })

        if school_class and school_class.school_id != school.id:
            raise serializers.ValidationError({
                "school_class": "Class does not belong to this school."
            })

        if session and enrollment_date:
            if not (
                session.start_date
                <= enrollment_date
                <= session.end_date
            ):
                raise serializers.ValidationError({
                    "enrollment_date": (
                        "Enrollment date must fall within the academic session."
                    )
                })

        if (
            student
            and session
            and status == StudentEnrollment.Status.ACTIVE
        ):
            existing = StudentEnrollment.objects.filter(
                student=student,
                session=session,
                status=StudentEnrollment.Status.ACTIVE,
            )

            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError({
                    "student": (
                        "This student already has an active enrollment "
                        "in this academic session."
                    )
                })

        return attrs
