import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  CalendarDaysIcon, 
  UserGroupIcon,
  StarIcon,
  WifiIcon,
  TvIcon,
  HomeIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import PublicHeader from '@/components/common/PublicHeader';
import AIChatbot from '@/components/ui/AIChatbot';
import LiveStaffChat from '@/components/ui/LiveStaffChat';

interface RoomType {
  id: string;
  name: string;
  description: string;
  capacity: number;
  size_sqm: number;
  bed_type: string;
  amenities: string[];
  base_price: number;
  final_price: number;
  images?: string[];
  available: boolean;
  room_type: {
    id: string;
    name: string;
    description: string;
    max_occupancy: number;
  };
  property: {
    id: string;
    name: string;
    city: string;
    country: string;
    address: string;
    rating: number;
  };
}

interface RoomsResponse {
  rooms: RoomType[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
    current_page: number;
    total_pages: number;
  };
  filters_applied: {
    room_type: string | null;
    min_price: number | null;
    max_price: number | null;
    min_capacity: number | null;
    max_capacity: number | null;
    amenities: string | null;
  };
}

interface FilterState {
  room_type: string;
  min_price: string;
  max_price: string;
  min_capacity: string;
  max_capacity: string;
  amenities: string;
}

const RoomsPage = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [rooms, setRooms] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState<RoomsResponse['pagination'] | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    room_type: '',
    min_price: '',
    max_price: '',
    min_capacity: '',
    max_capacity: '',
    amenities: ''
  });

  useEffect(() => {
    loadRooms(1);
  }, []);

  const loadRooms = async (page: number = 1) => {
    try {
      setLoading(true);
      
      // Build query parameters
      const params: any = {
        limit: 12, // Show 12 rooms per page
        offset: (page - 1) * 12
      };

      // Add filters if they exist
      if (filters.room_type) params.room_type = filters.room_type;
      if (filters.min_price) params.min_price = parseFloat(filters.min_price);
      if (filters.max_price) params.max_price = parseFloat(filters.max_price);
      if (filters.min_capacity) params.min_capacity = parseInt(filters.min_capacity);
      if (filters.max_capacity) params.max_capacity = parseInt(filters.max_capacity);
      if (filters.amenities) params.amenities = filters.amenities;

      const response: RoomsResponse = await apiClient.getPublicRooms(params);
      
      if (!response || !response.rooms) {
        console.error('Invalid API response:', response);
        toast.error('Invalid response from server');
        return;
      }

      const roomData = response.rooms?.map((room: any) => ({
        id: room.id,
        name: room.name,
        description: room.description,
        capacity: room.capacity,
        size_sqm: room.size_sqm,
        bed_type: room.bed_type,
        amenities: room.amenities || [],
        base_price: room.base_price,
        final_price: room.final_price,
        available: room.available,
        images: room.image_url ? [room.image_url] : [
          'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500'
        ],
        room_type: room.room_type,
        property: room.property
      })) || [];

      setRooms(roomData);
      setPagination(response.pagination);
      
      if (roomData.length === 0) {
        toast.info('No rooms found matching your criteria.');
      }
    } catch (error: any) {
      console.error('Failed to load rooms:', error);
      console.error('Error details:', error.response?.data || error.message);
      toast.error(`Failed to load rooms: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    loadRooms(1); // Reset to first page when applying filters
  };

  const clearFilters = () => {
    setFilters({
      room_type: '',
      min_price: '',
      max_price: '',
      min_capacity: '',
      max_capacity: '',
      amenities: ''
    });
    loadRooms(1);
  };

  const handlePageChange = (page: number) => {
    loadRooms(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };


  const getAmenityIcon = (amenity: string) => {
    const amenityLower = amenity.toLowerCase();
    if (amenityLower.includes('wifi')) return <WifiIcon className="w-4 h-4" />;
    if (amenityLower.includes('tv')) return <TvIcon className="w-4 h-4" />;
    return <HomeIcon className="w-4 h-4" />;
  };


  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <PublicHeader />

      {/* Page Header with Filters */}
      <section className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Our Rooms & Suites</h1>
            <p className="text-gray-600">
              Discover our collection of luxury accommodations. Select a room to view details and check availability.
            </p>
            {pagination && (
              <p className="text-sm text-gray-500 mt-2">
                Showing {pagination.offset + 1}-{Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total} rooms
              </p>
            )}
          </div>

          {/* Filter Toggle */}
          <div className="flex justify-center">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-6 bg-gray-50 rounded-lg p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Room Type</label>
                  <select
                    value={filters.room_type}
                    onChange={(e) => handleFilterChange('room_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">All Types</option>
                    <option value="Standard">Standard</option>
                    <option value="Deluxe">Deluxe</option>
                    <option value="Executive">Executive</option>
                    <option value="Presidential">Presidential</option>
                    <option value="Accessible">Accessible</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Min Price</label>
              <input
                    type="number"
                    value={filters.min_price}
                    onChange={(e) => handleFilterChange('min_price', e.target.value)}
                    placeholder="$0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Price</label>
              <input
                    type="number"
                    value={filters.max_price}
                    onChange={(e) => handleFilterChange('max_price', e.target.value)}
                    placeholder="$1000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Min Guests</label>
                  <select
                    value={filters.min_capacity}
                    onChange={(e) => handleFilterChange('min_capacity', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Any</option>
                    <option value="1">1+</option>
                    <option value="2">2+</option>
                    <option value="3">3+</option>
                    <option value="4">4+</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Guests</label>
              <select
                    value={filters.max_capacity}
                    onChange={(e) => handleFilterChange('max_capacity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                    <option value="">Any</option>
                    <option value="2">Up to 2</option>
                    <option value="3">Up to 3</option>
                    <option value="4">Up to 4</option>
                    <option value="6">Up to 6</option>
              </select>
            </div>
            
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amenities</label>
                  <input
                    type="text"
                    value={filters.amenities}
                    onChange={(e) => handleFilterChange('amenities', e.target.value)}
                    placeholder="WiFi, Pool..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="flex justify-center space-x-4 mt-6">
                <button
                  onClick={applyFilters}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Apply Filters
                </button>
            <button
                  onClick={clearFilters}
                  className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
            >
                  Clear All
            </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Rooms List */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {loading ? (
          <div className="space-y-6">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="md:flex">
                  <div className="md:w-1/3">
                    <div className="h-48 bg-gray-200 animate-pulse"></div>
                  </div>
                  <div className="md:w-2/3 p-6">
                    <div className="h-6 bg-gray-200 rounded mb-2 animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2 animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4 animate-pulse"></div>
                    <div className="flex justify-between items-center">
                      <div className="h-6 bg-gray-200 rounded w-20 animate-pulse"></div>
                      <div className="h-8 bg-gray-200 rounded w-24 animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : rooms.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No rooms available for the selected dates.</p>
            <p className="text-gray-400 mt-2">Please try different dates or contact us directly.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {rooms.map((room) => (
              <div key={room.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="md:flex">
                  {/* Room Image */}
                  <div className="md:w-1/3">
                    <img
                      src={room.images?.[0] || 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500'}
                      alt={room.name}
                      className="w-full h-64 md:h-full object-cover"
                    />
                  </div>
                  
                  {/* Room Details */}
                  <div className="md:w-2/3 p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">{room.name}</h3>
                        <p className="text-gray-600 mb-3">{room.description}</p>
                        
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-4">
                          <span>👥 Up to {room.capacity} guests</span>
                          <span>📐 {room.size_sqm} m²</span>
                          <span>🛏️ {room.bed_type}</span>
                        </div>
                        
                        {/* Amenities */}
                        {room.amenities && room.amenities.length > 0 && (
                          <div className="mb-4">
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Amenities</h4>
                            <div className="flex flex-wrap gap-2">
                              {room.amenities.slice(0, 6).map((amenity, index) => (
                                <span
                                  key={index}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                                >
                                  {getAmenityIcon(amenity)}
                                  {amenity}
                                </span>
                              ))}
                              {room.amenities.length > 6 && (
                                <span className="text-xs text-gray-500">
                                  +{room.amenities.length - 6} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Price and Book Button */}
                      <div className="text-right ml-4">
                        <div className="mb-4">
                          {room.final_price !== room.base_price && (
                            <p className="text-sm text-gray-500 line-through">
                              ${room.base_price}/night
                            </p>
                          )}
                          <p className="text-2xl font-bold text-gray-900">
                            ${room.final_price}
                          </p>
                          <p className="text-sm text-gray-500">per night</p>
                        </div>
                        
                        <button
                          onClick={() => navigate(`/room/${room.id}`)}
                          className="w-full bg-primary-600 text-white px-6 py-3 rounded-md font-medium hover:bg-primary-700 transition-colors"
                        >
                          View Details
                        </button>
                        
                        <div className="flex items-center justify-center mt-2 text-gray-600 text-sm">
                            <CheckIcon className="w-4 h-4 mr-1" />
                          Select dates to check availability
                          </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {pagination && pagination.total_pages > 1 && (
          <div className="flex justify-center items-center space-x-2 mt-8">
            <button
              onClick={() => handlePageChange(pagination.current_page - 1)}
              disabled={pagination.current_page <= 1}
              className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {Array.from({ length: pagination.total_pages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`px-3 py-2 border rounded-md ${
                  page === pagination.current_page
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                {page}
              </button>
            ))}
            
            <button
              onClick={() => handlePageChange(pagination.current_page + 1)}
              disabled={pagination.current_page >= pagination.total_pages}
              className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </section>

      {/* AI Chatbot */}
      <AIChatbot />
      
      {/* Live Staff Chat */}
      <LiveStaffChat />
    </div>
  );
};

export default RoomsPage;
