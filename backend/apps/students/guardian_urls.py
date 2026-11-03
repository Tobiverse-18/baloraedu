
from django.urls import path

from apps.students.guardian_views import (
    GuardianListCreateView,
    GuardianDetailView,
)

urlpatterns = [
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
]
