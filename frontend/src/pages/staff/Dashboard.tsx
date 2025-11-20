import React from 'react';
import Card from '@/components/ui/Card';

const StaffDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Staff Dashboard</h1>
      <Card>
        <Card.Body>
          <p>Staff dashboard for customer service operations</p>
        </Card.Body>
      </Card>
    </div>
  );
};

export default StaffDashboard;
