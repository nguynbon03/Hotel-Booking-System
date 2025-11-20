import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// ============================================================
// 🔧 API Configuration
// ============================================================

const getApiBaseUrl = () => {
  // Try to get from runtime environment (Docker)
  if (typeof window !== 'undefined' && (window as any).ENV) {
    console.log('🌐 Using runtime ENV API URL:', (window as any).ENV.VITE_API_URL);
    return (window as any).ENV.VITE_API_URL;
  }
  // Fallback to build-time environment
  const buildTimeUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
  console.log('🌐 Using build-time API URL:', buildTimeUrl);
  return buildTimeUrl;
};

const API_BASE_URL = getApiBaseUrl();

class ApiClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors (token expired)
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            this.handleAuthError();
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        this.handleApiError(error);
        return Promise.reject(error);
      }
    );
  }

  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  private clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  private async refreshAccessToken(): Promise<string> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    this.refreshPromise = this.client
      .post('/auth/refresh', { refresh_token: refreshToken })
      .then((response) => {
        const { access_token, refresh_token } = response.data;
        this.setTokens(access_token, refresh_token);
        this.refreshPromise = null;
        return access_token;
      })
      .catch((error) => {
        this.refreshPromise = null;
        throw error;
      });

    return this.refreshPromise;
  }

  private handleAuthError() {
    this.clearTokens();
    window.location.href = '/login';
    toast.error('Session expired. Please login again.');
  }

  private handleApiError(error: any) {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    
    // Don't show toast for 401 errors (handled by auth interceptor)
    if (error.response?.status !== 401) {
      toast.error(message);
    }
  }

  // ============================================================
  // 🔐 Authentication Methods
  // ============================================================

  async login(credentials: { email: string; password: string }) {
    console.log('🔐 Login attempt:', { email: credentials.email, baseURL: API_BASE_URL });
    
    // Use URLSearchParams instead of FormData for proper form encoding
    const params = new URLSearchParams();
    params.append('username', credentials.email);
    params.append('password', credentials.password);

    try {
      const response = await this.client.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('✅ Login success:', response.data);

      if (response.data.access_token) {
        this.setTokens(response.data.access_token, response.data.refresh_token);
      }

      return response.data;
    } catch (error: any) {
      console.error('❌ Login error:', error.response?.data || error.message);
      throw error;
    }
  }

  async confirmLoginOtp(data: { email: string; code: string }) {
    const response = await this.client.post('/auth/confirm-login-otp', data);
    
    if (response.data.access_token) {
      this.setTokens(response.data.access_token, response.data.refresh_token);
    }

    return response.data;
  }

  async logout() {
    const refreshToken = this.getRefreshToken();
    if (refreshToken) {
      try {
        await this.client.post('/auth/logout', { refresh_token: refreshToken });
      } catch (error) {
        // Ignore logout errors
      }
    }
    this.clearTokens();
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/me');
    return response.data;
  }

  // ============================================================
  // 🏢 Organization Methods
  // ============================================================

  async getOrganizations() {
    const response = await this.client.get('/organizations');
    return response.data;
  }

  async getOrganization(id: string) {
    const response = await this.client.get(`/organizations/${id}`);
    return response.data;
  }

  async createOrganization(data: any) {
    const response = await this.client.post('/organizations', data);
    return response.data;
  }

  async updateOrganization(id: string, data: any) {
    const response = await this.client.patch(`/organizations/${id}`, data);
    return response.data;
  }

  async switchOrganization(id: string) {
    const response = await this.client.post(`/organizations/${id}/switch`);
    return response.data;
  }

  async getOrganizationMembers(id: string) {
    const response = await this.client.get(`/organizations/${id}/members`);
    return response.data;
  }

  async updateMemberPermissions(orgId: string, memberId: string, data: any) {
    const response = await this.client.patch(`/organizations/${orgId}/members/${memberId}`, data);
    return response.data;
  }

  async removeMember(orgId: string, memberId: string) {
    const response = await this.client.delete(`/organizations/${orgId}/members/${memberId}`);
    return response.data;
  }

  async inviteUser(orgId: string, data: { email: string; role: string }) {
    const response = await this.client.post(`/organizations/${orgId}/invitations`, data);
    return response.data;
  }

  async getOrganizationStats(id: string) {
    const response = await this.client.get(`/organizations/${id}/stats`);
    return response.data;
  }

  // ============================================================
  // 👥 User Management Methods
  // ============================================================

  async getUsers(params?: any) {
    const response = await this.client.get('/admin/users', { params });
    return response.data;
  }

  async getUser(id: string) {
    const response = await this.client.get(`/admin/users/${id}`);
    return response.data;
  }

  async createUser(data: any) {
    const response = await this.client.post('/admin/users', data);
    return response.data;
  }

  async updateUser(id: string, data: any) {
    const response = await this.client.patch(`/admin/users/${id}`, data);
    return response.data;
  }

  async deleteUser(id: string) {
    const response = await this.client.delete(`/admin/users/${id}`);
    return response.data;
  }

  // ============================================================
  // 🏨 Property Methods
  // ============================================================

  async getProperties(params?: any) {
    const response = await this.client.get('/properties', { params });
    return response.data;
  }

  async getProperty(id: string) {
    const response = await this.client.get(`/properties/${id}`);
    return response.data;
  }

  async createProperty(data: any) {
    const response = await this.client.post('/properties', data);
    return response.data;
  }

  async updateProperty(id: string, data: any) {
    const response = await this.client.patch(`/properties/${id}`, data);
    return response.data;
  }

  async deleteProperty(id: string) {
    const response = await this.client.delete(`/properties/${id}`);
    return response.data;
  }

  // ============================================================
  // 🛏️ Room Methods
  // ============================================================

  async getRooms(params?: any) {
    const response = await this.client.get('/rooms', { params });
    return response.data;
  }

  async getRoom(id: string) {
    const response = await this.client.get(`/rooms/${id}`);
    return response.data;
  }

  async createRoom(data: any) {
    const response = await this.client.post('/rooms', data);
    return response.data;
  }

  async updateRoom(id: string, data: any) {
    const response = await this.client.patch(`/rooms/${id}`, data);
    return response.data;
  }

  async deleteRoom(id: string) {
    const response = await this.client.delete(`/rooms/${id}`);
    return response.data;
  }

  async getPublicRooms(params?: {
    limit?: number;
    offset?: number;
    property_id?: string;
    room_type?: string;
    min_price?: number;
    max_price?: number;
    min_capacity?: number;
    max_capacity?: number;
    amenities?: string;
  }) {
    // Create a public client for room listings (no auth required)
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get('/rooms/public', { params });
    return response.data;
  }

  async getPublicRoom(roomId: string) {
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    const response = await publicClient.get(`/rooms/public/${roomId}`);
    return response.data;
  }

  async checkRoomAvailability(params: {
    room_id: string;
    check_in: string;
    check_out: string;
    guests: number;
  }) {
    // Create a public client for availability check (no auth required)
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get(`/rooms/${params.room_id}/availability`, { 
      params: {
        check_in: params.check_in,
        check_out: params.check_out,
        guests: params.guests
      }
    });
    return response.data;
  }


  // ============================================================
  // 📅 Booking Methods
  // ============================================================

  async getBookings(params?: any) {
    const response = await this.client.get('/bookings', { params });
    return response.data;
  }

  async createGuestBooking(bookingData: {
    room_id: string;
    check_in: string;
    check_out: string;
    guests: number;
    guest_name: string;
    guest_email: string;
    guest_phone: string;
    special_requests?: string;
  }) {
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    const response = await publicClient.post('/bookings/public', bookingData);
    return response.data;
  }

  async getBooking(id: string) {
    const response = await this.client.get(`/bookings/${id}`);
    return response.data;
  }

  async updateBooking(id: string, data: any) {
    const response = await this.client.patch(`/bookings/${id}`, data);
    return response.data;
  }

  async createBooking(data: any) {
    const response = await this.client.post('/bookings', data);
    return response.data;
  }

  async cancelBooking(id: string) {
    const response = await this.client.delete(`/bookings/${id}`);
    return response.data;
  }

  // Staff booking management
  async getAllBookings(params?: any) {
    const response = await this.client.get('/staff/bookings', { params });
    return response.data;
  }

  async modifyBooking(id: string, data: any) {
    const response = await this.client.patch(`/staff/bookings/${id}`, data);
    return response.data;
  }

  // ============================================================
  // 🔥 FAVORITES API
  // ============================================================
  async getFavorites(params?: any) {
    const response = await this.client.get('/customers/favorites', { params });
    return response.data;
  }

  async addFavorite(data: { property_id: string; category?: string }) {
    const response = await this.client.post('/customers/favorites', data);
    return response.data;
  }

  async removeFavorite(favoriteId: string) {
    const response = await this.client.delete(`/customers/favorites/${favoriteId}`);
    return response.data;
  }

  async removeFavoriteByProperty(propertyId: string) {
    const response = await this.client.delete(`/customers/favorites/property/${propertyId}`);
    return response.data;
  }

  // ============================================================
  // 💳 PAYMENT API
  // ============================================================
  async createPayment(data: { booking_id: string; method: string; amount?: number; card_last_four?: string }) {
    const response = await this.client.post('/payments', data);
    return response.data;
  }

  async getPayments(params?: any) {
    const response = await this.client.get('/payments', { params });
    return response.data;
  }

  // ============================================================
  // 👤 PROFILE API
  // ============================================================
  async updateProfile(data: { full_name?: string; phone?: string; address?: string; date_of_birth?: string }) {
    const response = await this.client.patch('/users/me', data);
    return response.data;
  }

  // ============================================================
  // 📊 Analytics Methods
  // ============================================================

  async getRevenueAnalytics(params: { start_date: string; end_date: string; property_id?: string }) {
    const response = await this.client.get('/analytics/revenue', { params });
    return response.data;
  }

  async getOccupancyAnalytics(params: { start_date: string; end_date: string; property_id?: string }) {
    const response = await this.client.get('/analytics/occupancy', { params });
    return response.data;
  }

  async getBookingAnalytics(params: { start_date: string; end_date: string }) {
    const response = await this.client.get('/analytics/bookings', { params });
    return response.data;
  }

  async getCustomerAnalytics(params: { start_date: string; end_date: string }) {
    const response = await this.client.get('/analytics/customers', { params });
    return response.data;
  }

  async getAnalyticsSummary(params: { start_date: string; end_date: string }) {
    const response = await this.client.get('/analytics/summary', { params });
    return response.data;
  }

  async getTopPerformers(params: { start_date: string; end_date: string }) {
    const response = await this.client.get('/analytics/top-performers', { params });
    return response.data;
  }

  // ============================================================
  // 🔧 Admin Analytics
  // ============================================================

  async getAdminAnalytics() {
    const response = await this.client.get('/admin/analytics/overview');
    return response.data;
  }

  async getAdminRevenue(params: { from_date: string; to_date: string }) {
    const response = await this.client.get('/admin/analytics/revenue', { params });
    return response.data;
  }

  // ============================================================
  // 🔍 Search & Public Methods
  // ============================================================

  async searchProperties(params: {
    city?: string;
    check_in?: string;
    check_out?: string;
    guests?: number;
    property_type?: string;
    min_price?: number;
    max_price?: number;
    limit?: number;
    offset?: number;
  }) {
    const response = await this.client.get('/search/properties', { params });
    return response.data;
  }

  async getPropertyDetails(id: string, params?: {
    check_in?: string;
    check_out?: string;
    guests?: number;
  }) {
    const response = await this.client.get(`/search/properties/${id}`, { params });
    return response.data;
  }

  async checkAvailability(roomTypeId: string, params: {
    check_in: string;
    check_out: string;
  }) {
    const response = await this.client.get(`/search/availability/${roomTypeId}`, { params });
    return response.data;
  }

  async getPopularCities(limit = 20) {
    const response = await this.client.get('/search/cities', { params: { limit } });
    return response.data;
  }

  async getPropertyTypes() {
    const response = await this.client.get('/search/property-types');
    return response.data;
  }

  async getPriceRange(params?: { city?: string; property_type?: string }) {
    const response = await this.client.get('/search/price-range', { params });
    return response.data;
  }

  // ============================================================
  // 💰 Subscription Methods
  // ============================================================

  async getSubscriptionPlans() {
    const response = await this.client.get('/subscriptions/plans');
    return response.data;
  }

  async getCurrentSubscription() {
    const response = await this.client.get('/subscriptions/current');
    return response.data;
  }

  async createSubscription(data: {
    plan_name: string;
    billing_cycle?: string;
    trial_days?: number;
  }) {
    const response = await this.client.post('/subscriptions', data);
    return response.data;
  }

  async getUsageStatistics() {
    const response = await this.client.get('/subscriptions/usage');
    return response.data;
  }

  async upgradeSubscription(data: {
    new_plan_name: string;
    billing_cycle?: string;
  }) {
    const response = await this.client.patch('/subscriptions/upgrade', data);
    return response.data;
  }

  async cancelSubscription(data: {
    cancel_at_period_end?: boolean;
    reason?: string;
  }) {
    const response = await this.client.post('/subscriptions/cancel', data);
    return response.data;
  }

  async getInvoices(params?: { limit?: number; offset?: number }) {
    const response = await this.client.get('/subscriptions/invoices', { params });
    return response.data;
  }

  async getInvoiceDetails(invoiceId: string) {
    const response = await this.client.get(`/subscriptions/invoices/${invoiceId}`);
    return response.data;
  }

  async getSubscriptionAnalytics() {
    const response = await this.client.get('/subscriptions/analytics');
    return response.data;
  }

  async checkOperationLimits(operation: string) {
    const response = await this.client.post('/subscriptions/check-limits', { operation });
    return response.data;
  }

  // ============================================================
  // 🌐 Public API Methods (No Auth Required)
  // ============================================================

  async getPublicDestinations() {
    // Create a separate client without auth for public endpoints
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get('/public/cities');
    return response.data;
  }

  async searchPublicProperties(params: {
    city?: string;
    check_in?: string;
    check_out?: string;
    guests?: number;
    property_type?: string;
    min_price?: number;
    max_price?: number;
    limit?: number;
    offset?: number;
  }) {
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get('/search/properties', { params });
    return response.data;
  }

  async getPublicPropertyDetails(id: string, params?: {
    check_in?: string;
    check_out?: string;
    guests?: number;
  }) {
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get(`/search/properties/${id}`, { params });
    return response.data;
  }

  // ============================================================
  // 🤖 AI Recommendation Methods
  // ============================================================

  async getRoomRecommendations(params?: {
    check_in?: string;
    check_out?: string;
    capacity?: number;
    view?: string;
    price_max?: number;
    city?: string;
    amenities?: string;
    limit?: number;
  }) {
    // Create a public client for room recommendations (no auth required)
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get('/ai/recommendations/rooms', { params });
    return response.data;
  }

  async getPropertyRecommendations(params?: {
    check_in?: string;
    check_out?: string;
    guests?: number;
    city?: string;
    property_type?: string;
    min_price?: number;
    max_price?: number;
    limit?: number;
  }) {
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    
    const response = await publicClient.get('/ai/recommendations/properties', { params });
    return response.data;
  }

  // ============================================================
  // 🔧 Utility Methods
  // ============================================================

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  async request<T>(config: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client(config);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
