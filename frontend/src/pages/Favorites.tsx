import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  HeartIcon,
  MapPinIcon,
  StarIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { toast } from 'react-hot-toast';
import PublicHeader from '../components/common/PublicHeader';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { apiClient } from '../lib/api';

interface Favorite {
  id: string;
  property_id: string;
  category: string;
  created_at: string;
  property?: {
    id: string;
    name: string;
    city: string;
    country: string;
    address: string;
    star_rating: number;
    main_image_url?: string;
    description?: string;
  };
}

const Favorites: React.FC = () => {
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getFavorites();
      setFavorites(response);
    } catch (error: any) {
      console.error('Failed to load favorites:', error);
      toast.error('Failed to load favorites');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (favoriteId: string) => {
    if (!confirm('Are you sure you want to remove this from your favorites?')) {
      return;
    }

    try {
      await apiClient.removeFavorite(favoriteId);
      toast.success('Removed from favorites');
      loadFavorites(); // Reload favorites
    } catch (error: any) {
      console.error('Failed to remove favorite:', error);
      toast.error(error.response?.data?.detail || 'Failed to remove favorite');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, index) => (
      <StarIcon
        key={index}
        className={`w-4 h-4 ${
          index < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <PublicHeader />
        <div className="flex items-center justify-center py-20">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <PublicHeader />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Favorites</h1>
          <p className="text-gray-600">Properties you've saved for later</p>
        </div>

        {favorites.length === 0 ? (
          <div className="text-center py-12">
            <HeartIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No favorites yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Start exploring and save properties you love!
            </p>
            <div className="mt-6">
              <button
                onClick={() => navigate('/rooms')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                Browse Properties
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favorites.map((favorite) => (
              <div key={favorite.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                {/* Property Image */}
                <div className="h-48 bg-gray-200 relative">
                  <img
                    src={favorite.property?.main_image_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400'}
                    alt={favorite.property?.name}
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Favorite Button */}
                  <button
                    onClick={() => handleRemoveFavorite(favorite.id)}
                    className="absolute top-3 right-3 bg-white/90 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
                  >
                    <HeartIconSolid className="w-5 h-5 text-red-500" />
                  </button>

                  {/* Category Badge */}
                  <div className="absolute top-3 left-3">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 capitalize">
                      {favorite.category}
                    </span>
                  </div>
                </div>

                {/* Property Details */}
                <div className="p-4">
                  <div className="mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {favorite.property?.name || 'Property Name'}
                    </h3>
                    
                    {/* Rating */}
                    {favorite.property?.star_rating && (
                      <div className="flex items-center mb-2">
                        <div className="flex items-center">
                          {renderStars(favorite.property.star_rating)}
                        </div>
                        <span className="ml-2 text-sm text-gray-600">
                          {favorite.property.star_rating} star{favorite.property.star_rating > 1 ? 's' : ''}
                        </span>
                      </div>
                    )}

                    {/* Location */}
                    <div className="flex items-center text-sm text-gray-600 mb-2">
                      <MapPinIcon className="w-4 h-4 mr-1" />
                      <span>
                        {favorite.property?.city && favorite.property?.country 
                          ? `${favorite.property.city}, ${favorite.property.country}`
                          : favorite.property?.address || 'Location not specified'
                        }
                      </span>
                    </div>

                    {/* Description */}
                    {favorite.property?.description && (
                      <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                        {favorite.property.description}
                      </p>
                    )}

                    {/* Added Date */}
                    <p className="text-xs text-gray-500 mb-4">
                      Added on {formatDate(favorite.created_at)}
                    </p>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <button
                      onClick={() => navigate(`/property/${favorite.property_id}`)}
                      className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <EyeIcon className="w-4 h-4 mr-2" />
                      View Details
                    </button>
                    
                    <button
                      onClick={() => handleRemoveFavorite(favorite.id)}
                      className="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Favorites;
