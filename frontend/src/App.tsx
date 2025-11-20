import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

// Layout Components
import AuthLayout from '@/components/layouts/AuthLayout';
import DashboardLayout from '@/components/layouts/DashboardLayout';

// Public Pages
import LandingPage from '@/pages/LandingPage';
import RoomsPage from '@/pages/RoomsPage';
import RoomDetails from '@/pages/RoomDetails';
import BookingPage from '@/pages/BookingPage';
import SearchResults from '@/pages/SearchResults';
import PropertyDetails from '@/pages/PropertyDetails';
import MyBookings from '@/pages/MyBookings';
import Favorites from '@/pages/Favorites';
import Profile from '@/pages/Profile';
import TestAuth from '@/pages/TestAuth';

// Auth Pages
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import OtpPage from '@/pages/auth/OtpPage';

// Admin Pages
import AdminDashboard from '@/pages/admin/Dashboard';
import AdminUsers from '@/pages/admin/Users';
import AdminOrganizations from '@/pages/admin/Organizations';
import AdminProperties from '@/pages/admin/Properties';
import AdminBookings from '@/pages/admin/Bookings';
import AdminAnalytics from '@/pages/admin/Analytics';

// Staff Pages
import StaffDashboard from '@/pages/staff/Dashboard';
import StaffBookings from '@/pages/staff/Bookings';
import StaffCustomers from '@/pages/staff/Customers';

// Organization Pages
import OrganizationDashboard from '@/pages/organization/Dashboard';
import OrganizationProperties from '@/pages/organization/Properties';
import OrganizationBookings from '@/pages/organization/Bookings';
import OrganizationMembers from '@/pages/organization/Members';
import OrganizationSettings from '@/pages/organization/Settings';
import OrganizationSubscription from '@/pages/organization/Subscription';

// Route Guards
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import RoleGuard from '@/components/auth/RoleGuard';

function App() {
  const { isAuthenticated, getCurrentUser, otpRequired } = useAuthStore();

  useEffect(() => {
    console.log('🚀 App mounted, isAuthenticated:', isAuthenticated);
    // Initialize auth state on app load
    if (!isAuthenticated && localStorage.getItem('access_token')) {
      getCurrentUser();
    }
  }, [isAuthenticated, getCurrentUser]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* ============================================================ */}
        {/* 🏠 Public Routes */}
        {/* ============================================================ */}
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/rooms" element={<RoomsPage />} />
          <Route path="/room/:roomId" element={<RoomDetails />} />
          <Route path="/booking" element={<BookingPage />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/property/:propertyId" element={<PropertyDetails />} />
        <Route path="/my-bookings" element={
          <ProtectedRoute>
            <MyBookings />
          </ProtectedRoute>
        } />
        <Route path="/favorites" element={
          <ProtectedRoute>
            <Favorites />
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        } />
        <Route path="/test-auth" element={<TestAuth />} />
        
        {/* ============================================================ */}
        {/* 🔐 Authentication Routes */}
        {/* ============================================================ */}
        <Route path="/auth" element={<AuthLayout />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="otp" element={<OtpPage />} />
        </Route>

        {/* ============================================================ */}
        {/* 👑 Admin Routes */}
        {/* ============================================================ */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <RoleGuard allowedRoles={['ADMIN']}>
                <DashboardLayout userType="admin" />
              </RoleGuard>
            </ProtectedRoute>
          }
        >
          <Route index element={<AdminDashboard />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="organizations" element={<AdminOrganizations />} />
          <Route path="properties" element={<AdminProperties />} />
          <Route path="bookings" element={<AdminBookings />} />
          <Route path="analytics" element={<AdminAnalytics />} />
        </Route>

        {/* ============================================================ */}
        {/* 👥 Staff Routes */}
        {/* ============================================================ */}
        <Route
          path="/staff"
          element={
            <ProtectedRoute>
              <RoleGuard allowedRoles={['STAFF', 'ADMIN']}>
                <DashboardLayout userType="staff" />
              </RoleGuard>
            </ProtectedRoute>
          }
        >
          <Route index element={<StaffDashboard />} />
          <Route path="dashboard" element={<StaffDashboard />} />
          <Route path="bookings" element={<StaffBookings />} />
          <Route path="customers" element={<StaffCustomers />} />
        </Route>

        {/* ============================================================ */}
        {/* 🏢 Organization Routes */}
        {/* ============================================================ */}
        <Route
          path="/organization"
          element={
            <ProtectedRoute>
              <DashboardLayout userType="organization" />
            </ProtectedRoute>
          }
        >
          <Route index element={<OrganizationDashboard />} />
          <Route path="dashboard" element={<OrganizationDashboard />} />
          <Route path="properties" element={<OrganizationProperties />} />
          <Route path="bookings" element={<OrganizationBookings />} />
          <Route path="members" element={<OrganizationMembers />} />
          <Route path="subscription" element={<OrganizationSubscription />} />
          <Route path="settings" element={<OrganizationSettings />} />
        </Route>

        {/* ============================================================ */}
        {/* 🔄 Route Redirects */}
        {/* ============================================================ */}
        <Route
          path="/"
          element={
            <Navigate
              to={
                !isAuthenticated
                  ? '/landing'
                  : otpRequired
                  ? '/auth/otp'
                  : '/dashboard'
              }
              replace
            />
          }
        />

        <Route
          path="/login"
          element={<Navigate to="/auth/login" replace />}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardRedirect />
            </ProtectedRoute>
          }
        />

        {/* ============================================================ */}
        {/* 404 Fallback */}
        {/* ============================================================ */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

// ============================================================
// 🔄 Dashboard Redirect Component
// ============================================================
function DashboardRedirect() {
  const { user } = useAuthStore();

  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }

  // Redirect based on user role
  switch (user.role) {
    case 'ADMIN':
      return <Navigate to="/admin/dashboard" replace />;
    case 'STAFF':
      return <Navigate to="/staff/dashboard" replace />;
    case 'CUSTOMER':
      // Customer should not access admin/staff dashboards
      return <Navigate to="/landing" replace />;
    default:
      return <Navigate to="/landing" replace />;
  }
}

export default App;
