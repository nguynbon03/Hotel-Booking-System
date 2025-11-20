import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  MagnifyingGlassIcon,
  MapPinIcon,
  StarIcon,
  CurrencyDollarIcon,
  AdjustmentsHorizontalIcon,
  CalendarDaysIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface Property {
  id: string;
  name: string;
  location: string;
  city: string;
  country: string;
  property_type: string;
  star_rating: number;
  main_image_url: string;
  description: string;
  min_price: number;
  currency: string;
  available_room_types: RoomType[];
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
}

interface SearchFilters {
  city: string;
  check_in: string;
  check_out: string;
  guests: number;
  property_type: string;
  min_price: number;
  max_price: number;
}

const SearchResults = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  
  const [filters, setFilters] = useState<SearchFilters>({
    city: searchParams.get('city') || '',
    check_in: searchParams.get('check_in') || '',
    check_out: searchParams.get('check_out') || '',
    guests: parseInt(searchParams.get('guests') || '2'),
    property_type: searchParams.get('property_type') || '',
    min_price: parseInt(searchParams.get('min_price') || '0'),
    max_price: parseInt(searchParams.get('max_price') || '1000')
  });

  useEffect(() => {
    searchProperties();
  }, [searchParams]);

  const searchProperties = async () => {
    setLoading(true);
    try {
      const params = {
        city: filters.city,
        check_in: filters.check_in,
        check_out: filters.check_out,
        guests: filters.guests,
        property_type: filters.property_type || undefined,
        min_price: filters.min_price || undefined,
        max_price: filters.max_price || undefined,
        limit: 20,
        offset: 0
      };

      const response = await apiClient.searchPublicProperties(params);
      setProperties(response.properties || []);
      setTotal(response.total || 0);
      setHasMore(response.has_more || false);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Failed to search properties');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof SearchFilters, value: string | number) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    // Update URL params
    const newSearchParams = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v && v !== '' && v !== 0) {
        newSearchParams.set(k, v.toString());
      }
    });
    setSearchParams(newSearchParams);
  };

  const handlePropertyClick = (propertyId: string) => {
    const params = new URLSearchParams({
      check_in: filters.check_in,
      check_out: filters.check_out,
      guests: filters.guests.toString()
    });
    navigate(`/property/${propertyId}?${params.toString()}`);
  };

  const calculateNights = () => {
    if (!filters.check_in || !filters.check_out) return 0;
    const checkIn = new Date(filters.check_in);
    const checkOut = new Date(filters.check_out);
    return Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24));
  };

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

      {/* Search Summary */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {filters.city ? `Hotels in ${filters.city}` : 'Search Results'}
              </h1>
              <p className="text-gray-600 mt-1">
                {filters.check_in && filters.check_out && (
                  <>
                    {new Date(filters.check_in).toLocaleDateString()} - {new Date(filters.check_out).toLocaleDateString()} • 
                    {calculateNights()} night{calculateNights() !== 1 ? 's' : ''} • 
                    {filters.guests} guest{filters.guests !== 1 ? 's' : ''}
                  </>
                )}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {total} properties found
              </p>
            </div>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="mt-4 md:mt-0 flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <AdjustmentsHorizontalIcon className="w-5 h-5 mr-2" />
              Filters
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:w-80 bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
              
              {/* Search Location */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPinIcon className="w-4 h-4 inline mr-1" />
                  Destination
                </label>
                <input
                  type="text"
                  value={filters.city}
                  onChange={(e) => handleFilterChange('city', e.target.value)}
                  placeholder="Where are you going?"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Dates */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <CalendarDaysIcon className="w-4 h-4 inline mr-1" />
                  Check-in
                </label>
                <input
                  type="date"
                  value={filters.check_in}
                  onChange={(e) => handleFilterChange('check_in', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <CalendarDaysIcon className="w-4 h-4 inline mr-1" />
                  Check-out
                </label>
                <input
                  type="date"
                  value={filters.check_out}
                  onChange={(e) => handleFilterChange('check_out', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Guests */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <UserGroupIcon className="w-4 h-4 inline mr-1" />
                  Guests
                </label>
                <select
                  value={filters.guests}
                  onChange={(e) => handleFilterChange('guests', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                    <option key={num} value={num}>
                      {num} Guest{num !== 1 ? 's' : ''}
                    </option>
                  ))}
                </select>
              </div>

              {/* Property Type */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property Type
                </label>
                <select
                  value={filters.property_type}
                  onChange={(e) => handleFilterChange('property_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  <option value="HOTEL">Hotel</option>
                  <option value="APARTMENT">Apartment</option>
                  <option value="VILLA">Villa</option>
                  <option value="HOSTEL">Hostel</option>
                </select>
              </div>

              {/* Price Range */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <CurrencyDollarIcon className="w-4 h-4 inline mr-1" />
                  Price Range (per night)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    value={filters.min_price}
                    onChange={(e) => handleFilterChange('min_price', parseInt(e.target.value) || 0)}
                    placeholder="Min"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <input
                    type="number"
                    value={filters.max_price}
                    onChange={(e) => handleFilterChange('max_price', parseInt(e.target.value) || 1000)}
                    placeholder="Max"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          <div className="flex-1">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <LoadingSpinner />
              </div>
            ) : properties.length === 0 ? (
              <div className="text-center py-12">
                <MagnifyingGlassIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No properties found</h3>
                <p className="text-gray-600">Try adjusting your search criteria</p>
              </div>
            ) : (
              <div className="space-y-6">
                {properties.map((property) => (
                  <div
                    key={property.id}
                    onClick={() => handlePropertyClick(property.id)}
                    className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
                  >
                    <div className="flex flex-col md:flex-row">
                      {/* Property Image */}
                      <div className="md:w-80 h-48 md:h-auto">
                        <img
                          src={property.main_image_url || '/placeholder-hotel.jpg'}
                          alt={property.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = '/placeholder-hotel.jpg';
                          }}
                        />
                      </div>

                      {/* Property Details */}
                      <div className="flex-1 p-6">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-1">
                              {property.name}
                            </h3>
                            <div className="flex items-center text-gray-600 mb-2">
                              <MapPinIcon className="w-4 h-4 mr-1" />
                              <span>{property.city}, {property.country}</span>
                            </div>
                            {property.star_rating > 0 && (
                              <div className="flex items-center mb-2">
                                {[...Array(property.star_rating)].map((_, i) => (
                                  <StarIcon key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                                ))}
                              </div>
                            )}
                          </div>
                          
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900">
                              ${property.min_price}
                            </div>
                            <div className="text-sm text-gray-600">per night</div>
                            {calculateNights() > 0 && (
                              <div className="text-sm text-gray-500">
                                ${(property.min_price * calculateNights()).toFixed(2)} total
                              </div>
                            )}
                          </div>
                        </div>

                        <p className="text-gray-600 mb-4 line-clamp-2">
                          {property.description}
                        </p>

                        {/* Available Room Types */}
                        {property.available_room_types && property.available_room_types.length > 0 && (
                          <div className="border-t pt-4">
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Available Rooms:</h4>
                            <div className="space-y-2">
                              {property.available_room_types.slice(0, 2).map((room) => (
                                <div key={room.id} className="flex justify-between items-center text-sm">
                                  <span className="text-gray-700">{room.name}</span>
                                  <span className="text-gray-600">
                                    {room.available_count} available • ${room.price_per_night}/night
                                  </span>
                                </div>
                              ))}
                              {property.available_room_types.length > 2 && (
                                <div className="text-sm text-primary-600">
                                  +{property.available_room_types.length - 2} more room types
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchResults;
