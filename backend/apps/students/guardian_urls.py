from django.urls import path

from apps.students.guardian_views import (
    GuardianListCreateView,
    GuardianDetailView,
)

from apps.students.guardian_relationship_views import (
    StudentGuardianListCreateView,
    StudentGuardianDetailView,
)


urlpatterns = [
    # Guardian endpoints
    path(
        "",
        GuardianListCreateView.as_view(),
        name="guardian-list-create",
    ),
    path(
        "<uuid:guardian_id>/",
        GuardianDetailView.as_view(),
        name="guardian-detail",
    ),

    # Student-guardian relationship endpoints
    path(
        "relationships/",
        StudentGuardianListCreateView.as_view(),
        name="student-guardian-list-create",
    ),
    path(
        "relationships/<uuid:relationship_id>/",
        StudentGuardianDetailView.as_view(),
        name="student-guardian-detail",
    ),
]