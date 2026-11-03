import api from './api';
import tokenStorage from './tokenStorage';

const authService = {
  async register(userData) {
    const response = await api.post(
      '/accounts/register/',
      userData
    );

    return response.data;
  },

  async login(credentials) {
    const response = await api.post(
      '/accounts/login/',
      credentials
    );

    tokenStorage.setTokens(response.data);

    return response.data;
  },

  async getProfile() {
    const response = await api.get('/accounts/me/');

    return response.data;
  },

  async requestPasswordReset(email) {
    const response = await api.post(
      '/accounts/password-reset/',
      { email }
    );

    return response.data;
  },

  async confirmPasswordReset(resetData) {
    const response = await api.post(
      '/accounts/password-reset/confirm/',
      resetData
    );

    return response.data;
  },

  async logout() {
    const refreshToken = tokenStorage.getRefreshToken();

    try {
      if (refreshToken) {
        await api.post('/accounts/logout/', {
          refresh: refreshToken,
        });
      }
    } finally {
      tokenStorage.clearTokens();
    }
  },
};

export default authService;