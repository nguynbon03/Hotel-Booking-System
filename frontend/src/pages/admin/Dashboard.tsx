import React from 'react';
import { useQuery } from 'react-query';
import {
  UsersIcon,
  BuildingOfficeIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import Card from '@/components/ui/Card';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const AdminDashboard: React.FC = () => {
  // Fetch dashboard data
  const { data: analytics, isLoading } = useQuery(
    'admin-analytics',
    () => apiClient.getAdminAnalytics(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const { data: users } = useQuery('admin-users', () => apiClient.getUsers());
  const { data: organizations } = useQuery('admin-organizations', () => apiClient.getOrganizations());
  const { data: properties } = useQuery('admin-properties', () => apiClient.getProperties());
  const { data: bookings } = useQuery('admin-bookings', () => apiClient.getBookings());

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Mock data for charts (replace with real data from API)
  const revenueData = [
    { name: 'Jan', revenue: 12000, bookings: 45 },
    { name: 'Feb', revenue: 15000, bookings: 52 },
    { name: 'Mar', revenue: 18000, bookings: 61 },
    { name: 'Apr', revenue: 22000, bookings: 73 },
    { name: 'May', revenue: 25000, bookings: 84 },
    { name: 'Jun', revenue: 28000, bookings: 92 },
  ];

  const organizationData = [
    { name: 'Free', value: 45, color: '#94a3b8' },
    { name: 'Basic', value: 30, color: '#3b82f6' },
    { name: 'Professional', value: 20, color: '#10b981' },
    { name: 'Enterprise', value: 5, color: '#f59e0b' },
  ];

  const stats = [
    {
      name: 'Total Users',
      value: users?.length || 0,
      change: '+12%',
      changeType: 'increase' as const,
      icon: UsersIcon,
      color: 'blue' as const,
    },
    {
      name: 'Organizations',
      value: organizations?.length || 0,
      change: '+8%',
      changeType: 'increase' as const,
      icon: BuildingOfficeIcon,
      color: 'green' as const,
    },
    {
      name: 'Total Bookings',
      value: bookings?.length || 0,
      change: '+23%',
      changeType: 'increase' as const,
      icon: CalendarDaysIcon,
      color: 'purple' as const,
    },
    {
      name: 'Revenue',
      value: '$' + (analytics?.total_revenue_today || 0).toLocaleString(),
      change: '-2%',
      changeType: 'decrease' as const,
      icon: CurrencyDollarIcon,
      color: 'yellow' as const,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-2 text-lg text-gray-600">
          Overview of your hotel booking platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.name} className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`p-3 rounded-lg bg-${stat.color}-100`}>
                    <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                </div>
              </div>
              <div className="mt-4 flex items-center">
                {stat.changeType === 'increase' ? (
                  <ArrowUpIcon className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4 text-red-500" />
                )}
                <span
                  className={`ml-1 text-sm font-medium ${
                    stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {stat.change}
                </span>
                <span className="ml-1 text-sm text-gray-500">from last month</span>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Revenue Trend</h3>
            <p className="text-sm text-gray-600">Monthly revenue and bookings</p>
          </Card.Header>
          <Card.Body>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card.Body>
        </Card>

        {/* Organization Distribution */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Subscription Plans</h3>
            <p className="text-sm text-gray-600">Organization distribution by plan</p>
          </Card.Header>
          <Card.Body>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={organizationData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {organizationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Organizations */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Recent Organizations</h3>
            <p className="text-sm text-gray-600">Newly registered organizations</p>
          </Card.Header>
          <Card.Body>
            <div className="space-y-4">
              {organizations?.slice(0, 5).map((org: any) => (
                <div key={org.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <BuildingOfficeIcon className="h-5 w-5 text-primary-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{org.name}</p>
                      <p className="text-xs text-gray-500 capitalize">
                        {org.subscription_plan.toLowerCase()} plan
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">
                      {new Date(org.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>

        {/* Recent Bookings */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Recent Bookings</h3>
            <p className="text-sm text-gray-600">Latest booking activity</p>
          </Card.Header>
          <Card.Body>
            <div className="space-y-4">
              {bookings?.slice(0, 5).map((booking: any) => (
                <div key={booking.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <CalendarDaysIcon className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">
                        Booking #{booking.id.slice(0, 8)}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">
                        Status: {booking.status.toLowerCase()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      ${booking.total_amount}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(booking.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
