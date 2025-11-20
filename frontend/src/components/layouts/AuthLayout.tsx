import React from 'react';
import { Outlet } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

const AuthLayout: React.FC = () => {
  const { isAuthenticated, otpRequired } = useAuthStore();

  // Clear auth state when accessing auth pages
  React.useEffect(() => {
    if (isAuthenticated) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.clear();
      window.location.reload();
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      <div className="min-h-screen flex items-center justify-center py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-lg w-full space-y-6">
          {/* Logo */}
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg
                className="h-8 w-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
            </div>
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Hotel Booking Admin
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Manage your hotel booking system
            </p>
          </div>

          {/* Auth Form */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <Outlet />
          </div>

          {/* Footer */}
          <div className="text-center text-sm text-gray-500">
            <p>&copy; 2024 Hotel Booking System. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
