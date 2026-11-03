from django.shortcuts import get_object_or_404

from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated

from apps.schools.models import School, SchoolMembership

from .models import Student
from .permissions import HasStudentPermission
from .serializers import StudentSerializer


class AccountantStudentSerializer(serializers.ModelSerializer):
    """
    Accountants can identify students for financial and administrative
    purposes, but cannot access private student information.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "first_name",
            "last_name",
            "full_name",
            "status",
        ]
        read_only_fields = fields


class StudentPortalSerializer(serializers.ModelSerializer):
    """
    Limited student information for parent and student portal access.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "gender",
            "status",
            "admission_date",
        ]
        read_only_fields = fields


class StudentSchoolQuerysetMixin:
    """
    Shared school-scoping and membership logic for student API views.
    """

    def get_school(self):
        if not hasattr(self, "_student_school"):
            self._student_school = get_object_or_404(
                School,
                id=self.kwargs["school_id"],
                status=School.Status.ACTIVE,
            )

        return self._student_school

    def get_membership(self):
        if not hasattr(self, "_student_membership"):
            self._student_membership = get_object_or_404(
                SchoolMembership.objects.select_related("school"),
                school=self.get_school(),
                user=self.request.user,
                status=SchoolMembership.Status.ACTIVE,
            )

        return self._student_membership

    def get_student_queryset(self):
        school = self.get_school()
        membership = self.get_membership()

        queryset = Student.objects.filter(
            school=school,
        ).select_related(
            "school",
            "user",
        )

        if membership.role == SchoolMembership.Role.PARENT:
            return queryset.filter(
                guardian_links__guardian__user=self.request.user,
                guardian_links__guardian__is_active=True,
            ).distinct()

        if membership.role == SchoolMembership.Role.STUDENT:
            return queryset.filter(
                user=self.request.user,
            )

        return queryset


class StudentListCreateView(
    StudentSchoolQuerysetMixin,
    generics.ListCreateAPIView,
):
    """
    GET: List students accessible to the current school member.
    POST: Register a student, if the member has permission.
    """

    permission_classes = [
        IsAuthenticated,
        HasStudentPermission,
    ]

    def get_queryset(self):
        return self.get_student_queryset()

    def get_serializer_class(self):
        membership = self.get_membership()

        if self.request.method == "POST":
            return StudentSerializer

        if membership.role == SchoolMembership.Role.ACCOUNTANT:
            return AccountantStudentSerializer

        if membership.role in (
            SchoolMembership.Role.PARENT,
            SchoolMembership.Role.STUDENT,
        ):
            return StudentPortalSerializer

        return StudentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["school"] = self.get_school()
        return context

    def perform_create(self, serializer):
        serializer.save(
            school=self.get_school(),
        )


class StudentDetailView(
    StudentSchoolQuerysetMixin,
    generics.RetrieveUpdateAPIView,
):
    """
    GET: Retrieve a student within the requested school.
    PUT/PATCH: Update a student when the member has permission.

    DELETE is intentionally not implemented.
    """

    permission_classes = [
        IsAuthenticated,
        HasStudentPermission,
    ]

    lookup_field = "id"
    lookup_url_kwarg = "student_id"

    def get_queryset(self):
        return self.get_student_queryset()

    def get_serializer_class(self):
        membership = self.get_membership()

        if self.request.method in ("PUT", "PATCH"):
            return StudentSerializer

        if membership.role == SchoolMembership.Role.ACCOUNTANT:
            return AccountantStudentSerializer

        if membership.role in (
            SchoolMembership.Role.PARENT,
            SchoolMembership.Role.STUDENT,
        ):
            return StudentPortalSerializer

        return StudentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["school"] = self.get_school()
        return context