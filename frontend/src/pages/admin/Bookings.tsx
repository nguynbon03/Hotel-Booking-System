import React from 'react';
import { useQuery } from 'react-query';
import { apiClient } from '@/lib/api';
import Card from '@/components/ui/Card';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const AdminBookings: React.FC = () => {
  const { data: bookings, isLoading } = useQuery('admin-bookings', () => 
    apiClient.getBookings()
  );

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" /></div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Bookings Management</h1>
      <Card>
        <Card.Body>
          <p>Bookings management interface - {bookings?.length || 0} bookings found</p>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AdminBookings;
