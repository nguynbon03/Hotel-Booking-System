import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { 
  CalendarDaysIcon, 
  UserGroupIcon,
  StarIcon,
  WifiIcon,
  TvIcon,
  HomeIcon,
  CheckIcon,
  XMarkIcon,
  ArrowLeftIcon,
  HeartIcon,
  ShareIcon,
  MapPinIcon,
  ClockIcon,
  CreditCardIcon,
  ShieldCheckIcon,
  PhotoIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import PublicHeader from '@/components/common/PublicHeader';
import AIChatbot from '@/components/ui/AIChatbot';

interface RoomDetails {
  id: string;
  name: string;
  description: string;
  capacity: number;
  size_sqm: number;
  bed_type: string;
  amenities: string[];
  base_price: number;
  images?: string[];
  property: {
    id: string;
    name: string;
    location: string;
    star_rating: number;
  };
}

interface AvailabilityCheck {
  available: boolean;
  price_per_night: number;
  total_price: number;
  nights: number;
  message?: string;
  price_breakdown?: {
    base_price_per_night: number;
    nights: number;
    room_total: number;
    extra_guests: number;
    extra_guest_charge_per_night: number;
    extra_guest_total: number;
    subtotal: number;
    service_fee_rate: number;
    service_fee: number;
    tax_rate: number;
    taxes: number;
    total_price: number;
  };
}

const RoomDetails = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const [room, setRoom] = useState<RoomDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkingAvailability, setCheckingAvailability] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showImageGallery, setShowImageGallery] = useState(false);
  const [availability, setAvailability] = useState<AvailabilityCheck | null>(null);
  
  const [bookingForm, setBookingForm] = useState({
    check_in: new Date().toISOString().split('T')[0], // Today
    check_out: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Tomorrow
    guests: 2
  });

  useEffect(() => {
    if (roomId) {
      loadRoomDetails();
    }
  }, [roomId]);

  // Disabled auto-check availability to prevent toast spam
  // Users must manually click "Check Availability" button
  // useEffect(() => {
  //   if (room && roomId && bookingForm.check_in && bookingForm.check_out && bookingForm.guests > 0) {
  //     const timer = setTimeout(() => {
  //       checkAvailability();
  //     }, 500); // Debounce API calls
  //     
  //     return () => clearTimeout(timer);
  //   }
  // }, [room, roomId, bookingForm.check_in, bookingForm.check_out, bookingForm.guests]);

  const loadRoomDetails = async () => {
    if (!roomId) return;
    
    setLoading(true);
    try {
      // Get room details from public API
      const roomData = await apiClient.getPublicRoom(roomId);
      
      if (!roomData) {
        toast.error('Room not found');
        navigate('/rooms');
        return;
      }

      setRoom({
        id: roomData.id,
        name: roomData.name,
        description: roomData.description,
        capacity: roomData.capacity,
        size_sqm: roomData.size_sqm,
        bed_type: roomData.bed_type,
        amenities: roomData.amenities || [],
        base_price: roomData.base_price,
        images: roomData.images && roomData.images.length > 0 ? roomData.images : [
          'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800'
        ],
        property: roomData.property || {
          id: '1',
          name: 'Grand Palace Hotel',
          location: 'City Center',
          star_rating: 5
        }
      });
    } catch (error) {
      console.error('Failed to load room details:', error);
      toast.error('Failed to load room details');
      navigate('/rooms');
    } finally {
      setLoading(false);
    }
  };

  const checkAvailability = async () => {
    if (!bookingForm.check_in || !bookingForm.check_out || !roomId) {
      toast.error('Please select check-in and check-out dates');
      return;
    }

    if (new Date(bookingForm.check_in) >= new Date(bookingForm.check_out)) {
      toast.error('Check-out date must be after check-in date');
      return;
    }

    setCheckingAvailability(true);
    try {
      // Use apiClient for consistent API calls
      const availabilityData = await apiClient.checkRoomAvailability({
        room_id: roomId,
        check_in: bookingForm.check_in,
        check_out: bookingForm.check_out,
        guests: bookingForm.guests
      });
      
      console.log('Availability response:', availabilityData);
      
      setAvailability({
        available: availabilityData.available,
        price_per_night: availabilityData.price_per_night || 0,
        total_price: availabilityData.total_price || 0,
        nights: availabilityData.nights || calculateNights(),
        message: availabilityData.message || (availabilityData.available 
          ? 'Great! This room is available for your selected dates.'
          : 'Sorry, this room is already booked for your selected dates. Please try different dates.'),
        price_breakdown: availabilityData.price_breakdown
      });
      
      // Update room price display with real-time pricing
      if (availabilityData.price_per_night && room) {
        setRoom({
          ...room,
          price_per_night: availabilityData.price_per_night
        });
      }
      
      // Don't show toast for successful availability checks - just update the UI
      
    } catch (error: any) {
      console.error('Failed to check availability:', error);
      
      // Only show error toast for actual failures, not for "room not available"
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to check availability';
      if (!errorMessage.includes('not available') && !errorMessage.includes('already booked')) {
        toast.error(errorMessage);
      }
      
      // Fallback to basic calculation if API fails
      const nights = calculateNights();
      const pricePerNight = room?.price_per_night || 0;
      
      setAvailability({
        available: false,
        price_per_night: pricePerNight,
        total_price: pricePerNight * nights,
        nights: nights,
        message: 'Availability check failed, showing estimated pricing.'
      });
    } finally {
      setCheckingAvailability(false);
    }
  };

  const handleBookNow = () => {
    // Check authentication first
    if (!isAuthenticated) {
      toast.error('Please login to book this room');
      navigate('/auth/login');
      return;
    }

    if (!availability?.available) {
      toast.error('Room is not available for selected dates');
      return;
    }

    const bookingParams = new URLSearchParams({
      room_id: roomId || '',
      check_in: bookingForm.check_in,
      check_out: bookingForm.check_out,
      guests: bookingForm.guests.toString(),
      total_price: availability.total_price.toString()
    });
    
    navigate(`/booking?${bookingParams.toString()}`);
  };

  const calculateNights = () => {
    if (!bookingForm.check_in || !bookingForm.check_out) return 1;
    const checkIn = new Date(bookingForm.check_in);
    const checkOut = new Date(bookingForm.check_out);
    const diffTime = Math.abs(checkOut.getTime() - checkIn.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const handleFavoriteToggle = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add favorites');
      navigate('/auth/login');
      return;
    }

    try {
      if (isFavorite) {
        // Remove from favorites
        await apiClient.removeFavoriteByProperty(room?.property?.id);
        setIsFavorite(false);
        // Removed from favorites - no toast needed, UI update is enough
      } else {
        // Add to favorites
        await apiClient.addFavorite({
          property_id: room?.property?.id,
          category: 'hotel'
        });
        setIsFavorite(true);
        // Added to favorites - no toast needed, UI update is enough
      }
    } catch (error: any) {
      console.error('Favorite toggle error:', error);
      toast.error(error.response?.data?.detail || 'Failed to update favorites');
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: room?.name,
          text: room?.description,
          url: window.location.href,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    }
  };

  const nextImage = () => {
    if (room?.images) {
      setCurrentImageIndex((prev) => (prev + 1) % room.images!.length);
    }
  };

  const prevImage = () => {
    if (room?.images) {
      setCurrentImageIndex((prev) => (prev - 1 + room.images!.length) % room.images!.length);
    }
  };

  const getAmenityIcon = (amenity: string) => {
    const amenityLower = amenity.toLowerCase();
    if (amenityLower.includes('wifi')) return <WifiIcon className="w-4 h-4" />;
    if (amenityLower.includes('tv')) return <TvIcon className="w-4 h-4" />;
    return <HomeIcon className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!room) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Room not found</h2>
          <button
            onClick={() => navigate('/rooms')}
            className="text-primary-600 hover:text-primary-700"
          >
            Back to rooms
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <PublicHeader />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Back Button */}
        <button
          onClick={() => navigate('/rooms')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Back to All Rooms
        </button>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Room Details */}
          <div className="lg:col-span-2">
            {/* Room Images */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-6">
              <div className="h-96 relative group">
                <img
                  src={room.images?.[currentImageIndex] || 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800'}
                  alt={room.name}
                  className="w-full h-full object-cover cursor-pointer"
                  onClick={() => setShowImageGallery(true)}
                />
                
                {/* Image Navigation */}
                {room.images && room.images.length > 1 && (
                  <>
                    <button
                      onClick={prevImage}
                      className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <ArrowLeftIcon className="w-5 h-5" />
                    </button>
                    <button
                      onClick={nextImage}
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <ArrowLeftIcon className="w-5 h-5 rotate-180" />
                    </button>
                  </>
                )}

                {/* Image Counter */}
                {room.images && room.images.length > 1 && (
                  <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
                    {currentImageIndex + 1} / {room.images.length}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="absolute top-4 right-4 flex space-x-2">
                  <button
                    onClick={handleShare}
                    className="bg-white/90 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
                  >
                    <ShareIcon className="w-5 h-5 text-gray-700" />
                  </button>
                  <button
                    onClick={handleFavoriteToggle}
                    className="bg-white/90 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
                  >
                    {isFavorite ? (
                      <HeartIconSolid className="w-5 h-5 text-red-500" />
                    ) : (
                      <HeartIcon className="w-5 h-5 text-gray-700" />
                    )}
                  </button>
                </div>

                {/* View Gallery Button */}
                {room.images && room.images.length > 1 && (
                  <button
                    onClick={() => setShowImageGallery(true)}
                    className="absolute bottom-4 left-4 bg-white/90 hover:bg-white px-4 py-2 rounded-lg shadow-lg transition-colors flex items-center"
                  >
                    <PhotoIcon className="w-4 h-4 mr-2" />
                    View All Photos
                  </button>
                )}
              </div>
            </div>

            {/* Room Info */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <div className="mb-4">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{room.name}</h1>
                <div className="flex items-center text-gray-600 mb-2">
                  <span className="font-medium">{room.property.name}</span>
                  {room.property.star_rating > 0 && (
                    <div className="flex items-center ml-3">
                      {[...Array(room.property.star_rating)].map((_, i) => (
                        <StarIcon key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <p className="text-gray-700 mb-6">{room.description}</p>

              {/* Room Features */}
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="flex items-center">
                  <UserGroupIcon className="w-5 h-5 text-gray-400 mr-2" />
                  <span>Up to {room.capacity} guests</span>
                </div>
                <div className="flex items-center">
                  <span className="text-gray-400 mr-2">📐</span>
                  <span>{room.size_sqm} m²</span>
                </div>
                <div className="flex items-center">
                  <span className="text-gray-400 mr-2">🛏️</span>
                  <span>{room.bed_type}</span>
                </div>
              </div>

              {/* Amenities */}
              {room.amenities && room.amenities.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Amenities</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {room.amenities.map((amenity, index) => (
                      <div key={index} className="flex items-center">
                        {getAmenityIcon(amenity)}
                        <span className="ml-2 text-gray-700">{amenity}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Booking Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Check Availability</h3>
              
              <div className="mb-4">
                <div className="text-2xl font-bold text-gray-900">
                  ${availability?.price_per_night || room.price_per_night || 0}
                </div>
                <div className="text-gray-600">per night</div>
                {availability?.price_per_night && availability.price_per_night !== room.price_per_night && (
                  <div className="text-sm text-blue-600">
                    Updated pricing for selected dates
                  </div>
                )}
              </div>

              {/* Date Selection */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <CalendarDaysIcon className="w-4 h-4 inline mr-1" />
                    Check-in
                  </label>
                  <input
                    type="date"
                    value={bookingForm.check_in}
                    onChange={(e) => setBookingForm(prev => ({ ...prev, check_in: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <CalendarDaysIcon className="w-4 h-4 inline mr-1" />
                    Check-out
                  </label>
                  <input
                    type="date"
                    value={bookingForm.check_out}
                    onChange={(e) => setBookingForm(prev => ({ ...prev, check_out: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <UserGroupIcon className="w-4 h-4 inline mr-1" />
                    Guests (Max: {room.capacity})
                  </label>
                  <select
                    value={bookingForm.guests}
                    onChange={(e) => setBookingForm(prev => ({ ...prev, guests: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {Array.from({ length: room.capacity }, (_, i) => i + 1).map(num => (
                      <option key={num} value={num}>
                        {num} Guest{num !== 1 ? 's' : ''}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Additional charges: $10/night per extra guest beyond 2
                  </p>
                </div>
              </div>


              {/* Availability Result */}
              {availability && (
                <div className={`p-4 rounded-lg mb-4 ${
                  availability.available 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center mb-2">
                    {availability.available ? (
                      <CheckIcon className="w-5 h-5 text-green-600 mr-2" />
                    ) : (
                      <XMarkIcon className="w-5 h-5 text-red-600 mr-2" />
                    )}
                    <span className={`font-medium ${
                      availability.available ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {availability.available ? 'Available!' : 'Not Available'}
                    </span>
                  </div>
                  
                  <p className={`text-sm ${
                    availability.available ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {availability.message}
                  </p>

                  {availability.available && availability.price_breakdown && (
                    <div className="mt-3 pt-3 border-t border-green-200">
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Room rate ({availability.price_breakdown.nights} nights):</span>
                          <span>${availability.price_breakdown.room_total.toFixed(2)}</span>
                        </div>
                        
                        {availability.price_breakdown.extra_guests > 0 && (
                          <div className="flex justify-between">
                            <span>Extra guests ({availability.price_breakdown.extra_guests} × ${availability.price_breakdown.extra_guest_charge_per_night}/night):</span>
                            <span>${availability.price_breakdown.extra_guest_total.toFixed(2)}</span>
                          </div>
                        )}
                        
                        <div className="flex justify-between">
                          <span>Subtotal:</span>
                          <span>${availability.price_breakdown.subtotal.toFixed(2)}</span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span>Taxes & fees (10%):</span>
                          <span>${availability.price_breakdown.taxes.toFixed(2)}</span>
                        </div>
                        
                        <div className="flex justify-between font-semibold text-green-800 pt-2 border-t border-green-200">
                          <span>Total:</span>
                          <span>${availability.price_breakdown.total_price?.toFixed(2) || availability.total_price.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Book Now Button */}
              {availability ? (
                availability.available ? (
                  <button
                    onClick={handleBookNow}
                    className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                  >
                    Book Now - ${availability.total_price}
                  </button>
                ) : (
                  <button
                    disabled
                    className="w-full bg-gray-400 text-white py-3 px-4 rounded-lg font-semibold cursor-not-allowed"
                  >
                    Not Available
                  </button>
                )
              ) : (
                <button
                  onClick={() => {
                    if (!bookingForm.check_in || !bookingForm.check_out) {
                      toast.error('Please select check-in and check-out dates first');
                      return;
                    }
                    checkAvailability();
                  }}
                  disabled={checkingAvailability}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {checkingAvailability ? 'Checking...' : 'Check Availability'}
                </button>
              )}

              {/* Info */}
              <div className="text-center text-sm text-gray-500 mt-4">
                <div className="flex items-center justify-center mb-1">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-1" />
                  Free cancellation
                </div>
                <div className="flex items-center justify-center">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-1" />
                  No booking fees
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Gallery Modal */}
      {showImageGallery && room?.images && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
          <div className="max-w-4xl max-h-full p-4">
            <div className="relative">
              <button
                onClick={() => setShowImageGallery(false)}
                className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
              >
                <XMarkIcon className="w-8 h-8" />
              </button>
              
              <img
                src={room.images[currentImageIndex]}
                alt={`${room.name} - Image ${currentImageIndex + 1}`}
                className="max-w-full max-h-[80vh] object-contain mx-auto"
              />
              
              {room.images.length > 1 && (
                <>
                  <button
                    onClick={prevImage}
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300"
                  >
                    <ArrowLeftIcon className="w-8 h-8" />
                  </button>
                  <button
                    onClick={nextImage}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300"
                  >
                    <ArrowLeftIcon className="w-8 h-8 rotate-180" />
                  </button>
                </>
              )}
              
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-white text-sm">
                {currentImageIndex + 1} / {room.images.length}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Chatbot */}
      <AIChatbot />
    </div>
  );
};

export default RoomDetails;
