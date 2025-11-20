import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  CalendarDaysIcon, 
  UserGroupIcon,
  StarIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon,
  PhoneIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';
import PublicHeader from '@/components/common/PublicHeader';

interface SearchForm {
  city: string;
  check_in: string;
  check_out: string;
  guests: number;
}

interface PopularDestination {
  city: string;
  country: string;
  property_count: number;
}

const LandingPage = () => {
  const navigate = useNavigate();
  const [searchForm, setSearchForm] = useState<SearchForm>({
    city: '',
    check_in: '',
    check_out: '',
    guests: 2
  });
  const [popularDestinations, setPopularDestinations] = useState<PopularDestination[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    // Set default dates
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    setSearchForm(prev => ({
      ...prev,
      check_in: today.toISOString().split('T')[0],
      check_out: tomorrow.toISOString().split('T')[0]
    }));

    // Load popular destinations
    loadPopularDestinations();
  }, []);

  const loadPopularDestinations = async () => {
    try {
      const response = await apiClient.getPublicDestinations();
      setPopularDestinations(response.destinations?.slice(0, 8) || []);
    } catch (error) {
      console.error('Failed to load destinations:', error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!searchForm.check_in || !searchForm.check_out) {
      toast.error('Please select check-in and check-out dates');
      return;
    }

    setIsSearching(true);
    
    try {
      // Navigate to rooms page for this hotel
      const searchParams = new URLSearchParams({
        check_in: searchForm.check_in,
        check_out: searchForm.check_out,
        guests: searchForm.guests.toString()
      });
      
      navigate(`/rooms?${searchParams.toString()}`);
    } catch (error) {
      toast.error('Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleDestinationClick = (city: string) => {
    setSearchForm(prev => ({ ...prev, city }));
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <PublicHeader />

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Grand Palace Hotel
            </h1>
            <p className="text-xl md:text-2xl mb-12 text-primary-100 max-w-3xl mx-auto">
              Experience luxury and comfort in the heart of the city. Find your perfect room and book with confidence.
            </p>

            {/* Browse Rooms CTA */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8 max-w-2xl mx-auto text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Discover Our Beautiful Rooms
              </h3>
              <p className="text-gray-600 mb-6">
                Browse through our collection of luxury rooms and suites. Select your perfect room and choose your dates.
              </p>
                <button
                onClick={() => navigate('/rooms')}
                className="bg-primary-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-primary-700 transition-colors text-lg flex items-center justify-center mx-auto"
              >
                <MagnifyingGlassIcon className="w-6 h-6 mr-2" />
                Browse All Rooms
                </button>
            </div>
          </div>
        </div>
      </section>

      {/* Hotel Features */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Hotel Amenities</h2>
            <p className="text-lg text-gray-600">Everything you need for a perfect stay</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🏊‍♂️</div>
              <h3 className="font-semibold text-gray-900">Swimming Pool</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🏋️‍♂️</div>
              <h3 className="font-semibold text-gray-900">Fitness Center</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🍽️</div>
              <h3 className="font-semibold text-gray-900">Restaurant</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🚗</div>
              <h3 className="font-semibold text-gray-900">Free Parking</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">📶</div>
              <h3 className="font-semibold text-gray-900">Free WiFi</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🧖‍♀️</div>
              <h3 className="font-semibold text-gray-900">Spa & Wellness</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🏢</div>
              <h3 className="font-semibold text-gray-900">Business Center</h3>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-primary-600 text-3xl mb-3">🎯</div>
              <h3 className="font-semibold text-gray-900">Concierge</h3>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose Us</h2>
            <p className="text-lg text-gray-600">Experience the best in hotel booking</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <StarIcon className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Luxury Rooms</h3>
              <p className="text-gray-600">
                Choose from our selection of elegantly designed rooms and suites with premium amenities.
              </p>
            </div>
            
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <CurrencyDollarIcon className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Great Value</h3>
              <p className="text-gray-600">
                Enjoy competitive rates with exceptional service and amenities included in your stay.
              </p>
            </div>
            
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <ShieldCheckIcon className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Secure Booking</h3>
              <p className="text-gray-600">
                Your booking is protected with our secure payment system and instant confirmation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Your Journey?</h2>
          <p className="text-xl mb-8 text-primary-100">
            Join millions of travelers who trust us with their accommodation needs
          </p>
          <button
            onClick={() => navigate('/rooms')}
            className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            View Our Rooms
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">HotelBooking</h3>
              <p className="text-gray-400">
                Your trusted partner for finding the perfect accommodation worldwide.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About Us</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Press</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">Safety</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Contact</h4>
              <div className="space-y-2 text-gray-400">
                <div className="flex items-center">
                  <PhoneIcon className="w-4 h-4 mr-2" />
                  <span>+1 (555) 123-4567</span>
                </div>
                <div className="flex items-center">
                  <MapPinIcon className="w-4 h-4 mr-2" />
                  <span>24/7 Support</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 HotelBooking. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;