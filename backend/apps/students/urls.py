
from django.urls import path

from apps.students.views import (
    StudentListCreateView,
    StudentDetailView,
)

urlpatterns = [
    path(
        "",
        StudentListCreateView.as_view(),
        name="student-list-create",
    ),
    path(
        "<uuid:student_id>/",
        StudentDetailView.as_view(),
        name="student-detail",
    ),
]
