
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from apps.schools.models import School, SchoolMembership
from apps.students.models import Guardian
from apps.students.permissions import HasGuardianPermission
from apps.students.serializers import (
    GuardianSerializer,
    AccountantGuardianSerializer,
    ParentGuardianSerializer,
)


class GuardianQuerysetMixin:
    """
    Provides school-scoped guardian access.

    Parents can only see their own guardian profile.
    Other authorised roles can see guardians belonging
    to the requested school.
    """

    permission_classes = [HasGuardianPermission]

    def get_school(self):
        return get_object_or_404(
            School,
            pk=self.kwargs["school_id"],
            status=School.Status.ACTIVE,
        )

    def get_membership(self):
        if not hasattr(self, "_guardian_membership"):
            self._guardian_membership = SchoolMembership.objects.filter(
                school_id=self.kwargs["school_id"],
                user=self.request.user,
                status=SchoolMembership.Status.ACTIVE,
                school__status=School.Status.ACTIVE,
            ).first()

        return self._guardian_membership

    def get_queryset(self):
        membership = self.get_membership()

        if membership is None:
            return Guardian.objects.none()

        queryset = Guardian.objects.filter(
            school_id=self.kwargs["school_id"],
        ).select_related("school", "user")

        if membership.role == SchoolMembership.Role.PARENT:
            return queryset.filter(
                user=self.request.user,
                is_active=True,
            )

        return queryset

    def get_serializer_class(self):
        membership = self.get_membership()

        if membership is None:
            raise PermissionDenied(
                "You do not have an active membership in this school."
            )

        if membership.role == SchoolMembership.Role.ACCOUNTANT:
            return AccountantGuardianSerializer

        if membership.role == SchoolMembership.Role.PARENT:
            return ParentGuardianSerializer

        return GuardianSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["school"] = self.get_school()
        return context


class GuardianListCreateView(
    GuardianQuerysetMixin,
    generics.ListCreateAPIView,
):
    """
    GET:
        List guardians visible to the authenticated member.

    POST:
        Create a guardian. Requires guardians.manage.
    """

    def perform_create(self, serializer):
        school = self.get_school()

        serializer.save(school=school)


class GuardianDetailView(
    GuardianQuerysetMixin,
    generics.RetrieveUpdateAPIView,
):
    """
    GET:
        Retrieve a guardian visible to the authenticated member.

    PUT/PATCH:
        Update a guardian. Requires guardians.manage.

    DELETE:
        Not supported.
    """

    lookup_field = "pk"
    lookup_url_kwarg = "guardian_id"

    def perform_update(self, serializer):
        serializer.save(school=self.get_school())
