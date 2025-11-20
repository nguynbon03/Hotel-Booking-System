import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Transition } from '@headlessui/react';
import {
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  CogIcon,
  HeartIcon,
  ClockIcon,
  Bars3Icon,
  XMarkIcon,
  PhoneIcon
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/stores/authStore';
import { clsx } from 'clsx';
import CustomerService from '@/components/ui/CustomerService';

interface PublicHeaderProps {
  transparent?: boolean;
}

const PublicHeader: React.FC<PublicHeaderProps> = ({ transparent = false }) => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [customerServiceOpen, setCustomerServiceOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  const handleDashboardClick = () => {
    if (user?.role === 'ADMIN') {
      navigate('/admin/dashboard');
    } else if (user?.role === 'STAFF') {
      navigate('/staff/dashboard');
    } else {
      navigate('/profile');
    }
  };

  return (
    <header className={clsx(
      'border-b transition-all duration-200',
      transparent 
        ? 'bg-white/90 backdrop-blur-sm shadow-sm' 
        : 'bg-white shadow-sm'
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button
              onClick={() => navigate('/')}
              className="text-2xl font-bold text-primary-600 hover:text-primary-700 transition-colors"
            >
              Grand Palace Hotel
            </button>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <button
              onClick={() => navigate('/rooms')}
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Rooms
            </button>
            <button
              onClick={() => navigate('/about')}
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              About
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Contact
            </button>
            <button
              onClick={() => setCustomerServiceOpen(true)}
              className="flex items-center text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              <PhoneIcon className="w-4 h-4 mr-1" />
              Support
            </button>
          </div>

          {/* Auth Section */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <>
                {/* User Menu */}
                <Menu as="div" className="relative">
                  <Menu.Button className="flex items-center space-x-3 p-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors">
                    <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-medium text-sm">
                        {user.full_name?.charAt(0)?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div className="hidden md:block text-left">
                      <p className="text-sm font-medium text-gray-900">
                        {user.full_name || 'User'}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">
                        {user.role?.toLowerCase() || 'guest'}
                      </p>
                    </div>
                  </Menu.Button>

                  <Transition
                    enter="transition ease-out duration-100"
                    enterFrom="transform opacity-0 scale-95"
                    enterTo="transform opacity-100 scale-100"
                    leave="transition ease-in duration-75"
                    leaveFrom="transform opacity-100 scale-100"
                    leaveTo="transform opacity-0 scale-95"
                  >
                    <Menu.Items className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                      <div className="p-4 border-b border-gray-200">
                        <p className="text-sm font-medium text-gray-900">
                          {user.full_name}
                        </p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800 mt-2 capitalize">
                          {user.role.toLowerCase()}
                        </span>
                      </div>

                      <div className="py-2">
                        <Menu.Item>
                          {({ active }) => (
                            <button
                              onClick={handleProfileClick}
                              className={clsx(
                                'flex items-center w-full px-4 py-2 text-sm text-gray-700',
                                active && 'bg-gray-100'
                              )}
                            >
                              <UserCircleIcon className="h-4 w-4 mr-3" />
                              My Profile
                            </button>
                          )}
                        </Menu.Item>

                        {user.role === 'CUSTOMER' && (
                          <>
                            <Menu.Item>
                              {({ active }) => (
                                <button
                                  onClick={() => navigate('/my-bookings')}
                                  className={clsx(
                                    'flex items-center w-full px-4 py-2 text-sm text-gray-700',
                                    active && 'bg-gray-100'
                                  )}
                                >
                                  <ClockIcon className="h-4 w-4 mr-3" />
                                  My Bookings
                                </button>
                              )}
                            </Menu.Item>

                            <Menu.Item>
                              {({ active }) => (
                                <button
                                  onClick={() => navigate('/favorites')}
                                  className={clsx(
                                    'flex items-center w-full px-4 py-2 text-sm text-gray-700',
                                    active && 'bg-gray-100'
                                  )}
                                >
                                  <HeartIcon className="h-4 w-4 mr-3" />
                                  Favorites
                                </button>
                              )}
                            </Menu.Item>
                          </>
                        )}

                        {(user.role === 'ADMIN' || user.role === 'STAFF') && (
                          <Menu.Item>
                            {({ active }) => (
                              <button
                                onClick={handleDashboardClick}
                                className={clsx(
                                  'flex items-center w-full px-4 py-2 text-sm text-gray-700',
                                  active && 'bg-gray-100'
                                )}
                              >
                                <CogIcon className="h-4 w-4 mr-3" />
                                Dashboard
                              </button>
                            )}
                          </Menu.Item>
                        )}

                        <div className="border-t border-gray-200 my-2" />

                        <Menu.Item>
                          {({ active }) => (
                            <button
                              onClick={handleLogout}
                              className={clsx(
                                'flex items-center w-full px-4 py-2 text-sm text-red-700',
                                active && 'bg-red-50'
                              )}
                            >
                              <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                              Sign out
                            </button>
                          )}
                        </Menu.Item>
                      </div>
                    </Menu.Items>
                  </Transition>
                </Menu>
              </>
            ) : (
              <>
                {/* Guest Auth Buttons */}
                <button
                  onClick={() => navigate('/auth/login')}
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={() => navigate('/auth/register')}
                  className="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
                >
                  Sign Up
                </button>
              </>
            )}

            {/* Mobile menu button */}
            <button
              type="button"
              className="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        <Transition
          show={mobileMenuOpen}
          enter="transition ease-out duration-100"
          enterFrom="transform opacity-0 scale-95"
          enterTo="transform opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="transform opacity-100 scale-100"
          leaveTo="transform opacity-0 scale-95"
        >
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
              <button
                onClick={() => {
                  navigate('/rooms');
                  setMobileMenuOpen(false);
                }}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 w-full text-left"
              >
                Rooms
              </button>
              <button
                onClick={() => {
                  navigate('/about');
                  setMobileMenuOpen(false);
                }}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 w-full text-left"
              >
                About
              </button>
              <button
                onClick={() => {
                  navigate('/contact');
                  setMobileMenuOpen(false);
                }}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 w-full text-left"
              >
                Contact
              </button>

              {!isAuthenticated && (
                <div className="pt-4 pb-3 border-t border-gray-200">
                  <button
                    onClick={() => {
                      navigate('/auth/login');
                      setMobileMenuOpen(false);
                    }}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 w-full text-left"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      navigate('/auth/register');
                      setMobileMenuOpen(false);
                    }}
                    className="block px-3 py-2 rounded-md text-base font-medium bg-primary-600 text-white hover:bg-primary-700 w-full text-left mt-2"
                  >
                    Sign Up
                  </button>
                </div>
              )}
            </div>
          </div>
        </Transition>
      </div>

      {/* Customer Service Modal */}
      <CustomerService 
        isOpen={customerServiceOpen} 
        onClose={() => setCustomerServiceOpen(false)} 
      />
    </header>
  );
};

export default PublicHeader;
