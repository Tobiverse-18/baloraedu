from django.urls import path

from apps.staff.views import (
    StaffDepartmentListCreateView,
    StaffDepartmentDetailView,
)

urlpatterns = [
    path(
        "departments/",
        StaffDepartmentListCreateView.as_view(),
        name="staff-department-list-create",
    ),
    path(
        "departments/<uuid:department_id>/",
        StaffDepartmentDetailView.as_view(),
        name="staff-department-detail",
    ),
]