import AuthContext from './AuthContext.js';
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import authService from '../services/authService';
import tokenStorage from '../services/tokenStorage';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = useCallback(async (credentials) => {
    const data = await authService.login(credentials);

    setUser(data.user);

    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      tokenStorage.clearTokens();
      setUser(null);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    const profile = await authService.getProfile();

    setUser(profile);

    return profile;
  }, []);

  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      if (
        !tokenStorage.getAccessToken() &&
        !tokenStorage.getRefreshToken()
      ) {
        setLoading(false);
        return;
      }

      try {
        const profile = await authService.getProfile();

        if (mounted) {
          setUser(profile);
        }
      } catch {
        tokenStorage.clearTokens();

        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    initializeAuth();

    return () => {
      mounted = false;
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      refreshUser,
    }),
    [user, loading, login, logout, refreshUser]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}