
from django.urls import include, path

from .views import (
    SchoolRegistrationView,
    UserSchoolMembershipListView,
    SchoolWorkspaceView,
    SchoolMemberPermissionListCreateView,
    SchoolMemberPermissionDetailView,
)

urlpatterns = [
    path(
        "register/",
        SchoolRegistrationView.as_view(),
        name="school_register",
    ),
    path(
        "my-schools/",
        UserSchoolMembershipListView.as_view(),
        name="my_schools",
    ),
    path(
        "<uuid:school_id>/workspace/",
        SchoolWorkspaceView.as_view(),
        name="school_workspace",
    ),
    path(
        "<uuid:school_id>/members/<uuid:membership_id>/permissions/",
        SchoolMemberPermissionListCreateView.as_view(),
        name="school_member_permissions",
    ),
    path(
        "<uuid:school_id>/members/<uuid:membership_id>/permissions/<str:permission>/",
        SchoolMemberPermissionDetailView.as_view(),
        name="school_member_permission_detail",
    ),
    path(
        "<uuid:school_id>/students/",
        include("apps.students.urls"),
    ),
    path(
        "<uuid:school_id>/guardians/",
        include("apps.students.guardian_urls"),
    ),
]
