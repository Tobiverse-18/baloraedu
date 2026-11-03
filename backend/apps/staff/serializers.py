from rest_framework import serializers

from apps.staff.models import StaffDepartment


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