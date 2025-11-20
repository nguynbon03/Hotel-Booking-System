import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { MagnifyingGlassIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { Organization, SubscriptionPlan } from '@/types';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const AdminOrganizations: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [planFilter, setPlanFilter] = useState<string>('all');

  const { data: organizations, isLoading } = useQuery('admin-organizations', () => 
    apiClient.getOrganizations()
  );

  const filteredOrganizations = organizations?.filter((org: Organization) => {
    const matchesSearch = org.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPlan = planFilter === 'all' || org.subscription_plan === planFilter;
    return matchesSearch && matchesPlan;
  }) || [];

  const getPlanBadgeVariant = (plan: SubscriptionPlan) => {
    switch (plan) {
      case SubscriptionPlan.FREE: return 'gray';
      case SubscriptionPlan.BASIC: return 'info';
      case SubscriptionPlan.PROFESSIONAL: return 'success';
      case SubscriptionPlan.ENTERPRISE: return 'warning';
      default: return 'gray';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Organizations</h1>
        <p className="mt-1 text-sm text-gray-600">Manage all organizations in the platform</p>
      </div>

      {/* Filters */}
      <Card>
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search organizations..."
                className="form-input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select
              className="form-input"
              value={planFilter}
              onChange={(e) => setPlanFilter(e.target.value)}
            >
              <option value="all">All Plans</option>
              <option value={SubscriptionPlan.FREE}>Free</option>
              <option value={SubscriptionPlan.BASIC}>Basic</option>
              <option value={SubscriptionPlan.PROFESSIONAL}>Professional</option>
              <option value={SubscriptionPlan.ENTERPRISE}>Enterprise</option>
            </select>
          </div>
        </Card.Body>
      </Card>

      {/* Organizations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredOrganizations.map((org: Organization) => (
          <Card key={org.id}>
            <Card.Body>
              <div className="flex items-center justify-between mb-4">
                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <BuildingOfficeIcon className="h-6 w-6 text-primary-600" />
                </div>
                <Badge variant={getPlanBadgeVariant(org.subscription_plan)}>
                  {org.subscription_plan}
                </Badge>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{org.name}</h3>
              <p className="text-sm text-gray-600 mb-4">{org.description || 'No description'}</p>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Properties:</span>
                  <span className="font-medium">{org.max_properties}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Users:</span>
                  <span className="font-medium">{org.max_users}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Status:</span>
                  <Badge variant={org.is_active ? 'success' : 'danger'}>
                    {org.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Created:</span>
                  <span className="font-medium">
                    {new Date(org.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </Card.Body>
          </Card>
        ))}
      </div>

      {filteredOrganizations.length === 0 && (
        <Card>
          <Card.Body>
            <div className="text-center py-12">
              <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-900">No organizations found</p>
              <p className="text-sm text-gray-500">Try adjusting your search criteria</p>
            </div>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default AdminOrganizations;
