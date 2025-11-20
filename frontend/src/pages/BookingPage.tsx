import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  CalendarDaysIcon,
  UserGroupIcon,
  CreditCardIcon,
  ShieldCheckIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import PublicHeader from '@/components/common/PublicHeader';
import { useAuthStore } from '@/stores/authStore';

interface BookingDetails {
  room_id: string;
  check_in: string;
  check_out: string;
  guests: number;
  nights: number;
  price_per_night: number;
  total_price: number;
  room_details: {
    name: string;
    description: string;
    capacity: number;
  };
}

interface GuestInfo {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  special_requests: string;
}

const BookingPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  
  const [bookingDetails, setBookingDetails] = useState<BookingDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  
  const [guestInfo, setGuestInfo] = useState<GuestInfo>({
    first_name: user?.full_name?.split(' ')[0] || '',
    last_name: user?.full_name?.split(' ').slice(1).join(' ') || '',
    email: user?.email || '',
    phone: '',
    special_requests: ''
  });

  const [paymentInfo, setPaymentInfo] = useState({
    card_number: '',
    expiry_month: '',
    expiry_year: '',
    cvv: '',
    cardholder_name: ''
  });

  useEffect(() => {
    loadBookingDetails();
  }, []);

  const loadBookingDetails = async () => {
    const roomId = searchParams.get('room_id');
    const checkIn = searchParams.get('check_in');
    const checkOut = searchParams.get('check_out');
    const guests = searchParams.get('guests');

    if (!roomId || !checkIn || !checkOut || !guests) {
      toast.error('Missing booking information');
      navigate('/rooms');
      return;
    }

    try {
      setLoading(true);
      
      // Check availability and get pricing
      const availability = await apiClient.checkRoomAvailability({
        room_id: roomId,
        check_in: checkIn,
        check_out: checkOut,
        guests: parseInt(guests)
      });

      if (!availability.available) {
        toast.error('Room is no longer available for these dates');
        navigate('/rooms');
        return;
      }

      setBookingDetails({
        room_id: roomId,
        check_in: checkIn,
        check_out: checkOut,
        guests: parseInt(guests),
        nights: availability.nights,
        price_per_night: availability.price_per_night,
        total_price: availability.total_price,
        room_details: availability.room_details
      });
    } catch (error) {
      console.error('Failed to load booking details:', error);
      toast.error('Failed to load booking details');
      navigate('/rooms');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestInfoSubmit = () => {
    if (!guestInfo.first_name || !guestInfo.last_name || !guestInfo.email || !guestInfo.phone) {
      toast.error('Please fill in all required fields');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(guestInfo.email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setCurrentStep(2);
  };

  const handleBookingSubmit = async () => {
    if (!paymentInfo.card_number || !paymentInfo.expiry_month || !paymentInfo.expiry_year || 
        !paymentInfo.cvv || !paymentInfo.cardholder_name) {
      toast.error('Please fill in all payment information');
      return;
    }

    if (!bookingDetails) {
      toast.error('Booking details not found');
      return;
    }

    setSubmitting(true);
    try {
      // Check if user is authenticated
      if (!isAuthenticated) {
        toast.error('Please login to complete your booking');
        navigate('/auth/login');
        return;
      }

      // Step 1: Check availability one more time before booking
      const availabilityData = await apiClient.checkRoomAvailability({
        room_id: bookingDetails.room_id,
        check_in: bookingDetails.check_in,
        check_out: bookingDetails.check_out,
        guests: bookingDetails.guests
      });
      
      if (!availabilityData.available) {
        toast.error('Room is no longer available for the selected dates');
        return;
      }

      // Step 2: Reserve inventory (temporary hold) - Skip for now, go directly to booking
      // const reserveResponse = await apiClient.reserveInventory({
      //   room_id: bookingDetails.room_id,
      //   check_in: bookingDetails.check_in,
      //   check_out: bookingDetails.check_out,
      //   guest_count: bookingDetails.guests
      // });
      
      // Step 2: Process payment (simulate payment gateway)
      toast.success('Processing payment...');
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Step 3: Create the booking with guest details for email notification
      const bookingPayload = {
        room_id: bookingDetails.room_id,
        check_in: bookingDetails.check_in,
        check_out: bookingDetails.check_out,
        guests: bookingDetails.guests,
        guest_name: `${guestInfo.first_name} ${guestInfo.last_name}`.trim() || paymentInfo.cardholder_name,
        guest_email: guestInfo.email || user?.email || 'guest@example.com',
        guest_phone: guestInfo.phone || '+1234567890',
        special_requests: guestInfo.special_requests || 'Online booking via website'
      };
      
      const bookingResponse = await apiClient.createGuestBooking(bookingPayload);

      // Step 4: Create payment record
      await apiClient.createPayment({
        booking_id: bookingResponse.id,
        method: 'card',
        amount: availabilityData.total_price,
        card_last_four: paymentInfo.card_number.slice(-4)
      });

      toast.success('Booking confirmed! Check your email for confirmation details.');
      setCurrentStep(3);
      
      // Store booking ID for confirmation page
      localStorage.setItem('last_booking_id', bookingResponse.id);
      localStorage.setItem('last_booking_total', availabilityData.total_price.toString());
      
    } catch (error: any) {
      console.error('Booking submission error:', error);
      
      // Handle different types of errors
      let errorMessage = 'Failed to process booking. Please try again.';
      
      if (error.response) {
        // API responded with error
        const status = error.response.status;
        const detail = error.response.data?.detail;
        
        if (status === 401) {
          errorMessage = 'Please login again to complete your booking';
          navigate('/auth/login');
        } else if (status === 403) {
          errorMessage = 'You do not have permission to make bookings';
        } else if (status === 404) {
          errorMessage = 'Room not found or no longer available';
        } else if (status === 409) {
          errorMessage = 'Room is already booked for these dates';
        } else if (detail) {
          errorMessage = detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <PublicHeader />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading booking details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!bookingDetails) {
    return (
      <div className="min-h-screen bg-gray-50">
        <PublicHeader />
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Booking Error</h2>
            <p className="text-gray-600 mb-4">Unable to load booking details</p>
            <button
              onClick={() => navigate('/rooms')}
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Back to Rooms
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <PublicHeader />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Back
        </button>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center">
            {[1, 2, 3].map((step) => (
              <React.Fragment key={step}>
                <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  currentStep >= step 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {currentStep > step ? (
                    <CheckCircleIcon className="w-6 h-6" />
                  ) : (
                    <span className="font-medium">{step}</span>
                  )}
                </div>
                {step < 3 && (
                  <div className={`w-20 h-1 mx-2 ${
                    currentStep > step ? 'bg-primary-600' : 'bg-gray-200'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="flex justify-center mt-4">
            <div className="grid grid-cols-3 gap-8 text-center">
              <div className="text-sm">
                <div className="font-medium">Guest Info</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">Payment</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">Confirmation</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {currentStep === 1 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Guest Information</h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name *
                    </label>
                    <input
                      type="text"
                      value={guestInfo.first_name}
                      onChange={(e) => setGuestInfo(prev => ({ ...prev, first_name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      value={guestInfo.last_name}
                      onChange={(e) => setGuestInfo(prev => ({ ...prev, last_name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      value={guestInfo.email}
                      onChange={(e) => setGuestInfo(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      value={guestInfo.phone}
                      onChange={(e) => setGuestInfo(prev => ({ ...prev, phone: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Special Requests (Optional)
                  </label>
                  <textarea
                    value={guestInfo.special_requests}
                    onChange={(e) => setGuestInfo(prev => ({ ...prev, special_requests: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Any special requests or preferences..."
                  />
                </div>

                <div className="mt-8 flex justify-end">
                  <button
                    onClick={handleGuestInfoSubmit}
                    className="bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
                  >
                    Continue to Payment
                  </button>
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Payment Information</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cardholder Name *
                    </label>
                    <input
                      type="text"
                      value={paymentInfo.cardholder_name}
                      onChange={(e) => setPaymentInfo(prev => ({ ...prev, cardholder_name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Card Number *
                    </label>
                    <input
                      type="text"
                      value={paymentInfo.card_number}
                      onChange={(e) => setPaymentInfo(prev => ({ ...prev, card_number: e.target.value }))}
                      placeholder="1234 5678 9012 3456"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expiry Month *
                      </label>
                      <select
                        value={paymentInfo.expiry_month}
                        onChange={(e) => setPaymentInfo(prev => ({ ...prev, expiry_month: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      >
                        <option value="">Month</option>
                        {Array.from({ length: 12 }, (_, i) => (
                          <option key={i + 1} value={String(i + 1).padStart(2, '0')}>
                            {String(i + 1).padStart(2, '0')}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expiry Year *
                      </label>
                      <select
                        value={paymentInfo.expiry_year}
                        onChange={(e) => setPaymentInfo(prev => ({ ...prev, expiry_year: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      >
                        <option value="">Year</option>
                        {Array.from({ length: 10 }, (_, i) => (
                          <option key={i} value={new Date().getFullYear() + i}>
                            {new Date().getFullYear() + i}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CVV *
                      </label>
                      <input
                        type="text"
                        value={paymentInfo.cvv}
                        onChange={(e) => setPaymentInfo(prev => ({ ...prev, cvv: e.target.value }))}
                        placeholder="123"
                        maxLength={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-8 flex justify-between">
                  <button
                    onClick={() => setCurrentStep(1)}
                    className="bg-gray-300 text-gray-700 px-8 py-3 rounded-lg font-medium hover:bg-gray-400 transition-colors"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleBookingSubmit}
                    disabled={submitting}
                    className="bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {submitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <CreditCardIcon className="w-5 h-5 mr-2" />
                        Complete Booking
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Booking Confirmed!</h2>
                <p className="text-gray-600 mb-6">
                  Your reservation has been confirmed. You will receive a confirmation email shortly.
                </p>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="text-left">
                    <h3 className="font-medium text-gray-900 mb-2">Booking Details</h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p><span className="font-medium">Confirmation:</span> BK{Date.now()}</p>
                      <p><span className="font-medium">Guest:</span> {guestInfo.first_name} {guestInfo.last_name}</p>
                      <p><span className="font-medium">Email:</span> {guestInfo.email}</p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => navigate('/rooms')}
                    className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    Book Another Room
                  </button>
                  <button
                    onClick={() => navigate('/')}
                    className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Back to Home
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Booking Summary Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Booking Summary</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900">{bookingDetails.room_details.name}</h4>
                  <p className="text-sm text-gray-600">{bookingDetails.room_details.description}</p>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <CalendarDaysIcon className="w-4 h-4 mr-2" />
                    <span>Check-in: {new Date(bookingDetails.check_in).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <CalendarDaysIcon className="w-4 h-4 mr-2" />
                    <span>Check-out: {new Date(bookingDetails.check_out).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <UserGroupIcon className="w-4 h-4 mr-2" />
                    <span>{bookingDetails.guests} guest{bookingDetails.guests > 1 ? 's' : ''}</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <ClockIcon className="w-4 h-4 mr-2" />
                    <span>{bookingDetails.nights} night{bookingDetails.nights > 1 ? 's' : ''}</span>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span>Room rate ({bookingDetails.nights} nights)</span>
                    <span>${(bookingDetails.price_per_night * bookingDetails.nights).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Taxes & fees</span>
                    <span>$0.00</span>
                  </div>
                  <div className="border-t border-gray-200 pt-2 flex justify-between font-bold">
                    <span>Total</span>
                    <span>${bookingDetails.total_price.toFixed(2)}</span>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <div className="flex items-center text-sm text-green-600">
                    <ShieldCheckIcon className="w-4 h-4 mr-2" />
                    <span>Free cancellation until 24h before check-in</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingPage;
