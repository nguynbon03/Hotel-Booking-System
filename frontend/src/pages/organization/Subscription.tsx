import React, { useState, useEffect } from 'react';
import { 
  CreditCardIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Card from '@/components/ui/Card';

interface SubscriptionPlan {
  name: string;
  display_name: string;
  price: number;
  currency: string;
  billing_cycles: string[];
  features: {
    properties_limit: number | string;
    users_limit: number | string;
    bookings_limit: number | string;
    features: string[];
  };
  description: string;
  popular: boolean;
}

interface CurrentSubscription {
  id: string;
  plan_name: string;
  status: string;
  billing_cycle: string;
  base_price: number;
  currency: string;
  trial_start: string;
  trial_end: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  cancelled_at: string;
  limits: {
    properties: number;
    users: number;
    bookings: number;
  };
}

interface UsageStats {
  properties: {
    used: number;
    limit: number;
    available: number;
    percentage: number;
  };
  users: {
    used: number;
    limit: number;
    available: number;
    percentage: number;
  };
  bookings: {
    used: number;
    limit: number;
    available: number;
    percentage: number;
  };
}

interface Invoice {
  id: string;
  invoice_number: string;
  status: string;
  total_amount: number;
  currency: string;
  issue_date: string;
  due_date: string;
  paid_date: string;
  period_start: string;
  period_end: string;
}

const Subscription = () => {
  const [currentSubscription, setCurrentSubscription] = useState<CurrentSubscription | null>(null);
  const [availablePlans, setAvailablePlans] = useState<SubscriptionPlan[]>([]);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string>('');
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    setLoading(true);
    try {
      const [plansResponse, subscriptionResponse, usageResponse, invoicesResponse] = await Promise.all([
        apiClient.getSubscriptionPlans(),
        apiClient.getCurrentSubscription(),
        apiClient.getUsageStatistics(),
        apiClient.getInvoices({ limit: 10 })
      ]);

      setAvailablePlans(plansResponse.plans || []);
      setCurrentSubscription(subscriptionResponse.subscription || null);
      setUsageStats(usageResponse);
      setInvoices(invoicesResponse.invoices || []);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
      toast.error('Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async () => {
    if (!selectedPlan) return;

    setUpgrading(true);
    try {
      await apiClient.upgradeSubscription({
        new_plan_name: selectedPlan,
        billing_cycle: 'MONTHLY'
      });
      
      toast.success('Subscription upgraded successfully!');
      setShowUpgradeModal(false);
      loadSubscriptionData();
    } catch (error) {
      console.error('Upgrade failed:', error);
      toast.error('Failed to upgrade subscription');
    } finally {
      setUpgrading(false);
    }
  };

  const handleCancelSubscription = async () => {
    try {
      await apiClient.cancelSubscription({
        cancel_at_period_end: true,
        reason: 'User requested cancellation'
      });
      
      toast.success('Subscription will be cancelled at the end of the current period');
      setShowCancelModal(false);
      loadSubscriptionData();
    } catch (error) {
      console.error('Cancellation failed:', error);
      toast.error('Failed to cancel subscription');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'trial': return 'text-blue-600 bg-blue-100';
      case 'past_due': return 'text-red-600 bg-red-100';
      case 'cancelled': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Subscription & Billing</h1>
          <p className="text-gray-600">Manage your subscription plan and billing information</p>
        </div>
      </div>

      {/* Current Subscription */}
      {currentSubscription && (
        <Card>
          <div className="p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Current Plan</h2>
                <div className="flex items-center space-x-3">
                  <span className="text-2xl font-bold text-primary-600">
                    {currentSubscription.plan_name}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(currentSubscription.status)}`}>
                    {currentSubscription.status}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">
                  ${currentSubscription.base_price}
                </div>
                <div className="text-sm text-gray-600">
                  per {currentSubscription.billing_cycle.toLowerCase()}
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Billing Period</h3>
                <div className="text-sm text-gray-600">
                  <div className="flex items-center mb-1">
                    <CalendarDaysIcon className="w-4 h-4 mr-2" />
                    {new Date(currentSubscription.current_period_start).toLocaleDateString()} - 
                    {new Date(currentSubscription.current_period_end).toLocaleDateString()}
                  </div>
                  {currentSubscription.status === 'TRIAL' && currentSubscription.trial_end && (
                    <div className="flex items-center text-blue-600">
                      <ExclamationTriangleIcon className="w-4 h-4 mr-2" />
                      Trial ends: {new Date(currentSubscription.trial_end).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Plan Limits</h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <div className="flex items-center">
                    <BuildingOfficeIcon className="w-4 h-4 mr-2" />
                    {currentSubscription.limits.properties} Properties
                  </div>
                  <div className="flex items-center">
                    <UserGroupIcon className="w-4 h-4 mr-2" />
                    {currentSubscription.limits.users} Users
                  </div>
                  <div className="flex items-center">
                    <ClipboardDocumentListIcon className="w-4 h-4 mr-2" />
                    {currentSubscription.limits.bookings || 'Unlimited'} Bookings
                  </div>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowUpgradeModal(true)}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Upgrade Plan
              </button>
              {!currentSubscription.cancel_at_period_end && (
                <button
                  onClick={() => setShowCancelModal(true)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel Subscription
                </button>
              )}
            </div>

            {currentSubscription.cancel_at_period_end && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center text-yellow-800">
                  <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
                  <span className="font-medium">Subscription will be cancelled on {new Date(currentSubscription.current_period_end).toLocaleDateString()}</span>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Usage Statistics */}
      {usageStats && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Usage Statistics</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Properties</span>
                  <span className="text-sm text-gray-600">
                    {usageStats.properties.used} / {usageStats.properties.limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUsageColor(usageStats.properties.percentage)}`}
                    style={{ width: `${Math.min(usageStats.properties.percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {usageStats.properties.available} remaining
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Users</span>
                  <span className="text-sm text-gray-600">
                    {usageStats.users.used} / {usageStats.users.limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUsageColor(usageStats.users.percentage)}`}
                    style={{ width: `${Math.min(usageStats.users.percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {usageStats.users.available} remaining
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Bookings (This Period)</span>
                  <span className="text-sm text-gray-600">
                    {usageStats.bookings.used} / {usageStats.bookings.limit || '∞'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUsageColor(usageStats.bookings.percentage)}`}
                    style={{ width: `${Math.min(usageStats.bookings.percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {usageStats.bookings.available !== null ? `${usageStats.bookings.available} remaining` : 'Unlimited'}
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Recent Invoices */}
      {invoices.length > 0 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Invoices</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Invoice
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Period
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {invoice.invoice_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(invoice.period_start).toLocaleDateString()} - {new Date(invoice.period_end).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${invoice.total_amount.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(invoice.status)}`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(invoice.due_date).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      )}

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Choose Your Plan</h3>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                {availablePlans.map((plan) => (
                  <div
                    key={plan.name}
                    onClick={() => setSelectedPlan(plan.name)}
                    className={`border-2 rounded-lg p-6 cursor-pointer transition-colors ${
                      selectedPlan === plan.name
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${plan.popular ? 'ring-2 ring-primary-500' : ''}`}
                  >
                    {plan.popular && (
                      <div className="text-xs font-semibold text-primary-600 mb-2">MOST POPULAR</div>
                    )}
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">{plan.display_name}</h4>
                    <div className="text-3xl font-bold text-gray-900 mb-1">
                      ${plan.price}
                    </div>
                    <div className="text-sm text-gray-600 mb-4">per month</div>
                    <p className="text-sm text-gray-600 mb-4">{plan.description}</p>
                    
                    <div className="space-y-2">
                      <div className="text-sm">
                        <strong>{plan.features.properties_limit}</strong> Properties
                      </div>
                      <div className="text-sm">
                        <strong>{plan.features.users_limit}</strong> Users
                      </div>
                      <div className="text-sm">
                        <strong>{plan.features.bookings_limit}</strong> Bookings
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowUpgradeModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpgrade}
                  disabled={!selectedPlan || upgrading}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {upgrading ? 'Upgrading...' : 'Upgrade Plan'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cancel Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Cancel Subscription</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to cancel your subscription? You'll continue to have access until the end of your current billing period.
            </p>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowCancelModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Keep Subscription
              </button>
              <button
                onClick={handleCancelSubscription}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Cancel Subscription
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Subscription;
