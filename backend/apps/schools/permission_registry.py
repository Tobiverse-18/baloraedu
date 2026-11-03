
# Central registry of all valid school feature permissions.
# This file must remain independent of Django models.


class SchoolPermissions:
    SCHOOL_VIEW_SETTINGS = "school.view_settings"
    SCHOOL_MANAGE_SETTINGS = "school.manage_settings"

    STAFF_VIEW = "staff.view"
    STAFF_MANAGE = "staff.manage"

    STUDENTS_VIEW = "students.view"
    STUDENTS_MANAGE = "students.manage"

    GUARDIANS_VIEW = "guardians.view"
    GUARDIANS_MANAGE = "guardians.manage"

    ATTENDANCE_VIEW = "attendance.view"
    ATTENDANCE_MANAGE = "attendance.manage"

    EXAMS_VIEW = "exams.view"
    EXAMS_MANAGE = "exams.manage"

    FEES_VIEW = "fees.view"
    FEES_MANAGE = "fees.manage"

    ACCOUNTING_VIEW = "accounting.view"
    ACCOUNTING_MANAGE = "accounting.manage"

    TIMETABLES_VIEW = "timetables.view"
    TIMETABLES_MANAGE = "timetables.manage"

    SUBSCRIPTION_MANAGE = "subscription.manage"


# All registered permission values.
ALL_SCHOOL_PERMISSIONS = frozenset({
    value
    for name, value in vars(SchoolPermissions).items()
    if name.isupper() and isinstance(value, str)
})


# Choices suitable for Django model fields.
SCHOOL_PERMISSION_CHOICES = [
    (
        permission,
        permission.replace(".", " ").replace("_", " ").title(),
    )
    for permission in sorted(ALL_SCHOOL_PERMISSIONS)
]


# Set of valid permission values for model validation.
SCHOOL_PERMISSION_CHOICES_VALUES = ALL_SCHOOL_PERMISSIONS
