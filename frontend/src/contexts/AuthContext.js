import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // To check initial auth status

  useEffect(() => {
    // Check if user is already logged in (e.g., token exists in localStorage)
    const checkLoggedIn = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          // Validate token by fetching user data
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Token might be invalid or expired
          apiLogout(); // Clear invalid token
          setUser(null);
        }
      }
      setLoading(false);
    };

    checkLoggedIn();
  }, []);

  const login = async (email, password) => {
    try {
      await apiLogin(email, password);
      // After successful login, fetch user data
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      return currentUser; // Return user data on successful login
    } catch (error) {
      setUser(null);
      throw error; // Re-throw error to be handled by the login form
    }
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
  };

  // Don't render children until loading is false to prevent flicker
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

