import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { 
  MapPinIcon,
  StarIcon,
  CalendarDaysIcon,
  UserGroupIcon,
  PhoneIcon,
  ClockIcon,
  CurrencyDollarIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface PropertyDetails {
  id: string;
  name: string;
  description: string;
  property_type: string;
  star_rating: number;
  address: string;
  city: string;
  country: string;
  postal_code: string;
  latitude: number;
  longitude: number;
  contact_email: string;
  contact_phone: string;
  check_in_time: string;
  check_out_time: string;
  currency: string;
  cancellation_policy: string;
  house_rules: string;
  main_image_url: string;
  organization: {
    id: string;
    name: string;
    slug: string;
  };
  available_room_types: RoomType[];
  min_price: number;
}

interface RoomType {
  id: string;
  name: string;
  description: string;
  max_occupancy: number;
  available_count: number;
  price: number;
  price_per_night: number;
  currency: string;
  nights: number;
  rate_plans: RatePlan[];
}

interface RatePlan {
  id: string;
  name: string;
  base_price: number;
  currency: string;
  is_refundable: boolean;
  cancellation_policy: string;
}

const PropertyDetails = () => {
  const { propertyId } = useParams<{ propertyId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const [property, setProperty] = useState<PropertyDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRoom, setSelectedRoom] = useState<RoomType | null>(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  
  const checkIn = searchParams.get('check_in') || '';
  const checkOut = searchParams.get('check_out') || '';
  const guests = parseInt(searchParams.get('guests') || '2');

  useEffect(() => {
    if (propertyId) {
      loadPropertyDetails();
    }
  }, [propertyId]);

  const loadPropertyDetails = async () => {
    if (!propertyId) return;
    
    setLoading(true);
    try {
      const params = checkIn && checkOut ? {
        check_in: checkIn,
        check_out: checkOut,
        guests: guests
      } : undefined;

      const response = await apiClient.getPublicPropertyDetails(propertyId, params);
      setProperty(response);
    } catch (error) {
      console.error('Failed to load property details:', error);
      toast.error('Failed to load property details');
      navigate('/search');
    } finally {
      setLoading(false);
    }
  };

  const calculateNights = () => {
    if (!checkIn || !checkOut) return 0;
    const checkInDate = new Date(checkIn);
    const checkOutDate = new Date(checkOut);
    return Math.ceil((checkOutDate.getTime() - checkInDate.getTime()) / (1000 * 60 * 60 * 24));
  };

  const handleBookRoom = (room: RoomType) => {
    setSelectedRoom(room);
    setShowBookingModal(true);
  };

  const handleProceedToBooking = () => {
    // Redirect to registration/login with booking intent
    const bookingParams = new URLSearchParams({
      property_id: propertyId || '',
      room_type_id: selectedRoom?.id || '',
      check_in: checkIn,
      check_out: checkOut,
      guests: guests.toString()
    });
    
    navigate(`/auth/register?${bookingParams.toString()}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!property) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Property not found</h2>
          <button
            onClick={() => navigate('/search')}
            className="text-primary-600 hover:text-primary-700"
          >
            Back to search
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="text-2xl font-bold text-primary-600 hover:text-primary-700"
              >
                HotelBooking
              </button>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/search')}
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Back to Search
              </button>
              <button
                onClick={() => navigate('/auth/login')}
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/auth/register')}
                className="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Property Header */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-6">
          {/* Hero Image */}
          <div className="h-96 relative">
            <img
              src={property.main_image_url || '/placeholder-hotel.jpg'}
              alt={property.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/placeholder-hotel.jpg';
              }}
            />
            <div className="absolute inset-0 bg-black bg-opacity-30 flex items-end">
              <div className="p-6 text-white">
                <h1 className="text-4xl font-bold mb-2">{property.name}</h1>
                <div className="flex items-center mb-2">
                  <MapPinIcon className="w-5 h-5 mr-2" />
                  <span className="text-lg">{property.address}, {property.city}, {property.country}</span>
                </div>
                {property.star_rating > 0 && (
                  <div className="flex items-center">
                    {[...Array(property.star_rating)].map((_, i) => (
                      <StarIcon key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                    <span className="ml-2 text-lg">{property.star_rating} Star {property.property_type}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* About */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">About this property</h2>
              <p className="text-gray-700 leading-relaxed">
                {property.description || 'No description available.'}
              </p>
            </div>

            {/* Property Details */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Property Details</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <ClockIcon className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <div className="font-medium">Check-in</div>
                    <div className="text-gray-600">{property.check_in_time}</div>
                  </div>
                </div>
                <div className="flex items-center">
                  <ClockIcon className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <div className="font-medium">Check-out</div>
                    <div className="text-gray-600">{property.check_out_time}</div>
                  </div>
                </div>
                {property.contact_phone && (
                  <div className="flex items-center">
                    <PhoneIcon className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="font-medium">Contact</div>
                      <div className="text-gray-600">{property.contact_phone}</div>
                    </div>
                  </div>
                )}
                <div className="flex items-center">
                  <MapPinIcon className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <div className="font-medium">Property Type</div>
                    <div className="text-gray-600">{property.property_type}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Policies */}
            {(property.cancellation_policy || property.house_rules) && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Policies</h2>
                {property.cancellation_policy && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Cancellation Policy</h3>
                    <p className="text-gray-700">{property.cancellation_policy}</p>
                  </div>
                )}
                {property.house_rules && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">House Rules</h3>
                    <p className="text-gray-700">{property.house_rules}</p>
                  </div>
                )}
              </div>
            )}

            {/* Available Rooms */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Available Rooms</h2>
              {checkIn && checkOut && (
                <div className="mb-4 p-4 bg-primary-50 rounded-lg">
                  <div className="flex items-center text-primary-700">
                    <CalendarDaysIcon className="w-5 h-5 mr-2" />
                    <span className="font-medium">
                      {new Date(checkIn).toLocaleDateString()} - {new Date(checkOut).toLocaleDateString()}
                    </span>
                    <span className="mx-2">•</span>
                    <UserGroupIcon className="w-5 h-5 mr-1" />
                    <span>{guests} guest{guests !== 1 ? 's' : ''}</span>
                    <span className="mx-2">•</span>
                    <span>{calculateNights()} night{calculateNights() !== 1 ? 's' : ''}</span>
                  </div>
                </div>
              )}

              {property.available_room_types && property.available_room_types.length > 0 ? (
                <div className="space-y-4">
                  {property.available_room_types.map((room) => (
                    <div key={room.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">{room.name}</h3>
                          <p className="text-gray-600 mb-2">{room.description}</p>
                          <div className="flex items-center text-sm text-gray-500 space-x-4">
                            <span>Max {room.max_occupancy} guests</span>
                            <span>{room.available_count} available</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-gray-900">
                            ${room.price_per_night}
                          </div>
                          <div className="text-sm text-gray-600">per night</div>
                          {calculateNights() > 0 && (
                            <div className="text-lg font-semibold text-primary-600 mt-1">
                              ${room.price} total
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Rate Plans */}
                      {room.rate_plans && room.rate_plans.length > 0 && (
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Rate Options:</h4>
                          <div className="space-y-1">
                            {room.rate_plans.map((plan) => (
                              <div key={plan.id} className="flex items-center justify-between text-sm">
                                <div className="flex items-center">
                                  {plan.is_refundable ? (
                                    <CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />
                                  ) : (
                                    <XCircleIcon className="w-4 h-4 text-red-500 mr-2" />
                                  )}
                                  <span className="text-gray-700">{plan.name}</span>
                                </div>
                                <span className="text-gray-600">
                                  {plan.is_refundable ? 'Free cancellation' : 'Non-refundable'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <button
                        onClick={() => handleBookRoom(room)}
                        disabled={room.available_count === 0}
                        className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                      >
                        {room.available_count === 0 ? 'Sold Out' : 'Select Room'}
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600">No rooms available for the selected dates.</p>
                  <p className="text-sm text-gray-500 mt-2">Try different dates or contact the property directly.</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Book Your Stay</h3>
              
              {property.min_price && (
                <div className="mb-4">
                  <div className="text-3xl font-bold text-gray-900">
                    From ${property.min_price}
                  </div>
                  <div className="text-gray-600">per night</div>
                </div>
              )}

              {checkIn && checkOut && calculateNights() > 0 && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Your stay</div>
                  <div className="font-medium">{calculateNights()} nights</div>
                  <div className="text-sm text-gray-600">
                    {new Date(checkIn).toLocaleDateString()} - {new Date(checkOut).toLocaleDateString()}
                  </div>
                </div>
              )}

              <button
                onClick={() => setShowBookingModal(true)}
                className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 transition-colors mb-4"
              >
                Book Now
              </button>

              <div className="text-center text-sm text-gray-500">
                <div className="flex items-center justify-center mb-1">
                  <CheckCircleIcon className="w-4 h-4 text-green-500 mr-1" />
                  Free cancellation
                </div>
                <div className="flex items-center justify-center">
                  <CheckCircleIcon className="w-4 h-4 text-green-500 mr-1" />
                  No booking fees
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      {showBookingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Complete Your Booking</h3>
            
            {selectedRoom && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900">{selectedRoom.name}</h4>
                <p className="text-sm text-gray-600 mb-2">{selectedRoom.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    {calculateNights()} nights • {guests} guests
                  </span>
                  <span className="font-bold text-primary-600">
                    ${selectedRoom.price}
                  </span>
                </div>
              </div>
            )}

            <p className="text-gray-600 mb-6">
              To complete your booking, please sign up or sign in to your account.
            </p>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowBookingModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleProceedToBooking}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyDetails;
