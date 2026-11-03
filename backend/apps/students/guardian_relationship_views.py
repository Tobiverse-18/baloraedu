from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from apps.schools.models import School, SchoolMembership
from apps.students.models import StudentGuardian
from apps.students.permissions import HasStudentGuardianPermission
from apps.students.serializers import StudentGuardianSerializer


class StudentGuardianQuerysetMixin:
    """
    Provides school-scoped access to student-guardian relationships.

    Parents can only see relationships connected to their own
    Guardian profile.

    Other authorised roles can access relationships belonging
    to the requested school.
    """

    permission_classes = [HasStudentGuardianPermission]

    def get_school(self):
        return get_object_or_404(
            School,
            pk=self.kwargs["school_id"],
            status=School.Status.ACTIVE,
        )

    def get_membership(self):
        if not hasattr(self, "_relationship_membership"):
            self._relationship_membership = (
                SchoolMembership.objects.filter(
                    school_id=self.kwargs["school_id"],
                    user=self.request.user,
                    status=SchoolMembership.Status.ACTIVE,
                    school__status=School.Status.ACTIVE,
                ).first()
            )

        return self._relationship_membership

    def get_queryset(self):
        membership = self.get_membership()

        if membership is None:
            return StudentGuardian.objects.none()

        queryset = StudentGuardian.objects.filter(
            student__school_id=self.kwargs["school_id"],
            guardian__school_id=self.kwargs["school_id"],
        ).select_related(
            "student",
            "guardian",
            "student__school",
            "guardian__school",
        )

        if membership.role == SchoolMembership.Role.PARENT:
            return queryset.filter(
                guardian__user=self.request.user,
                guardian__is_active=True,
            )

        return queryset

    def get_serializer_class(self):
        if self.get_membership() is None:
            raise PermissionDenied(
                "You do not have an active membership in this school."
            )

        return StudentGuardianSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["school"] = self.get_school()
        return context


class StudentGuardianListCreateView(
    StudentGuardianQuerysetMixin,
    generics.ListCreateAPIView,
):
    """
    GET:
        List student-guardian relationships.

    POST:
        Create a student-guardian relationship.
        Requires guardians.manage.
    """

    def perform_create(self, serializer):
        serializer.save()


class StudentGuardianDetailView(
    StudentGuardianQuerysetMixin,
    generics.RetrieveUpdateAPIView,
):
    """
    GET:
        Retrieve a student-guardian relationship.

    PUT/PATCH:
        Update a student-guardian relationship.
        Requires guardians.manage.

    DELETE:
        Not supported.
    """

    lookup_field = "pk"
    lookup_url_kwarg = "relationship_id"