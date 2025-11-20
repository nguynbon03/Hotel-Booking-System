import React from 'react';
import Card from '@/components/ui/Card';

const AdminAnalytics: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics & Reports</h1>
      <Card>
        <Card.Body>
          <p>Advanced analytics and reporting interface</p>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AdminAnalytics;
