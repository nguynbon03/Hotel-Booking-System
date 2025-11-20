import React, { useState, useEffect } from 'react';
import {
  CalendarDaysIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  EyeIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../../lib/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';

interface Booking {
  id: string;
  guest_name: string;
  guest_email: string;
  guest_phone: string;
  room_number: string;
  check_in: string;
  check_out: string;
  guests: number;
  total_amount: number;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  special_requests?: string;
  created_at: string;
  payment_status: 'pending' | 'paid' | 'refunded';
}

const StaffDashboard: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    pendingBookings: 0,
    todayCheckIns: 0,
    todayCheckOuts: 0,
    totalRevenue: 0
  });
  const [selectedStatus, setSelectedStatus] = useState<string>('pending');

  useEffect(() => {
    loadBookings();
    loadStats();
  }, [selectedStatus]);

  const loadBookings = async () => {
    setLoading(true);
    try {
      // Mock data for now - replace with real API
      const mockBookings: Booking[] = [
        {
          id: '1',
          guest_name: 'Nguyen Trung Nguyen',
          guest_email: 'nguyentrungnguyen13@gmail.com',
          guest_phone: '+84 123 456 789',
          room_number: '001',
          check_in: '2025-11-20',
          check_out: '2025-11-21',
          guests: 2,
          total_amount: 138.60,
          status: 'pending',
          payment_status: 'paid',
          special_requests: 'Late check-in requested',
          created_at: '2025-11-18T10:30:00Z'
        },
        {
          id: '2',
          guest_name: 'John Smith',
          guest_email: 'john.smith@example.com',
          guest_phone: '+1 555 123 4567',
          room_number: '105',
          check_in: '2025-11-19',
          check_out: '2025-11-22',
          guests: 1,
          total_amount: 450.00,
          status: 'pending',
          payment_status: 'paid',
          created_at: '2025-11-18T09:15:00Z'
        },
        {
          id: '3',
          guest_name: 'Maria Garcia',
          guest_email: 'maria.garcia@example.com',
          guest_phone: '+34 612 345 678',
          room_number: '203',
          check_in: '2025-11-18',
          check_out: '2025-11-20',
          guests: 3,
          total_amount: 320.00,
          status: 'confirmed',
          payment_status: 'paid',
          special_requests: 'Extra towels needed',
          created_at: '2025-11-17T14:20:00Z'
        }
      ];

      // Filter by status
      const filteredBookings = selectedStatus === 'all' 
        ? mockBookings 
        : mockBookings.filter(booking => booking.status === selectedStatus);

      setBookings(filteredBookings);
    } catch (error) {
      console.error('Failed to load bookings:', error);
      toast.error('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      // Mock stats
      setStats({
        pendingBookings: 3,
        todayCheckIns: 5,
        todayCheckOuts: 2,
        totalRevenue: 2450.80
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleApproveBooking = async (bookingId: string) => {
    try {
      // API call to approve booking
      toast.success('Booking approved successfully');
      loadBookings();
    } catch (error) {
      toast.error('Failed to approve booking');
    }
  };

  const handleRejectBooking = async (bookingId: string) => {
    if (window.confirm('Are you sure you want to reject this booking?')) {
      try {
        // API call to reject booking
        toast.success('Booking rejected');
        loadBookings();
      } catch (error) {
        toast.error('Failed to reject booking');
      }
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pending Approval
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.pendingBookings}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CalendarDaysIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Today Check-ins
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.todayCheckIns}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Today Check-outs
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.todayCheckOuts}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Today Revenue
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${stats.totalRevenue.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bookings Management */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="sm:flex sm:items-center sm:justify-between mb-6">
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Booking Management
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Review and approve customer bookings
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="pending">Pending Approval</option>
                <option value="confirmed">Confirmed</option>
                <option value="cancelled">Cancelled</option>
                <option value="completed">Completed</option>
                <option value="all">All Bookings</option>
              </select>
            </div>
          </div>

          {/* Bookings List */}
          <div className="overflow-hidden">
            <div className="space-y-4">
              {bookings.map((booking) => (
                <div
                  key={booking.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <h4 className="text-lg font-medium text-gray-900">
                          {booking.guest_name}
                        </h4>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(booking.status)}`}>
                          {booking.status}
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          booking.payment_status === 'paid' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {booking.payment_status}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <p><span className="font-medium">Room:</span> {booking.room_number}</p>
                          <p><span className="font-medium">Guests:</span> {booking.guests}</p>
                        </div>
                        <div>
                          <p><span className="font-medium">Check-in:</span> {formatDate(booking.check_in)}</p>
                          <p><span className="font-medium">Check-out:</span> {formatDate(booking.check_out)}</p>
                        </div>
                        <div>
                          <p><span className="font-medium">Email:</span> {booking.guest_email}</p>
                          <p><span className="font-medium">Phone:</span> {booking.guest_phone}</p>
                        </div>
                      </div>

                      {booking.special_requests && (
                        <div className="mt-3 p-3 bg-blue-50 rounded-md">
                          <p className="text-sm text-blue-800">
                            <span className="font-medium">Special Requests:</span> {booking.special_requests}
                          </p>
                        </div>
                      )}

                      <div className="mt-3 flex items-center justify-between">
                        <div className="text-sm text-gray-500">
                          Booked on {formatDateTime(booking.created_at)}
                        </div>
                        <div className="text-lg font-semibold text-gray-900">
                          ${booking.total_amount.toFixed(2)}
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="ml-6 flex flex-col space-y-2">
                      {booking.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleApproveBooking(booking.id)}
                            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          >
                            <CheckIcon className="h-4 w-4 mr-1" />
                            Approve
                          </button>
                          <button
                            onClick={() => handleRejectBooking(booking.id)}
                            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          >
                            <XMarkIcon className="h-4 w-4 mr-1" />
                            Reject
                          </button>
                        </>
                      )}
                      <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        <EyeIcon className="h-4 w-4 mr-1" />
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {bookings.length === 0 && (
              <div className="text-center py-12">
                <CalendarDaysIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No bookings</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No bookings found for the selected status.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffDashboard;
