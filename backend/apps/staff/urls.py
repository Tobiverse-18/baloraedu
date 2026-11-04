from django.urls import path

from apps.staff.views import (
    StaffDepartmentListCreateView,
    StaffDepartmentDetailView,
    StaffProfileListCreateView,
    StaffProfileDetailView,
)


urlpatterns = [
    # Staff departments
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

    # Staff profiles
    path(
        "profiles/",
        StaffProfileListCreateView.as_view(),
        name="staff-profile-list-create",
    ),
    path(
        "profiles/<uuid:staff_id>/",
        StaffProfileDetailView.as_view(),
        name="staff-profile-detail",
    ),
]