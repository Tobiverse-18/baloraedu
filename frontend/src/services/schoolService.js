import api from './api';

const schoolService = {
  async registerSchool(schoolData) {
    const response = await api.post(
      '/schools/register/',
      schoolData
    );

    return response.data;
  },

  async getMySchools() {
    const response = await api.get(
      '/schools/my-schools/'
    );

    return response.data;
  },

  async getWorkspace(schoolId) {
    const response = await api.get(
      `/schools/${schoolId}/workspace/`
    );

    return response.data;
  },

  async getMemberPermissions(schoolId, membershipId) {
    const response = await api.get(
      `/schools/${schoolId}/members/${membershipId}/permissions/`
    );

    return response.data;
  },

  async updateMemberPermission(
    schoolId,
    membershipId,
    permission,
    isGranted
  ) {
    const response = await api.post(
      `/schools/${schoolId}/members/${membershipId}/permissions/`,
      {
        permission,
        is_granted: isGranted,
      }
    );

    return response.data;
  },

  async removeMemberPermission(
    schoolId,
    membershipId,
    permission
  ) {
    const response = await api.delete(
      `/schools/${schoolId}/members/${membershipId}/permissions/${permission}/`
    );

    return response.data;
  },
};

export default schoolService;