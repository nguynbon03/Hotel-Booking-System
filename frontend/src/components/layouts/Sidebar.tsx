import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  HomeIcon,
  UsersIcon,
  BuildingOfficeIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  CogIcon,
  UserGroupIcon,
  PhoneIcon,
  DocumentTextIcon,
  ArrowRightOnRectangleIcon,
  CreditCardIcon,
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/stores/authStore';
import { MenuItem } from '@/types';

interface SidebarProps {
  userType: 'admin' | 'staff' | 'organization';
  open: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ userType, open, onClose }) => {
  const location = useLocation();
  const { user, currentOrganization, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Define menu items based on user type
  const getMenuItems = (): MenuItem[] => {
    switch (userType) {
      case 'admin':
        return [
          {
            id: 'dashboard',
            label: 'Dashboard',
            icon: HomeIcon,
            path: '/admin/dashboard',
          },
          {
            id: 'users',
            label: 'Users',
            icon: UsersIcon,
            path: '/admin/users',
          },
          {
            id: 'organizations',
            label: 'Organizations',
            icon: BuildingOfficeIcon,
            path: '/admin/organizations',
          },
          {
            id: 'properties',
            label: 'Properties',
            icon: BuildingOfficeIcon,
            path: '/admin/properties',
          },
          {
            id: 'bookings',
            label: 'Bookings',
            icon: CalendarDaysIcon,
            path: '/admin/bookings',
          },
          {
            id: 'analytics',
            label: 'Analytics',
            icon: ChartBarIcon,
            path: '/admin/analytics',
          },
        ];

      case 'staff':
        return [
          {
            id: 'dashboard',
            label: 'Dashboard',
            icon: HomeIcon,
            path: '/staff/dashboard',
          },
          {
            id: 'bookings',
            label: 'Bookings',
            icon: CalendarDaysIcon,
            path: '/staff/bookings',
          },
          {
            id: 'customers',
            label: 'Customers',
            icon: PhoneIcon,
            path: '/staff/customers',
          },
        ];

      case 'organization':
        return [
          {
            id: 'dashboard',
            label: 'Dashboard',
            icon: HomeIcon,
            path: '/organization/dashboard',
          },
          {
            id: 'properties',
            label: 'Properties',
            icon: BuildingOfficeIcon,
            path: '/organization/properties',
          },
          {
            id: 'bookings',
            label: 'Bookings',
            icon: CalendarDaysIcon,
            path: '/organization/bookings',
          },
          {
            id: 'members',
            label: 'Team Members',
            icon: UserGroupIcon,
            path: '/organization/members',
          },
          {
            id: 'subscription',
            label: 'Subscription',
            icon: CreditCardIcon,
            path: '/organization/subscription',
          },
          {
            id: 'settings',
            label: 'Settings',
            icon: CogIcon,
            path: '/organization/settings',
          },
        ];

      default:
        return [];
    }
  };

  const menuItems = getMenuItems();

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onClose}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 bg-primary-600">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-white rounded-lg flex items-center justify-center">
                <svg
                  className="h-5 w-5 text-primary-600"
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
              <span className="ml-2 text-white font-semibold text-lg">
                Hotel Admin
              </span>
            </div>
          </div>

          {/* Organization Info (for organization users) */}
          {userType === 'organization' && currentOrganization && (
            <div className="px-4 py-3 bg-gray-50 border-b">
              <div className="text-sm font-medium text-gray-900 truncate">
                {currentOrganization.name}
              </div>
              <div className="text-xs text-gray-500 capitalize">
                {currentOrganization.subscription_plan.toLowerCase()} Plan
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={clsx(
                    'sidebar-link',
                    isActive && 'active'
                  )}
                  onClick={onClose}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  <span className="font-medium">{item.label}</span>
                  {item.badge && (
                    <span className="ml-auto bg-primary-100 text-primary-600 text-xs px-2 py-1 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>

          {/* User Info & Logout */}
          <div className="px-4 py-4 border-t border-gray-200 space-y-3">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.full_name?.charAt(0)?.toUpperCase() || 'A'}
                </span>
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <div className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name || 'Administrator'}
                </div>
                <div className="text-xs text-gray-500 capitalize">
                  {user?.role?.toLowerCase() || 'admin'}
                </div>
              </div>
            </div>
            
            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
            >
              <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
              Sign out
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
