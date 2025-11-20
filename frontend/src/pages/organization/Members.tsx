import React from 'react';
import Card from '@/components/ui/Card';

const OrganizationMembers: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Team Members</h1>
      <Card><Card.Body><p>Organization team management</p></Card.Body></Card>
    </div>
  );
};

export default OrganizationMembers;
