import React from 'react';
import Card from '@/components/ui/Card';

const OrganizationDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Organization Dashboard</h1>
      <Card>
        <Card.Body>
          <p>Organization dashboard for hotel management</p>
        </Card.Body>
      </Card>
    </div>
  );
};

export default OrganizationDashboard;
