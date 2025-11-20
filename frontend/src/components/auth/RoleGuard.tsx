import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles: string[];
  fallbackPath?: string;
}

const RoleGuard: React.FC<RoleGuardProps> = ({ 
  children, 
  allowedRoles, 
  fallbackPath 
}) => {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  if (!user || !allowedRoles.includes(user.role)) {
    // Redirect based on user role if no fallback specified
    if (!fallbackPath) {
      if (user?.role === 'admin') {
        return <Navigate to="/admin" replace />;
      } else if (user?.role === 'staff') {
        return <Navigate to="/staff" replace />;
      } else if (user?.role === 'organization_owner') {
        return <Navigate to="/organization" replace />;
      } else {
        return <Navigate to="/" replace />;
      }
    }
    return <Navigate to={fallbackPath} replace />;
  }

  return <>{children}</>;
};

export default RoleGuard;
