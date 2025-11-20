import React from 'react';
import { useQuery } from 'react-query';
import { apiClient } from '@/lib/api';
import Card from '@/components/ui/Card';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const AdminProperties: React.FC = () => {
  const { data: properties, isLoading } = useQuery('admin-properties', () => 
    apiClient.getProperties()
  );

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" /></div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Properties Management</h1>
      <Card>
        <Card.Body>
          <p>Properties management interface - {properties?.length || 0} properties found</p>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AdminProperties;
