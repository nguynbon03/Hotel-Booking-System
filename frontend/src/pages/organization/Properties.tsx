import React from 'react';
import Card from '@/components/ui/Card';

const OrganizationProperties: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">My Properties</h1>
      <Card><Card.Body><p>Organization properties management</p></Card.Body></Card>
    </div>
  );
};

export default OrganizationProperties;
