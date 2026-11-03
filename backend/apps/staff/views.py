from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.schools.models import School, SchoolMembership

from apps.staff.models import StaffDepartment
from apps.staff.permissions import HasStaffPermission
from apps.staff.serializers import StaffDepartmentSerializer


class StaffSchoolQuerysetMixin:
    """
    Shared school-scoping and membership logic for Staff API views.
    """

    def get_school(self):
        if not hasattr(self, "_staff_school"):
            self._staff_school = get_object_or_404(
                School,
                id=self.kwargs["school_id"],
                status=School.Status.ACTIVE,
            )

        return self._staff_school

    def get_membership(self):
        if not hasattr(self, "_staff_membership"):
            self._staff_membership = get_object_or_404(
                SchoolMembership.objects.select_related("school"),
                school=self.get_school(),
                user=self.request.user,
                status=SchoolMembership.Status.ACTIVE,
            )

        return self._staff_membership

    def get_department_queryset(self):
        return StaffDepartment.objects.filter(
            school=self.get_school(),
        ).select_related(
            "school",
        )


class StaffDepartmentListCreateView(
    StaffSchoolQuerysetMixin,
    generics.ListCreateAPIView,
):
    """
    GET: List departments belonging to the requested school.
    POST: Create a department in the requested school.
    """

    permission_classes = [
        IsAuthenticated,
        HasStaffPermission,
    ]

    serializer_class = StaffDepartmentSerializer

    def get_queryset(self):
        self.get_membership()

        return self.get_department_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["school"] = self.get_school()
        return context

    def perform_create(self, serializer):
        serializer.save(
            school=self.get_school(),
        )


class StaffDepartmentDetailView(
    StaffSchoolQuerysetMixin,
    generics.RetrieveUpdateAPIView,
):
    """
    GET: Retrieve a department within the requested school.
    PUT/PATCH: Update a department.

    DELETE is intentionally not implemented.
    """

    permission_classes = [
        IsAuthenticated,
        HasStaffPermission,
    ]

    serializer_class = StaffDepartmentSerializer

    lookup_field = "id"
    lookup_url_kwarg = "department_id"

    def get_queryset(self):
        self.get_membership()

        return self.get_department_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["school"] = self.get_school()
        return context