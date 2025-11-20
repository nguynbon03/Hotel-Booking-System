import React from 'react';
import Card from '@/components/ui/Card';

const OrganizationSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Organization Settings</h1>
      <Card><Card.Body><p>Organization settings and configuration</p></Card.Body></Card>
    </div>
  );
};

export default OrganizationSettings;
