import React, { useState } from 'react';
import { 
  PhoneIcon, 
  ChatBubbleLeftEllipsisIcon,
  EnvelopeIcon,
  XMarkIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface CustomerServiceProps {
  isOpen: boolean;
  onClose: () => void;
}

const CustomerService: React.FC<CustomerServiceProps> = ({ isOpen, onClose }) => {
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [cancelBookingForm, setCancelBookingForm] = useState({
    bookingId: '',
    reason: '',
    email: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleCancelBooking = async () => {
    if (!cancelBookingForm.bookingId || !cancelBookingForm.reason || !cancelBookingForm.email) {
      alert('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    try {
      // Simulate API call for booking cancellation
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSubmitSuccess(true);
      setTimeout(() => {
        setSubmitSuccess(false);
        setSelectedService(null);
        setCancelBookingForm({ bookingId: '', reason: '', email: '' });
      }, 3000);
    } catch (error) {
      console.error('Cancellation error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-primary-600 text-white p-4 rounded-t-lg flex items-center justify-between">
          <h3 className="text-lg font-semibold">Customer Service</h3>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {!selectedService && !submitSuccess && (
            <>
              <p className="text-gray-600 mb-6">How can we help you today?</p>
              
              {/* Service Options */}
              <div className="space-y-3">
                <button
                  onClick={() => setSelectedService('cancel')}
                  className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left"
                >
                  <div className="flex items-center">
                    <ExclamationTriangleIcon className="w-5 h-5 text-red-500 mr-3" />
                    <div>
                      <h4 className="font-medium text-gray-900">Cancel Booking</h4>
                      <p className="text-sm text-gray-600">Cancel your existing reservation</p>
                    </div>
                  </div>
                </button>

                <a
                  href="tel:+1-555-HOTEL"
                  className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left block"
                >
                  <div className="flex items-center">
                    <PhoneIcon className="w-5 h-5 text-green-500 mr-3" />
                    <div>
                      <h4 className="font-medium text-gray-900">Call Us</h4>
                      <p className="text-sm text-gray-600">+1-555-HOTEL (24/7)</p>
                    </div>
                  </div>
                </a>

                <button
                  onClick={() => setSelectedService('chat')}
                  className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left"
                >
                  <div className="flex items-center">
                    <ChatBubbleLeftEllipsisIcon className="w-5 h-5 text-blue-500 mr-3" />
                    <div>
                      <h4 className="font-medium text-gray-900">Live Chat</h4>
                      <p className="text-sm text-gray-600">Chat with our support team</p>
                    </div>
                  </div>
                </button>

                <a
                  href="mailto:support@grandpalacehotel.com"
                  className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left block"
                >
                  <div className="flex items-center">
                    <EnvelopeIcon className="w-5 h-5 text-purple-500 mr-3" />
                    <div>
                      <h4 className="font-medium text-gray-900">Email Support</h4>
                      <p className="text-sm text-gray-600">support@grandpalacehotel.com</p>
                    </div>
                  </div>
                </a>
              </div>

              {/* Operating Hours */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <ClockIcon className="w-4 h-4 text-gray-500 mr-2" />
                  <h4 className="font-medium text-gray-900">Support Hours</h4>
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>Phone Support: 24/7</p>
                  <p>Live Chat: 6:00 AM - 12:00 AM</p>
                  <p>Email: Response within 24 hours</p>
                </div>
              </div>
            </>
          )}

          {/* Cancel Booking Form */}
          {selectedService === 'cancel' && !submitSuccess && (
            <div>
              <button
                onClick={() => setSelectedService(null)}
                className="flex items-center text-gray-600 hover:text-gray-800 mb-4"
              >
                ← Back to options
              </button>
              
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Cancel Booking</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Booking ID / Confirmation Number
                  </label>
                  <input
                    type="text"
                    value={cancelBookingForm.bookingId}
                    onChange={(e) => setCancelBookingForm(prev => ({ ...prev, bookingId: e.target.value }))}
                    placeholder="e.g., BK123456789"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={cancelBookingForm.email}
                    onChange={(e) => setCancelBookingForm(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="your.email@example.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reason for Cancellation
                  </label>
                  <select
                    value={cancelBookingForm.reason}
                    onChange={(e) => setCancelBookingForm(prev => ({ ...prev, reason: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Select a reason</option>
                    <option value="change_of_plans">Change of plans</option>
                    <option value="emergency">Emergency</option>
                    <option value="found_better_rate">Found better rate elsewhere</option>
                    <option value="travel_restrictions">Travel restrictions</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
                    <div className="text-sm text-yellow-800">
                      <p className="font-medium mb-1">Cancellation Policy</p>
                      <p>Free cancellation up to 24 hours before check-in. Cancellations within 24 hours may incur charges.</p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleCancelBooking}
                  disabled={isSubmitting}
                  className="w-full bg-red-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Processing...' : 'Submit Cancellation Request'}
                </button>
              </div>
            </div>
          )}

          {/* Live Chat */}
          {selectedService === 'chat' && !submitSuccess && (
            <div>
              <button
                onClick={() => setSelectedService(null)}
                className="flex items-center text-gray-600 hover:text-gray-800 mb-4"
              >
                ← Back to options
              </button>
              
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Live Chat</h4>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-blue-800 text-sm">
                  Our live chat feature will be available soon. In the meantime, please call us at +1-555-HOTEL or send an email to support@grandpalacehotel.com
                </p>
              </div>
              
              <div className="space-y-3">
                <a
                  href="tel:+1-555-HOTEL"
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors text-center block"
                >
                  Call Now: +1-555-HOTEL
                </a>
                
                <a
                  href="mailto:support@grandpalacehotel.com"
                  className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors text-center block"
                >
                  Send Email
                </a>
              </div>
            </div>
          )}

          {/* Success Message */}
          {submitSuccess && (
            <div className="text-center">
              <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Request Submitted</h4>
              <p className="text-gray-600 mb-4">
                Your cancellation request has been submitted successfully. You will receive a confirmation email shortly.
              </p>
              <p className="text-sm text-gray-500">
                This window will close automatically...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomerService;
