
from .models import SchoolMembership
from .permission_registry import SchoolPermissions


# Default feature permissions assigned to each school role.
ROLE_PERMISSIONS = {

    SchoolMembership.Role.SCHOOL_OWNER: {
        SchoolPermissions.SCHOOL_VIEW_SETTINGS,
        SchoolPermissions.SCHOOL_MANAGE_SETTINGS,
        SchoolPermissions.STAFF_VIEW,
        SchoolPermissions.STAFF_MANAGE,
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.STUDENTS_MANAGE,
        SchoolPermissions.GUARDIANS_VIEW,
        SchoolPermissions.GUARDIANS_MANAGE,
        SchoolPermissions.ATTENDANCE_VIEW,
        SchoolPermissions.ATTENDANCE_MANAGE,
        SchoolPermissions.EXAMS_VIEW,
        SchoolPermissions.EXAMS_MANAGE,
        SchoolPermissions.FEES_VIEW,
        SchoolPermissions.FEES_MANAGE,
        SchoolPermissions.ACCOUNTING_VIEW,
        SchoolPermissions.ACCOUNTING_MANAGE,
        SchoolPermissions.TIMETABLES_VIEW,
        SchoolPermissions.TIMETABLES_MANAGE,
        SchoolPermissions.SUBSCRIPTION_MANAGE,
    },

    SchoolMembership.Role.SCHOOL_ADMIN: {
        SchoolPermissions.SCHOOL_VIEW_SETTINGS,
        SchoolPermissions.SCHOOL_MANAGE_SETTINGS,
        SchoolPermissions.STAFF_VIEW,
        SchoolPermissions.STAFF_MANAGE,
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.STUDENTS_MANAGE,
        SchoolPermissions.GUARDIANS_VIEW,
        SchoolPermissions.GUARDIANS_MANAGE,
        SchoolPermissions.ATTENDANCE_VIEW,
        SchoolPermissions.ATTENDANCE_MANAGE,
        SchoolPermissions.EXAMS_VIEW,
        SchoolPermissions.EXAMS_MANAGE,
        SchoolPermissions.FEES_VIEW,
        SchoolPermissions.FEES_MANAGE,
        SchoolPermissions.ACCOUNTING_VIEW,
        SchoolPermissions.ACCOUNTING_MANAGE,
        SchoolPermissions.TIMETABLES_VIEW,
        SchoolPermissions.TIMETABLES_MANAGE,
    },

    SchoolMembership.Role.PRINCIPAL: {
        SchoolPermissions.SCHOOL_VIEW_SETTINGS,
        SchoolPermissions.STAFF_VIEW,
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.STUDENTS_MANAGE,
        SchoolPermissions.GUARDIANS_VIEW,
        SchoolPermissions.GUARDIANS_MANAGE,
        SchoolPermissions.ATTENDANCE_VIEW,
        SchoolPermissions.ATTENDANCE_MANAGE,
        SchoolPermissions.EXAMS_VIEW,
        SchoolPermissions.EXAMS_MANAGE,
        SchoolPermissions.FEES_VIEW,
        SchoolPermissions.ACCOUNTING_VIEW,
        SchoolPermissions.TIMETABLES_VIEW,
        SchoolPermissions.TIMETABLES_MANAGE,
    },

    SchoolMembership.Role.ACCOUNTANT: {
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.GUARDIANS_VIEW,
        SchoolPermissions.FEES_VIEW,
        SchoolPermissions.FEES_MANAGE,
        SchoolPermissions.ACCOUNTING_VIEW,
        SchoolPermissions.ACCOUNTING_MANAGE,
    },

    SchoolMembership.Role.TEACHER: {
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.ATTENDANCE_VIEW,
        SchoolPermissions.ATTENDANCE_MANAGE,
        SchoolPermissions.EXAMS_VIEW,
        SchoolPermissions.EXAMS_MANAGE,
        SchoolPermissions.TIMETABLES_VIEW,
    },

    SchoolMembership.Role.PARENT: {
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.ATTENDANCE_VIEW,
        SchoolPermissions.EXAMS_VIEW,
        SchoolPermissions.FEES_VIEW,
        SchoolPermissions.TIMETABLES_VIEW,
    },

    SchoolMembership.Role.STUDENT: {
        SchoolPermissions.STUDENTS_VIEW,
        SchoolPermissions.ATTENDANCE_VIEW,
        SchoolPermissions.EXAMS_VIEW,
        SchoolPermissions.FEES_VIEW,
        SchoolPermissions.TIMETABLES_VIEW,
    },
}
