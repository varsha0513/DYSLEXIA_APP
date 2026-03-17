import React, { createContext, useContext, useEffect, ReactNode, useState } from 'react';
import { User, AuthAPI } from '../utils/authAPI';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, age: number, password: string, passwordConfirm: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing session on mount
  useEffect(() => {
    const storedToken = AuthAPI.getToken();
    const storedUser = AuthAPI.getUser();

    if (storedToken && storedUser) {
      // Verify token is still valid
      AuthAPI.validateToken(storedToken)
        .then(isValid => {
          if (isValid) {
            setToken(storedToken);
            setUser(storedUser);
          } else {
            // Token expired
            AuthAPI.logout();
          }
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await AuthAPI.login({ email, password });

      // Save token and user
      AuthAPI.saveToken(response.access_token);
      AuthAPI.saveUser(response.user);

      setToken(response.access_token);
      setUser(response.user);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (name: string, email: string, age: number, password: string, passwordConfirm: string) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await AuthAPI.signup({
        name,
        email,
        age,
        password,
        password_confirm: passwordConfirm,
      });

      // Save token and user
      AuthAPI.saveToken(response.access_token);
      AuthAPI.saveUser(response.user);

      setToken(response.access_token);
      setUser(response.user);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Signup failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    AuthAPI.logout();
    setToken(null);
    setUser(null);
    setError(null);
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated: !!token && !!user,
    error,
    login,
    signup,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
