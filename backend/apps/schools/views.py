
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    School,
    SchoolMembership,
    SchoolMemberPermission,
)
from .permissions import (
    IsActiveSchoolMember,
    IsSchoolManagementMember,
    HasSchoolRole,
)
from .role_permissions import ROLE_PERMISSIONS
from .permission_registry import SCHOOL_PERMISSION_CHOICES
from .serializers import (
    SchoolRegistrationSerializer,
    SchoolMembershipSerializer,
    SchoolMemberPermissionWriteSerializer,
)


class SchoolRegistrationView(generics.CreateAPIView):
    serializer_class = SchoolRegistrationSerializer
    permission_classes = [IsAuthenticated]


class UserSchoolMembershipListView(generics.ListAPIView):
    serializer_class = SchoolMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            SchoolMembership.objects
            .select_related("school")
            .filter(
                user=self.request.user,
                status=SchoolMembership.Status.ACTIVE,
            )
            .order_by("-created_at")
        )


class SchoolWorkspaceView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolManagementMember]

    def get(self, request, school_id):
        school = get_object_or_404(
            School,
            id=school_id,
            status__in=[
                School.Status.PENDING,
                School.Status.ACTIVE,
            ],
        )

        return Response({
            "id": str(school.id),
            "name": school.name,
            "slug": school.slug,
            "email": school.email,
            "phone_number": school.phone_number,
            "address": school.address,
            "website": school.website,
            "status": school.status,
            "timezone": school.timezone,
        })


class SchoolMemberPermissionListCreateView(APIView):
    """
    Lists, grants and denies custom permissions
    for a member of a specific school.

    Pending schools:
        Only school owners can manage permissions.

    Active schools:
        School owners and authorised school admins
        can manage permissions.

    Suspended and archived schools:
        Access is blocked.
    """

    permission_classes = [IsAuthenticated, HasSchoolRole]

    required_school_roles = (
        SchoolMembership.Role.SCHOOL_OWNER,
        SchoolMembership.Role.SCHOOL_ADMIN,
    )

    def get_actor_membership(self):
        return get_object_or_404(
            SchoolMembership.objects.select_related("school"),
            school_id=self.kwargs["school_id"],
            user=self.request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status__in=[
                School.Status.PENDING,
                School.Status.ACTIVE,
            ],
        )

    def get_target_membership(self):
        return get_object_or_404(
            SchoolMembership.objects.select_related(
                "school",
                "user",
            ).prefetch_related("custom_permissions"),
            id=self.kwargs["membership_id"],
            school_id=self.kwargs["school_id"],
        )

    def get(self, request, school_id, membership_id):

        actor_membership = self.get_actor_membership()
        target_membership = self.get_target_membership()

        custom_permissions = {
            item.permission: item
            for item in target_membership.custom_permissions.all()
        }

        default_permissions = ROLE_PERMISSIONS.get(
            target_membership.role,
            set(),
        )

        permissions = []

        for permission, label in SCHOOL_PERMISSION_CHOICES:

            custom = custom_permissions.get(permission)

            default_access = (
                permission in default_permissions
            )

            if target_membership.role == SchoolMembership.Role.SCHOOL_OWNER:
                effective_access = True
            elif custom is not None:
                effective_access = custom.is_granted
            else:
                effective_access = default_access

            permissions.append({
                "permission": permission,
                "label": label,
                "default_access": default_access,
                "custom_override": (
                    custom.is_granted if custom else None
                ),
                "effective_access": effective_access,
            })

        return Response({
            "membership_id": str(target_membership.id),
            "member_email": target_membership.user.email,
            "role": target_membership.role,
            "permissions": permissions,
        })

    def post(self, request, school_id, membership_id):

        actor_membership = self.get_actor_membership()
        target_membership = self.get_target_membership()

        serializer = SchoolMemberPermissionWriteSerializer(
            data=request.data,
            context={
                "request": request,
                "membership": target_membership,
                "actor_membership": actor_membership,
            },
        )

        serializer.is_valid(raise_exception=True)

        with transaction.atomic():

            permission_record, created = (
                SchoolMemberPermission.objects.update_or_create(
                    membership=target_membership,
                    permission=serializer.validated_data["permission"],
                    defaults={
                        "is_granted": serializer.validated_data["is_granted"],
                        "assigned_by": request.user,
                    },
                )
            )

        return Response(
            {
                "message": (
                    "Permission created successfully."
                    if created
                    else "Permission updated successfully."
                ),
                "permission": permission_record.permission,
                "is_granted": permission_record.is_granted,
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


class SchoolMemberPermissionDetailView(APIView):
    """
    Removes a custom permission override,
    restoring the member's default role access.

    Only authorised school management members can
    remove permission overrides.
    """

    permission_classes = [IsAuthenticated, HasSchoolRole]

    required_school_roles = (
        SchoolMembership.Role.SCHOOL_OWNER,
        SchoolMembership.Role.SCHOOL_ADMIN,
    )

    def delete(self, request, school_id, membership_id, permission):

        actor_membership = get_object_or_404(
            SchoolMembership.objects.select_related("school"),
            school_id=school_id,
            user=request.user,
            status=SchoolMembership.Status.ACTIVE,
            school__status__in=[
                School.Status.PENDING,
                School.Status.ACTIVE,
            ],
        )

        target_membership = get_object_or_404(
            SchoolMembership,
            id=membership_id,
            school_id=school_id,
        )

        permission_record = get_object_or_404(
            SchoolMemberPermission,
            membership=target_membership,
            permission=permission,
        )

        serializer = SchoolMemberPermissionWriteSerializer(
            data={
                "permission": permission_record.permission,
                "is_granted": permission_record.is_granted,
            },
            context={
                "request": request,
                "membership": target_membership,
                "actor_membership": actor_membership,
            },
        )

        serializer.is_valid(raise_exception=True)

        permission_record.delete()

        return Response(
            {
                "message": (
                    "Custom permission removed. "
                    "The member's default role permission now applies."
                )
            },
            status=status.HTTP_200_OK,
        )
